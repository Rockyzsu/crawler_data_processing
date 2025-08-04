import re
import string
import hashlib
import spacy
import fasttext
import dask.bag as db
from dask.diagnostics import ProgressBar
from typing import List, Tuple, Dict
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import numpy as np
from langdetect import detect, LangDetectException

# ----------------------
# Resource Initialization
# ----------------------
# Load NLP models (download first if needed)
# spacy download en_core_web_lg
# spacy download zh_core_web_lg
try:
    nlp_en = spacy.load("en_core_web_lg")  # For English NER and parsing
    nlp_zh = spacy.load("zh_core_web_lg")  # For Chinese NER
except:
    print("Warning: SpaCy models not found. Sensitive info detection may be limited.")
    nlp_en = None
    nlp_zh = None

# FastText for language detection (more accurate than regex)
# Download model: https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
try:
    ft_model = fasttext.load_model('lid.176.bin')
except:
    print("Warning: FastText model not found. Using fallback language detection.")
    ft_model = None

# Load quality assessment model (assesses text coherence/information density)
quality_model_name = "microsoft/xtremedistil-l6-h384-uncased"
quality_tokenizer = AutoTokenizer.from_pretrained(quality_model_name)
quality_model = AutoModelForSequenceClassification.from_pretrained(
    quality_model_name, 
    num_labels=2  # 0: low quality, 1: high quality (fine-tuned on custom data)
)
quality_pipeline = pipeline(
    "text-classification",
    model=quality_model,
    tokenizer=quality_tokenizer,
    device=0 if torch.cuda.is_available() else -1
)

# ----------------------
# Advanced Cleaner Class
# ----------------------
class AdvancedLLMCleaner:
    def __init__(self):
        # Sensitive pattern database (extended)
        self.sensitive_patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b(?:\+?86)?1[3-9]\d{9}\b',  # Chinese phone
            "id_card": r'\b\d{17}[\dXx]\b',  # Chinese ID
            "credit_card": r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
        }
        # Harmful keywords (example categories)
        self.harmful_keywords = {"violence", "discrimination", "hate", "terrorism"}

    def detect_language_advanced(self, text: str) -> Tuple[str, float]:
        """
        Advanced language detection with confidence score
        Returns (language code, confidence)
        """
        if not text.strip():
            return ("unknown", 0.0)
        
        try:
            if ft_model:
                predictions = ft_model.predict(text, k=1)
                lang = predictions[0][0].replace("__label__", "")
                confidence = predictions[1][0]
                return (lang, confidence)
            else:
                # Fallback to langdetect
                lang = detect(text)
                return (lang, 0.8)  # Assume lower confidence
        except (LangDetectException, IndexError):
            return ("unknown", 0.0)

    def split_long_text(self, text: str, lang: str = "en", max_tokens: int = 512) -> List[str]:
        """
        Split long text into semantic chunks (avoid splitting sentences)
        """
        nlp = nlp_en if lang == "en" else nlp_zh if lang == "zh" else None
        if not nlp or not text.strip():
            return [text]
        
        doc = nlp(text)
        sentences = [sent.text for sent in doc.sents]
        chunks = []
        current_chunk = []
        current_length = 0

        for sent in sentences:
            sent_tokens = len(nlp(sent))
            if current_length + sent_tokens <= max_tokens:
                current_chunk.append(sent)
                current_length += sent_tokens
            else:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = [sent]
                current_length = sent_tokens
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks

    def filter_semantic_quality(self, texts: List[str], threshold: float = 0.7) -> List[str]:
        """
        Filter texts based on semantic quality (using pre-trained classifier)
        """
        high_quality = []
        # Batch processing to improve efficiency
        for i in range(0, len(texts), 32):
            batch = texts[i:i+32]
            results = quality_pipeline(batch)
            for text, res in zip(batch, results):
                if res["label"] == "LABEL_1" and res["score"] >= threshold:
                    high_quality.append(text)
        return high_quality

    def desensitize_text(self, text: str, lang: str = "en") -> str:
        """
        Deep desensitization: replace sensitive info with placeholders
        """
        # 1. Pattern-based replacement
        for name, pattern in self.sensitive_patterns.items():
            text = re.sub(pattern, f"[{name}_REDACTED]", text)
        
        # 2. NER-based replacement (names, addresses, organizations)
        nlp = nlp_en if lang == "en" else nlp_zh if lang == "zh" else None
        if nlp:
            doc = nlp(text)
            for ent in doc.ents:
                # Redact personal entities (customize based on your needs)
                if ent.label_ in ["PERSON", "GPE", "ORG", "DATE"]:  # GPE: countries/cities
                    text = text.replace(ent.text, f"[{ent.label_}_REDACTED]")
        
        # 3. Harmful content filtering
        for keyword in self.harmful_keywords:
            if keyword in text.lower():
                return ""  # Remove entirely if harmful content is found
        return text

    def remove_cross_lang_noise(self, text: str, primary_lang: str = None) -> str:
        """
        Remove mixed-language noise (e.g., English words in Chinese text with low info value)
        """
        if not primary_lang:
            primary_lang, _ = self.detect_language_advanced(text)
            if primary_lang == "unknown":
                return text
        
        # For Chinese text: remove English words with low semantic value
        if primary_lang == "zh":
            # Keep meaningful English terms (e.g., "AI", "GDP") but remove noise
            english_words = re.findall(r'[A-Za-z]+', text)
            for word in english_words:
                if len(word) < 3 and word.lower() not in {"ai", "it", "gdp"}:
                    text = text.replace(word, "")
        return text

    def distributed_clean(self, file_paths: List[str], batch_size: int = 1000) -> None:
        """
        Distributed cleaning for large-scale data using Dask
        """
        # Create Dask bag from file paths
        bag = db.from_sequence(file_paths, npartitions=8)
        
        # Define processing pipeline
        def process_file(file_path):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                texts = [line.strip() for line in f if line.strip()]
            
            cleaned = []
            for text in texts:
                # Basic cleaning
                text = re.sub(r'\s+', ' ', text).strip()
                if len(text) < 20:
                    continue
                
                # Language detection
                lang, conf = self.detect_language_advanced(text)
                if conf < 0.6:
                    continue
                
                # Desensitize
                text = self.desensitize_text(text, lang)
                if not text:
                    continue
                
                # Cross-language noise removal
                text = self.remove_cross_lang_noise(text, lang)
                
                # Split long text
                chunks = self.split_long_text(text, lang)
                cleaned.extend(chunks)
            
            return cleaned
        
        # Execute in parallel
        cleaned_bag = bag.map(process_file).flatten()
        
        # Save results (example: write to output directory)
        with ProgressBar():
            cleaned_bag.to_textfiles("cleaned_data/output_*.txt")
        
        print("Distributed cleaning completed.")


# ----------------------
# Usage Example
# ----------------------
if __name__ == "__main__":
    cleaner = AdvancedLLMCleaner()
    
    # Example 1: Process a single long text
    long_text = """
    Dr. John Smith (john.smith@example.com) delivered a speech on AI in Beijing. 
    He mentioned that 80% of data scientists use Python. His phone number is 13800138000.
    这是一段包含英文单词的中文文本，其中夹杂着一些 short 英文单词。
    """
    lang, _ = cleaner.detect_language_advanced(long_text)
    desensitized = cleaner.desensitize_text(long_text, lang)
    filtered = cleaner.remove_cross_lang_noise(desensitized, lang)
    chunks = cleaner.split_long_text(filtered, lang)
    print("Processed chunks:")
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i+1}: {chunk}")
    
    # Example 2: Semantic quality filtering
    sample_texts = [
        "Good morning! How are you?",  # High quality
        "Asdflkj qwerpoi 12345...",    # Low quality
        "The quick brown fox jumps over the lazy dog."  # High quality
    ]
    high_quality = cleaner.filter_semantic_quality(sample_texts)
    print("\nHigh quality texts after filtering:", high_quality)
    
    # Example 3: Distributed cleaning (uncomment to test with your files)
    # file_paths = [f"data/raw_{i}.txt" for i in range(10)]  # Replace with your file paths
    # cleaner.distributed_clean(file_paths)
    
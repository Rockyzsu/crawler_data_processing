import re
import string
import hashlib
from typing import List, Tuple
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download NLTK resources (required for first run)
nltk.download('stopwords')
nltk.download('punkt')

class LLMDataCleaner:
    def __init__(self):
        """Initialize data cleaning utility and load resources like stop words"""
        self.stop_words = set(stopwords.words('english'))  # English stop words
        # Extended custom stop words (can be extended as needed)
        self.custom_stop_words = {"http", "https", "www", "com", "html", "jpg", "png"}
        self.stop_words.update(self.custom_stop_words)
        
    def remove_duplicates(self, texts: List[str]) -> Tuple[List[str], int]:
        """
        Remove duplicate texts
        :param texts: List of texts
        :return: Tuple of (deduplicated text list, number of duplicates removed)
        """
        # Use hash values for fast duplicate detection
        seen = set()
        unique_texts = []
        duplicates = 0
        
        for text in texts:
            # Normalize text before hashing (ignore case and leading/trailing spaces)
            text_normalized = text.strip().lower()
            text_hash = hashlib.md5(text_normalized.encode()).hexdigest()
            
            if text_hash not in seen:
                seen.add(text_hash)
                unique_texts.append(text)
            else:
                duplicates += 1
                
        return unique_texts, duplicates
    
    def filter_short_texts(self, texts: List[str], min_length: int = 10) -> Tuple[List[str], int]:
        """
        Filter out excessively short texts (usually containing noise)
        :param texts: List of texts
        :param min_length: Minimum character length threshold
        :return: Tuple of (filtered text list, number of short texts removed)
        """
        filtered = []
        removed = 0
        
        for text in texts:
            if len(text.strip()) >= min_length:
                filtered.append(text)
            else:
                removed += 1
                
        return filtered, removed
    
    def clean_special_characters(self, text: str) -> str:
        """
        Clean special characters, garbled code, and extra spaces
        :param text: Original text
        :return: Cleaned text
        """
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove HTML tags
        text = re.sub(r'<.*?>', '', text)
        
        # Remove special characters and garbled code (retain basic punctuation and alphanumerics)
        text = re.sub(r'[^\w\s.,!?\'\"-]', '', text)
        
        # Merge multiple spaces into one
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def remove_stopwords(self, text: str, language: str = 'english') -> str:
        """
        Remove stop words (optional step, depends on model requirements)
        :param text: Original text
        :param language: Language (currently supports English)
        :return: Text with stop words removed
        """
        if language != 'english':
            return text  # Can be extended to support other languages
        
        words = word_tokenize(text)
        filtered_words = [word for word in words if word.lower() not in self.stop_words]
        return ' '.join(filtered_words)
    
    def normalize_case(self, text: str, case: str = 'lower') -> str:
        """
        Normalize text case (usually convert to lowercase to reduce vocabulary size)
        :param text: Original text
        :param case: Target case ('lower' or 'upper')
        :return: Case-normalized text
        """
        if case == 'lower':
            return text.lower()
        elif case == 'upper':
            return text.upper()
        return text
    
    def filter_low_quality_texts(self, texts: List[str], quality_threshold: float = 0.3) -> Tuple[List[str], int]:
        """
        Filter low-quality texts (based on proportion of non-punctuation characters)
        :param texts: List of texts
        :param quality_threshold: Threshold for proportion of non-punctuation characters
        :return: Tuple of (filtered text list, number of low-quality texts removed)
        """
        filtered = []
        removed = 0
        
        for text in texts:
            if not text:
                removed += 1
                continue
                
            # Calculate ratio of non-punctuation characters
            total_chars = len(text)
            punctuation_chars = sum(1 for c in text if c in string.punctuation)
            non_punct_ratio = (total_chars - punctuation_chars) / total_chars
            
            if non_punct_ratio >= quality_threshold:
                filtered.append(text)
            else:
                removed += 1
                
        return filtered, removed
    
    def detect_language(self, text: str) -> str:
        """
        Simple language detection (based on character set)
        :param text: Input text
        :return: Language code ('en'/'zh'/'other')
        """
        # Detect Chinese characters
        if re.search(r'[\u4e00-\u9fff]', text):
            return 'zh'
        # Detect English characters
        elif re.search(r'[a-zA-Z]', text):
            return 'en'
        else:
            return 'other'
    
    def process_batch(self, texts: List[str], min_length: int = 10, quality_threshold: float = 0.3) -> Tuple[List[str], dict]:
        """
        Complete processing pipeline for batch text cleaning
        :param texts: Original list of texts
        :param min_length: Minimum length threshold
        :param quality_threshold: Quality threshold for filtering
        :return: Tuple of (cleaned text list, processing statistics)
        """
        stats = {
            'original_count': len(texts),
            'duplicates_removed': 0,
            'short_texts_removed': 0,
            'low_quality_removed': 0,
            'other_removed': 0,
            'final_count': 0
        }
        
        # 1. Remove duplicate texts
        unique_texts, duplicates = self.remove_duplicates(texts)
        stats['duplicates_removed'] = duplicates
        
        # 2. Filter out short texts
        filtered_length, short_removed = self.filter_short_texts(unique_texts, min_length)
        stats['short_texts_removed'] = short_removed
        
        # 3. Clean special characters and normalize
        cleaned = []
        for text in filtered_length:
            # Clean special characters
            text_clean = self.clean_special_characters(text)
            # Normalize case (for English)
            lang = self.detect_language(text_clean)
            if lang == 'en':
                text_clean = self.normalize_case(text_clean, 'lower')
            cleaned.append(text_clean)
        
        # 4. Filter low quality texts
        high_quality, low_quality_removed = self.filter_low_quality_texts(cleaned, quality_threshold)
        stats['low_quality_removed'] = low_quality_removed
        
        # 5. Final statistics
        stats['final_count'] = len(high_quality)
        stats['other_removed'] = stats['original_count'] - stats['final_count'] - sum([
            stats['duplicates_removed'],
            stats['short_texts_removed'],
            stats['low_quality_removed']
        ])
        
        return high_quality, stats


# Usage example
if __name__ == "__main__":
    # Sample data (simulating raw text read from files)
    raw_texts = [
        "Hello world! This is a sample text for LLM training.   ",
        "Hello world! This is a sample text for LLM training.   ",  # Duplicate text
        "Bad text!!!???",  # Low quality text (too many punctuation)
        "Short.",  # Excessively short text
        "https://example.com - Check this website!",  # Contains URL
        "<p>HTML tagged text</p>",  # Contains HTML tags
        "中文文本示例，测试多语言处理。",  # Chinese text example
        "Another example with   multiple   spaces and special chars: @#$%"
    ]
    
    # Initialize cleaner
    cleaner = LLMDataCleaner()
    
    # Process text batch
    cleaned_texts, stats = cleaner.process_batch(
        raw_texts,
        min_length=8,
        quality_threshold=0.5
    )
    
    # Output results
    print("Cleaning statistics:")
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\nCleaned texts:")
    for i, text in enumerate(cleaned_texts, 1):
        print(f"{i}. {text}")
    
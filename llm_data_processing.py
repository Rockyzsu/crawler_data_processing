import re
import string
import pandas as pd
import numpy as np
from typing import List, Tuple
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
import hashlib

# 下载NLTK资源（首次次运行需要）
nltk.download('stopwords')
nltk.download('punkt')

class LLMDataCleaner:
    def __init__(self):
        """初始化数据清洗工具，加载停用词等资源"""
        self.stop_words = set(stopwords.words('english'))  # 英文停用词
        # 扩展停用词表（可根据需求添加中文停用词）
        self.custom_stop_words = {"http", "https", "www", "com", "html", "jpg", "png"}
        self.stop_words.update(self.custom_stop_words)
        
    def remove_duplicates(self, texts: List[str]) -> Tuple[List[str], int]:
        """
        去除重复文本
        :param texts: 文本列表
        :return: 去重后的文本列表和去除的重复数量
        """
        # 使用哈希值快速检测重复
        seen = set()
        unique_texts = []
        duplicates = 0
        
        for text in texts:
            # 对文本进行哈希处理（忽略大小写和前后空格）
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
        过滤过短文本（通常包含噪声）
        :param texts: 文本列表
        :param min_length: 最小字符长度
        :return: 过滤后的文本列表和去除的短文本数量
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
        清理特殊字符、乱码和多余空格
        :param text: 原始文本
        :return: 清理后的文本
        """
        # 去除URL
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # 去除HTML标签
        text = re.sub(r'<.*?>', '', text)
        
        # 去除特殊字符和乱码（保留基本标点和字母数字）
        text = re.sub(r'[^\w\s.,!?\'\"-]', '', text)
        
        # 合并多个空格为一个
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def remove_stopwords(self, text: str, language: str = 'english') -> str:
        """
        去除停用词（可选步骤，根据模型需求决定）
        :param text: 原始文本
        :param language: 语言（目前支持英文）
        :return: 去除停用词后的文本
        """
        if language != 'english':
            return text  # 可扩展支持其他语言
        
        words = word_tokenize(text)
        filtered_words = [word for word in words if word.lower() not in self.stop_words]
        return ' '.join(filtered_words)
    
    def normalize_case(self, text: str, case: str = 'lower') -> str:
        """
        规范化大小写（通常转为小写，减少词汇表大小）
        :param text: 原始文本
        :param case: 目标大小写（'lower'或'upper'）
        :return: 规范化后的文本
        """
        if case == 'lower':
            return text.lower()
        elif case == 'upper':
            return text.upper()
        return text
    
    def filter_low_quality_texts(self, texts: List[str], quality_threshold: float = 0.3) -> Tuple[List[str], int]:
        """
        过滤低质量文本（基于非标点字符比例）
        :param texts: 文本列表
        :param quality_threshold: 非标点字符占比阈值
        :return: 过滤后的文本列表和去除的低质量文本数量
        """
        filtered = []
        removed = 0
        
        for text in texts:
            if not text:
                removed += 1
                continue
                
            # 计算非标点字符比例
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
        简单语言检测（基于字符集）
        :param text: 文本
        :return: 语言标识（'en'/'zh'/'other'）
        """
        # 检测中文字符
        if re.search(r'[\u4e00-\u9fff]', text):
            return 'zh'
        # 检测英文字符
        elif re.search(r'[a-zA-Z]', text):
            return 'en'
        else:
            return 'other'
    
    def process_batch(self, texts: List[str], min_length: int = 10, quality_threshold: float = 0.3) -> Tuple[List[str], dict]:
        """
        批量处理文本的完整流程
        :param texts: 原始文本列表
        :param min_length: 最小长度阈值
        :param quality_threshold: 质量阈值
        :return: 清洗后的文本列表和处理统计信息
        """
        stats = {
            'original_count': len(texts),
            'duplicates_removed': 0,
            'short_texts_removed': 0,
            'low_quality_removed': 0,
            'other_removed': 0,
            'final_count': 0
        }
        
        # 1. 去除重复文本
        unique_texts, duplicates = self.remove_duplicates(texts)
        stats['duplicates_removed'] = duplicates
        
        # 2. 过滤过短文本
        filtered_length, short_removed = self.filter_short_texts(unique_texts, min_length)
        stats['short_texts_removed'] = short_removed
        
        # 3. 清理特殊字符和规范化
        cleaned = []
        for text in filtered_length:
            # 清理特殊字符
            text_clean = self.clean_special_characters(text)
            # 规范化大小写（英文）
            lang = self.detect_language(text_clean)
            if lang == 'en':
                text_clean = self.normalize_case(text_clean, 'lower')
            cleaned.append(text_clean)
        
        # 4. 过滤低质量文本
        high_quality, low_quality_removed = self.filter_low_quality_texts(cleaned, quality_threshold)
        stats['low_quality_removed'] = low_quality_removed
        
        # 5. 最终统计
        stats['final_count'] = len(high_quality)
        stats['other_removed'] = stats['original_count'] - stats['final_count'] - sum([
            stats['duplicates_removed'],
            stats['short_texts_removed'],
            stats['low_quality_removed']
        ])
        
        return high_quality, stats


# 使用示例
if __name__ == "__main__":
    # 示例数据（模拟从文件读取的原始文本）
    raw_texts = [
        "Hello world! This is a sample text for LLM training.   ",
        "Hello world! This is a sample text for LLM training.   ",  # 重复文本
        "Bad text!!!???",  # 低质量文本（标点过多）
        "Short.",  # 过短文本
        "https://example.com - Check this website!",  # 包含URL
        "<p>HTML tagged text</p>",  # 包含HTML标签
        "中文文本示例，测试多语言处理。",
        "Another example with   multiple   spaces and special chars: @#$%"
    ]
    
    # 初始化清洗器
    cleaner = LLMDataCleaner()
    
    # 批量处理文本
    cleaned_texts, stats = cleaner.process_batch(
        raw_texts,
        min_length=8,
        quality_threshold=0.5
    )
    
    # 输出结果
    print("清洗统计:")
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n清洗后的文本:")
    for i, text in enumerate(cleaned_texts, 1):
        print(f"{i}. {text}")

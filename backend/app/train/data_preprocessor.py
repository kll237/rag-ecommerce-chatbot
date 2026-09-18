"""
数据预处理器
"""
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple
import pandas as pd

class DataPreprocessor:
    """数据预处理器"""

    def __init__(self, raw_data_dir: str = None):
        self.raw_data_dir = Path(raw_data_dir) if raw_data_dir else None

    def clean_text(self, text: str) -> str:
        """
        清洗文本

        Args:
            text: 原始文本

        Returns:
            清洗后的文本
        """
        # 去除HTML标签
        text = re.sub(r'<[^>]+>', '', text)

        # 去除多余空格和换行
        text = ' '.join(text.split())

        # 转小写（可选）
        # text = text.lower()

        return text.strip()

    def load_faq_data(self, faq_path: str) -> List[Dict]:
        """
        加载FAQ数据

        Args:
            faq_path: FAQ文件路径

        Returns:
            FAQ数据列表
        """
        faq_path = Path(faq_path)
        if not faq_path.exists():
            return []

        with open(faq_path, 'r', encoding='utf-8') as f:
            content = f.read()

        faqs = []
        lines = content.split('\n')
        current_qa = {}

        for line in lines:
            line = line.strip()
            if line.startswith('Q:'):
                if current_qa:
                    faqs.append(current_qa)
                current_qa = {'question': line[2:].strip(), 'answer': ''}
            elif line.startswith('A:'):
                current_qa['answer'] = line[2:].strip()

        if current_qa:
            faqs.append(current_qa)

        # 清洗数据
        for faq in faqs:
            faq['question'] = self.clean_text(faq['question'])
            faq['answer'] = self.clean_text(faq['answer'])

        return faqs

    def load_product_data(self, product_path: str) -> List[Dict]:
        """
        加载商品数据

        Args:
            product_path: 商品JSON文件路径

        Returns:
            商品数据列表
        """
        product_path = Path(product_path)
        if not product_path.exists():
            return []

        with open(product_path, 'r', encoding='utf-8') as f:
            products = json.load(f)

        # 清洗数据
        for product in products:
            if 'name' in product:
                product['name'] = self.clean_text(product['name'])
            if 'description' in product:
                product['description'] = self.clean_text(product['description'])

        return products

    def create_training_pairs(self, faqs: List[Dict]) -> List[Tuple[str, str]]:
        """
        创建训练样本对（问题，答案）

        Args:
            faqs: FAQ数据

        Returns:
            训练样本对列表
        """
        pairs = []
        for faq in faqs:
            if faq['question'] and faq['answer']:
                pairs.append((faq['question'], faq['answer']))
        return pairs

    def chunk_documents(self, documents: List[str], chunk_size: int = 256, overlap: int = 50) -> List[str]:
        """
        将文档切分为块

        Args:
            documents: 文档列表
            chunk_size: 块大小
            overlap: 重叠大小

        Returns:
            文档块列表
        """
        chunks = []
        for doc in documents:
            words = doc.split()
            for i in range(0, len(words), chunk_size - overlap):
                chunk = ' '.join(words[i:i + chunk_size])
                if len(chunk.split()) > 20:  # 过滤太短的块
                    chunks.append(chunk)
        return chunks

    def split_dataset(self, data: List, train_ratio: float = 0.8) -> Tuple[List, List]:
        """
        划分训练集和验证集

        Args:
            data: 数据列表
            train_ratio: 训练集比例

        Returns:
            (训练集, 验证集)
        """
        split_idx = int(len(data) * train_ratio)
        return data[:split_idx], data[split_idx:]

    def save_processed_data(self, data: List, output_path: str):
        """保存处理后的数据"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_processed_data(self, input_path: str) -> List:
        """加载处理后的数据"""
        input_path = Path(input_path)
        if not input_path.exists():
            return []

        with open(input_path, 'r', encoding='utf-8') as f:
            return json.load(f)

"""
文本嵌入模型
支持HuggingFace模型
"""
import numpy as np
from typing import List
import warnings
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    warnings.warn(f"sentence-transformers导入失败: {e}，将使用简化的嵌入方法")

from app.config import config

class EmbeddingModel:
    """文本嵌入模型"""

    def __init__(self, model_name: str = None):
        self.model_name = model_name or config.LOCAL_EMBEDDING_MODEL
        self.model = None
        self.embedding_dim = config.EMBEDDING_DIM

        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer(self.model_name)
                self.embedding_dim = self.model.get_sentence_embedding_dimension()
                print(f"加载嵌入模型: {self.model_name}")
            except Exception as e:
                print(f"加载嵌入模型失败: {e}")
                self.model = None

    def encode(self, texts: List[str]) -> np.ndarray:
        """
        将文本编码为嵌入向量

        Args:
            texts: 文本列表

        Returns:
            嵌入向量数组，形状为 (len(texts), embedding_dim)
        """
        if not texts:
            return np.array([])

        if self.model is not None:
            # 使用SentenceTransformers
            return self.model.encode(texts, convert_to_numpy=True)
        else:
            # 使用简化的嵌入方法（基于字符N-gram）
            return self._simple_encode(texts)

    def _simple_encode(self, texts: List[str]) -> np.ndarray:
        """
        改进的简化嵌入方法（基于字符N-gram）
        相比纯字符顺序，能够更好地捕捉语义相似度
        """
        embeddings = []
        for text in texts:
            # 转为小写
            text = text.lower()

            # 创建字符N-gram特征向量（2-gram和3-gram）
            vec = np.zeros(self.embedding_dim)

            # 2-gram 特征
            for i in range(len(text) - 1):
                ngram = text[i:i+2]
                hash_val = hash(ngram) % self.embedding_dim
                vec[hash_val] += 1.0

            # 3-gram 特征（权重更高）
            for i in range(len(text) - 2):
                ngram = text[i:i+3]
                hash_val = hash(ngram) % self.embedding_dim
                vec[hash_val] += 1.5

            # 归一化
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm

            embeddings.append(vec)

        return np.array(embeddings)

    def encode_single(self, text: str) -> np.ndarray:
        """编码单个文本"""
        return self.encode([text])[0]

    def get_embedding_dim(self) -> int:
        """获取嵌入维度"""
        return self.embedding_dim

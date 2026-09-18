"""
向量存储实现
支持FAISS和ChromaDB
"""
import json
import pickle
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

from .config import config
from .ai_models.embedder import EmbeddingModel

class VectorStore:
    """向量存储基类"""

    def __init__(self, embedding_dim: int = None):
        self.embedding_dim = embedding_dim or config.EMBEDDING_DIM
        self.embedder = EmbeddingModel()

    def add_documents(self, documents: List[str], metadatas: List[Dict] = None):
        """添加文档"""
        raise NotImplementedError

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """搜索相似文档"""
        raise NotImplementedError

    def save(self, path: str):
        """保存向量存储"""
        raise NotImplementedError

    def load(self, path: str):
        """加载向量存储"""
        raise NotImplementedError

class FAISSVectorStore(VectorStore):
    """基于FAISS的向量存储"""

    def __init__(self, embedding_dim: int = None):
        super().__init__(embedding_dim)
        self.index = None
        self.documents = []
        self.metadatas = []

        if not FAISS_AVAILABLE:
            raise ImportError("FAISS未安装，请先安装: pip install faiss-cpu")

        # 使用embedder的实际嵌入维度
        self.embedding_dim = self.embedder.get_embedding_dim()

    def _create_index(self):
        """创建FAISS索引"""
        self.index = faiss.IndexFlatL2(self.embedding_dim)

    def add_documents(self, documents: List[str], metadatas: List[Dict] = None):
        """添加文档到向量库"""
        if self.index is None:
            self._create_index()

        # 生成嵌入向量
        embeddings = self.embedder.encode(documents)

        # 添加到索引
        self.index.add(embeddings.astype('float32'))

        # 保存文档和元数据
        self.documents.extend(documents)
        if metadatas:
            self.metadatas.extend(metadatas)
        else:
            self.metadatas.extend([{} for _ in documents])

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """搜索相似文档"""
        if self.index is None:
            return []

        # 生成查询嵌入
        query_embedding = self.embedder.encode([query]).astype('float32')

        # 搜索
        distances, indices = self.index.search(query_embedding, min(top_k, len(self.documents)))

        # 返回结果
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.documents):
                results.append({
                    'content': self.documents[idx],
                    'score': float(1 / (1 + dist)),  # 转换为相似度分数
                    'metadata': self.metadatas[idx],
                    'index': int(idx)
                })

        return results

    def save(self, path: str):
        """保存向量存储"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)

        # 保存FAISS索引
        faiss.write_index(self.index, str(path / "index.faiss"))

        # 保存文档和元数据
        with open(path / "documents.pkl", 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'metadatas': self.metadatas
            }, f)

    def load(self, path: str):
        """加载向量存储"""
        path = Path(path)

        # 加载FAISS索引
        self.index = faiss.read_index(str(path / "index.faiss"))

        # 加载文档和元数据
        with open(path / "documents.pkl", 'rb') as f:
            data = pickle.load(f)
            self.documents = data['documents']
            self.metadatas = data['metadatas']

class SimpleVectorStore(VectorStore):
    """简单的内存向量存储（无需FAISS）"""

    def __init__(self, embedding_dim: int = None):
        super().__init__(embedding_dim)
        self.embeddings = []
        self.documents = []
        self.metadatas = []

        # 使用embedder的实际嵌入维度
        self.embedding_dim = self.embedder.get_embedding_dim()

    def add_documents(self, documents: List[str], metadatas: List[Dict] = None):
        """添加文档"""
        embeddings = self.embedder.encode(documents)

        for i, (doc, emb) in enumerate(zip(documents, embeddings)):
            self.embeddings.append(emb)
            self.documents.append(doc)
            if metadatas and i < len(metadatas):
                self.metadatas.append(metadatas[i])
            else:
                self.metadatas.append({})

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """搜索相似文档"""
        if not self.embeddings:
            return []

        # 生成查询嵌入
        query_embedding = self.embedder.encode([query])[0]

        # 计算相似度
        similarities = []
        for i, emb in enumerate(self.embeddings):
            # 使用余弦相似度
            sim = np.dot(query_embedding, emb) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(emb)
            )
            similarities.append((i, float(sim)))

        # 排序
        similarities.sort(key=lambda x: x[1], reverse=True)

        # 返回top_k
        results = []
        for idx, score in similarities[:top_k]:
            if score >= config.SIMILARITY_THRESHOLD:
                results.append({
                    'content': self.documents[idx],
                    'score': score,
                    'metadata': self.metadatas[idx],
                    'index': idx
                })

        return results

    def save(self, path: str):
        """保存向量存储"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)

        with open(path / "vector_store.pkl", 'wb') as f:
            pickle.dump({
                'embeddings': self.embeddings,
                'documents': self.documents,
                'metadatas': self.metadatas
            }, f)

    def load(self, path: str):
        """加载向量存储"""
        path = Path(path)

        with open(path / "vector_store.pkl", 'rb') as f:
            data = pickle.load(f)
            self.embeddings = data['embeddings']
            self.documents = data['documents']
            self.metadatas = data['metadatas']


def get_vector_store():
    """获取向量存储实例"""
    if config.VECTOR_DB_TYPE == "faiss" and FAISS_AVAILABLE:
        return FAISSVectorStore()
    else:
        return SimpleVectorStore()
"""
文档重排序器
"""
from typing import List, Dict
import numpy as np

from .embedder import EmbeddingModel

class Reranker:
    """文档重排序器"""

    def __init__(self):
        self.embedder = EmbeddingModel()

    def rerank(
        self,
        query: str,
        documents: List[Dict],
        top_k: int = 3
    ) -> List[Dict]:
        """
        重新排序检索到的文档

        Args:
            query: 用户查询
            documents: 检索到的文档列表
            top_k: 返回的文档数量

        Returns:
            重排序后的文档列表
        """
        if not documents:
            return []

        # 提取文档内容
        doc_contents = [doc['content'] for doc in documents]

        # 编码查询和文档
        query_emb = self.embedder.encode([query])[0]
        doc_embs = self.embedder.encode(doc_contents)

        # 计算相似度分数（考虑多种因素）
        reranked = []
        for i, (doc, doc_emb) in enumerate(zip(documents, doc_embs)):
            # 语义相似度
            semantic_sim = np.dot(query_emb, doc_emb) / (
                np.linalg.norm(query_emb) * np.linalg.norm(doc_emb)
            )

            # 原始检索分数
            original_score = doc.get('score', 0)

            # 文档类型权重
            metadata = doc.get('metadata', {})
            doc_type = metadata.get('type', '')
            type_weight = self._get_type_weight(doc_type)

            # 综合分数
            combined_score = (
                semantic_sim * 0.6 +
                original_score * 0.3 +
                type_weight * 0.1
            )

            reranked.append({
                **doc,
                'rerank_score': combined_score
            })

        # 按重排序分数排序
        reranked.sort(key=lambda x: x['rerank_score'], reverse=True)

        # 返回top_k
        return reranked[:top_k]

    def _get_type_weight(self, doc_type: str) -> float:
        """根据文档类型返回权重"""
        weights = {
            'faq': 0.8,
            'product': 0.9,
            'policy': 0.7
        }
        return weights.get(doc_type, 0.5)
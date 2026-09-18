"""
意图分类器
"""
from typing import Tuple
import numpy as np

from ..config import config
from .embedder import EmbeddingModel

class IntentClassifier:
    """意图分类器"""

    # 意图定义
    INTENTS = {
        'greeting': ['你好', '您好', '哈喽', 'hello', 'hi', '在吗'],
        'product_inquiry': [
            '产品', '商品', '有什么', '推荐', '介绍', '价格', '多少钱', '型号',
            # 服装类关键词
            '大衣', '衣服', '外套', '上衣', '裙子', '裤子', '鞋子', '包包', '帽子',
            '男装', '女装', '童装', '适合', '穿搭', '搭配', '款式', '尺码', '颜色',
            # 家电类关键词
            '手机', '电脑', '耳机', '音箱', '电视', '冰箱', '洗衣机', '空调',
            # 化妆品类关键词
            '化妆品', '护肤品', '口红', '粉底', '精华', '面霜', '面膜',
            # 其他
            '购买', '买', '想要', '想买', '有没有', '看看', '选', '挑'
        ],
        'order_inquiry': ['订单', '物流', '发货', '快递', '配送', '收货', '查询订单', '订单状态', '查看订单', '我的订单'],
        'complaint': ['投诉', '问题', '不好', '质量差', '服务差', '不满意'],
        'return_exchange': ['退货', '换货', '退款', '售后', '退换'],
        'payment': ['支付', '付款', '支付宝', '微信', '银行卡', '怎么付'],
        'shipping': ['配送', '包邮', '运费', '发货时间', '什么时候发货', '几天能到'],
        'faq': ['怎么', '如何', '什么', '是否'],
        'other': []
    }

    def __init__(self):
        self.embedder = EmbeddingModel()
        self.intent_embeddings = {}
        self._build_intent_embeddings()

    def _build_intent_embeddings(self):
        """构建意图关键词的嵌入向量"""
        for intent, keywords in self.INTENTS.items():
            if keywords:
                embeddings = self.embedder.encode(keywords)
                self.intent_embeddings[intent] = np.mean(embeddings, axis=0)

    def classify(self, text: str) -> Tuple[str, float]:
        """
        分类用户意图

        Args:
            text: 用户输入文本

        Returns:
            (意图, 置信度)
        """
        if not text or not text.strip():
            return 'other', 0.0

        text = text.lower().strip()

        # 优先使用关键词匹配（更可靠）
        best_intent = 'other'
        best_score = 0.0
        matched_keyword = None

        for intent, keywords in self.INTENTS.items():
            if not keywords:
                continue

            # 计算关键词匹配得分
            intent_score = 0.0
            exact_matches = 0

            # 精确匹配（完整关键词在文本中）
            for keyword in keywords:
                if keyword in text:
                    intent_score += 2.0  # 精确匹配权重更高
                    exact_matches += 1

            # 部分匹配（关键词的一部分在文本中）
            if exact_matches == 0:  # 只有在没有精确匹配时才考虑部分匹配
                for keyword in keywords:
                    words = keyword.split()
                    for word in words:
                        if len(word) >= 2 and word in text:  # 至少2个字符才匹配
                            intent_score += 0.8

            if intent_score > best_score:
                best_score = intent_score
                best_intent = intent
                matched_keyword = keywords[0]

        # 如果没有关键词匹配，使用基于嵌入的方法
        if best_score == 0.0:
            text_embedding = self.embedder.encode([text])[0]

            for intent, intent_emb in self.intent_embeddings.items():
                # 计算余弦相似度
                score = np.dot(text_embedding, intent_emb) / (
                    np.linalg.norm(text_embedding) * np.linalg.norm(intent_emb)
                )

                if score > best_score:
                    best_score = score
                    best_intent = intent

        # 归一化置信度
        if best_score > 1.0:
            best_score = min(best_score / 3.0, 1.0)  # 最多匹配3个关键词
        elif best_score < 0.5:  # 提高阈值，减少误判
            # 如果得分太低，重新检查是否有 product_inquiry 的关键词
            if any(kw in text for kw in ['推荐', '介绍', '有没有', '想要', '买']):
                best_intent = 'product_inquiry'
                best_score = 0.6
            else:
                best_intent = 'other'
                best_score = 0.0

        return best_intent, float(best_score)

    def get_all_intents(self) -> list:
        """获取所有意图列表"""
        return list(self.INTENTS.keys())

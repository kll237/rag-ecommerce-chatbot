"""
训练流水线
"""
import json
from pathlib import Path

from .data_preprocessor import DataPreprocessor
from .embedding_trainer import EmbeddingTrainer
from .intent_classifier import IntentClassifierTrainer
from .reranker_model import RerankerTrainer
from .response_generator import ResponseGeneratorTrainer
from ..config import config

class TrainingPipeline:
    """训练流水线"""

    def __init__(self):
        self.preprocessor = DataPreprocessor()

    def run_full_training(self):
        """运行完整的训练流程"""
        print("开始训练流水线...")

        # 1. 加载数据
        print("\n1. 加载数据...")
        self._load_data()

        # 2. 预处理数据
        print("\n2. 预处理数据...")
        self._preprocess_data()

        # 3. 训练嵌入模型
        print("\n3. 训练嵌入模型...")
        self._train_embedding_model()

        # 4. 训练意图分类器
        print("\n4. 训练意图分类器...")
        self._train_intent_classifier()

        # 5. 训练重排序模型
        print("\n5. 训练重排序模型...")
        self._train_reranker_model()

        # 6. 训练响应生成器
        print("\n6. 训练响应生成器...")
        self._train_response_generator()

        print("\n训练流水线完成！")

    def _load_data(self):
        """加载数据"""
        # 加载FAQ
        self.faqs = self.preprocessor.load_faq_data(
            config.KNOWLEDGE_BASE_DIR / "faq.txt"
        )

        # 加载商品数据
        self.products = self.preprocessor.load_product_data(
            config.KNOWLEDGE_BASE_DIR / "products.json"
        )

        print(f"加载了 {len(self.faqs)} 条FAQ")
        print(f"加载了 {len(self.products)} 个商品")

    def _preprocess_data(self):
        """预处理数据"""
        # 创建训练对
        self.embedding_pairs = self.preprocessor.create_training_pairs(self.faqs)

        # 划分训练集和验证集
        self.train_pairs, self.val_pairs = self.preprocessor.split_dataset(
            self.embedding_pairs,
            train_ratio=0.8
        )

        print(f"训练对: {len(self.train_pairs)}, 验证对: {len(self.val_pairs)}")

        # 准备意图分类数据
        self.train_texts = [faq['question'] for faq in self.faqs]
        self.train_labels = self._auto_label_intents(self.train_texts)

        # 准备重排序训练数据（简化版）
        self.reranker_triples = []
        for faq in self.faqs[:50]:
            self.reranker_triples.append((faq['question'], faq['answer'], 1))
            # 添加负样本
            self.reranker_triples.append((faq['question'], "不相关的内容", 0))

        # 准备响应生成训练数据
        self.response_pairs = self.embedding_pairs

    def _auto_label_intents(self, texts: list) -> list:
        """自动标注意图（简化版）"""
        labels = []
        for text in texts:
            if any(kw in text for kw in ['你好', '您好', 'hello']):
                labels.append('greeting')
            elif any(kw in text for kw in ['产品', '商品', '价格']):
                labels.append('product_inquiry')
            elif any(kw in text for kw in ['订单', '物流']):
                labels.append('order_inquiry')
            elif any(kw in text for kw in ['退货', '换货', '退款']):
                labels.append('return_exchange')
            elif any(kw in text for kw in ['支付', '付款']):
                labels.append('payment')
            else:
                labels.append('faq')
        return labels

    def _train_embedding_model(self):
        """训练嵌入模型"""
        trainer = EmbeddingTrainer(
            vocab_size=50000,
            embedding_dim=config.EMBEDDING_DIM,
            hidden_dim=512,
            learning_rate=config.LEARNING_RATE,
            batch_size=config.BATCH_SIZE,
            epochs=config.EPOCHS
        )

        trainer.train(self.train_pairs, self.val_pairs)

        # 保存模型
        model_path = config.MODELS_DIR / "custom_embedder.pt"
        trainer.save_model(str(model_path))

    def _train_intent_classifier(self):
        """训练意图分类器"""
        trainer = IntentClassifierTrainer(
            vocab_size=50000,
            embedding_dim=config.EMBEDDING_DIM,
            hidden_dim=512,
            num_intents=9,
            learning_rate=config.LEARNING_RATE,
            batch_size=config.BATCH_SIZE,
            epochs=config.EPOCHS
        )

        # 划分训练集和验证集
        split_idx = int(len(self.train_texts) * 0.8)
        train_texts = self.train_texts[:split_idx]
        train_labels = self.train_labels[:split_idx]
        val_texts = self.train_texts[split_idx:]
        val_labels = self.train_labels[split_idx:]

        trainer.train(train_texts, train_labels, val_texts, val_labels)

        # 保存模型
        model_path = config.MODELS_DIR / "intent_classifier.pt"
        trainer.save_model(str(model_path))

    def _train_reranker_model(self):
        """训练重排序模型"""
        trainer = RerankerTrainer(
            embedding_dim=config.EMBEDDING_DIM,
            hidden_dim=512,
            learning_rate=config.LEARNING_RATE,
            batch_size=config.BATCH_SIZE,
            epochs=config.EPOCHS
        )

        # 划分训练集和验证集
        split_idx = int(len(self.reranker_triples) * 0.8)
        train_triples = self.reranker_triples[:split_idx]
        val_triples = self.reranker_triples[split_idx:]

        trainer.train(train_triples, val_triples)

        # 保存模型
        model_path = config.MODELS_DIR / "reranker.pt"
        trainer.save_model(str(model_path))

    def _train_response_generator(self):
        """训练响应生成器"""
        trainer = ResponseGeneratorTrainer(
            vocab_size=50003,
            embedding_dim=256,
            hidden_dim=512,
            num_layers=2,
            learning_rate=1e-4,
            batch_size=config.BATCH_SIZE,
            epochs=5
        )

        # 划分训练集和验证集
        split_idx = int(len(self.response_pairs) * 0.8)
        train_pairs = self.response_pairs[:split_idx]
        val_pairs = self.response_pairs[split_idx:]

        trainer.train(train_pairs, val_pairs)

        # 保存模型
        model_path = config.MODELS_DIR / "response_generator.pt"
        trainer.save_model(str(model_path))

if __name__ == "__main__":
    pipeline = TrainingPipeline()
    pipeline.run_full_training()

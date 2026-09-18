"""
嵌入模型训练器
"""
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from typing import List, Tuple
import numpy as np

from ..models.custom_embedder import CustomEmbedder
from ..config import config

class EmbeddingDataset(Dataset):
    """嵌入训练数据集"""

    def __init__(self, pairs: List[Tuple[str, str]], max_length: int = 128):
        self.pairs = pairs
        self.max_length = max_length

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        query, doc = self.pairs[idx]

        # 简化版：使用字符编码
        query_ids = self._text_to_ids(query)
        doc_ids = self._text_to_ids(doc)

        return {
            'query_ids': torch.tensor(query_ids, dtype=torch.long),
            'doc_ids': torch.tensor(doc_ids, dtype=torch.long),
            'label': torch.tensor(1, dtype=torch.float)  # 正样本
        }

    def _text_to_ids(self, text: str) -> List[int]:
        """将文本转换为token IDs（简化版）"""
        ids = []
        for char in text[:self.max_length]:
            ids.append(min(ord(char), 49999))

        # 填充
        while len(ids) < self.max_length:
            ids.append(0)

        return ids

class EmbeddingTrainer:
    """嵌入模型训练器"""

    def __init__(
        self,
        vocab_size: int = 50000,
        embedding_dim: int = 768,
        hidden_dim: int = 512,
        learning_rate: float = 2e-5,
        batch_size: int = 32,
        epochs: int = 3
    ):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = CustomEmbedder(vocab_size, embedding_dim, hidden_dim).to(self.device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        self.criterion = nn.MSELoss()
        self.batch_size = batch_size
        self.epochs = epochs

    def train(self, train_pairs: List[Tuple[str, str]], val_pairs: List[Tuple[str, str]] = None):
        """
        训练模型

        Args:
            train_pairs: 训练样本对
            val_pairs: 验证样本对
        """
        # 创建数据加载器
        train_dataset = EmbeddingDataset(train_pairs)
        train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)

        if val_pairs:
            val_dataset = EmbeddingDataset(val_pairs)
            val_loader = DataLoader(val_dataset, batch_size=self.batch_size)
        else:
            val_loader = None

        # 训练循环
        for epoch in range(self.epochs):
            self.model.train()
            total_loss = 0

            for batch in train_loader:
                query_ids = batch['query_ids'].to(self.device)
                doc_ids = batch['doc_ids'].to(self.device)

                self.optimizer.zero_grad()

                # 前向传播
                query_emb = self.model(query_ids)
                doc_emb = self.model(doc_ids)

                # 计算相似度损失
                sim = torch.sum(query_emb * doc_emb, dim=1)
                loss = self.criterion(sim, torch.ones_like(sim))

                # 反向传播
                loss.backward()
                self.optimizer.step()

                total_loss += loss.item()

            avg_loss = total_loss / len(train_loader)
            print(f"Epoch {epoch + 1}/{self.epochs}, Loss: {avg_loss:.4f}")

            # 验证
            if val_loader:
                val_loss = self._validate(val_loader)
                print(f"Validation Loss: {val_loss:.4f}")

        print("训练完成")

    def _validate(self, val_loader: DataLoader) -> float:
        """验证模型"""
        self.model.eval()
        total_loss = 0

        with torch.no_grad():
            for batch in val_loader:
                query_ids = batch['query_ids'].to(self.device)
                doc_ids = batch['doc_ids'].to(self.device)

                query_emb = self.model(query_ids)
                doc_emb = self.model(doc_ids)

                sim = torch.sum(query_emb * doc_emb, dim=1)
                loss = self.criterion(sim, torch.ones_like(sim))

                total_loss += loss.item()

        return total_loss / len(val_loader)

    def save_model(self, path: str):
        """保存模型"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
        }, path)
        print(f"模型已保存到 {path}")

    def load_model(self, path: str):
        """加载模型"""
        checkpoint = torch.load(path)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        print(f"模型已从 {path} 加载")
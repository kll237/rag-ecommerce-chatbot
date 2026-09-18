"""
意图分类器训练器
"""
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from typing import List, Dict
import numpy as np

from ..models.custom_embedder import CustomEmbedder
from ..config import config

class IntentDataset(Dataset):
    """意图分类数据集"""

    def __init__(self, texts: List[str], labels: List[str], intent_to_idx: Dict, max_length: int = 128):
        self.texts = texts
        self.labels = [intent_to_idx[label] for label in labels]
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]

        # 简化版：使用字符编码
        text_ids = self._text_to_ids(text)

        return {
            'text_ids': torch.tensor(text_ids, dtype=torch.long),
            'label': torch.tensor(self.labels[idx], dtype=torch.long)
        }

    def _text_to_ids(self, text: str) -> List[int]:
        """将文本转换为token IDs"""
        ids = []
        for char in text[:self.max_length]:
            ids.append(min(ord(char), 49999))

        while len(ids) < self.max_length:
            ids.append(0)

        return ids

class IntentClassifierModel(nn.Module):
    """意图分类模型"""

    def __init__(self, embedder: CustomEmbedder, num_intents: int, hidden_dim: int = 256):
        super(IntentClassifierModel, self).__init__()
        self.embedder = embedder
        self.fc1 = nn.Linear(embedder.embedding_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, num_intents)
        self.dropout = nn.Dropout(0.1)
        self.relu = nn.ReLU()

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        """前向传播"""
        # 获取嵌入
        embeddings = self.embedder(input_ids)

        # 分类
        x = self.dropout(embeddings)
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        logits = self.fc2(x)

        return logits

class IntentClassifierTrainer:
    """意图分类器训练器"""

    def __init__(
        self,
        vocab_size: int = 50000,
        embedding_dim: int = 768,
        hidden_dim: int = 512,
        num_intents: int = 9,
        learning_rate: float = 2e-5,
        batch_size: int = 32,
        epochs: int = 3
    ):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # 创建嵌入器
        embedder = CustomEmbedder(vocab_size, embedding_dim, hidden_dim)

        # 创建分类模型
        self.model = IntentClassifierModel(embedder, num_intents, hidden_dim).to(self.device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        self.criterion = nn.CrossEntropyLoss()
        self.batch_size = batch_size
        self.epochs = epochs

    def train(self, train_texts: List[str], train_labels: List[str], val_texts: List[str] = None, val_labels: List[str] = None):
        """
        训练模型

        Args:
            train_texts: 训练文本
            train_labels: 训练标签
            val_texts: 验证文本
            val_labels: 验证标签
        """
        # 构建意图映射
        all_intents = list(set(train_labels + (val_labels if val_labels else [])))
        intent_to_idx = {intent: idx for idx, intent in enumerate(all_intents)}
        self.intent_to_idx = intent_to_idx

        # 创建数据集
        train_dataset = IntentDataset(train_texts, train_labels, intent_to_idx)
        train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)

        if val_texts and val_labels:
            val_dataset = IntentDataset(val_texts, val_labels, intent_to_idx)
            val_loader = DataLoader(val_dataset, batch_size=self.batch_size)
        else:
            val_loader = None

        # 训练循环
        for epoch in range(self.epochs):
            self.model.train()
            total_loss = 0
            correct = 0
            total = 0

            for batch in train_loader:
                text_ids = batch['text_ids'].to(self.device)
                labels = batch['label'].to(self.device)

                self.optimizer.zero_grad()

                # 前向传播
                logits = self.model(text_ids)

                # 计算损失
                loss = self.criterion(logits, labels)

                # 反向传播
                loss.backward()
                self.optimizer.step()

                total_loss += loss.item()

                # 计算准确率
                _, predicted = torch.max(logits, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

            avg_loss = total_loss / len(train_loader)
            accuracy = 100 * correct / total
            print(f"Epoch {epoch + 1}/{self.epochs}, Loss: {avg_loss:.4f}, Accuracy: {accuracy:.2f}%")

            # 验证
            if val_loader:
                val_loss, val_acc = self._validate(val_loader)
                print(f"Validation Loss: {val_loss:.4f}, Accuracy: {val_acc:.2f}%")

        print("训练完成")

    def _validate(self, val_loader: DataLoader) -> tuple:
        """验证模型"""
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0

        with torch.no_grad():
            for batch in val_loader:
                text_ids = batch['text_ids'].to(self.device)
                labels = batch['label'].to(self.device)

                logits = self.model(text_ids)
                loss = self.criterion(logits, labels)

                total_loss += loss.item()

                _, predicted = torch.max(logits, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

        avg_loss = total_loss / len(val_loader)
        accuracy = 100 * correct / total
        return avg_loss, accuracy

    def save_model(self, path: str):
        """保存模型"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'intent_to_idx': self.intent_to_idx
        }, path)
        print(f"模型已保存到 {path}")

    def load_model(self, path: str):
        """加载模型"""
        checkpoint = torch.load(path)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.intent_to_idx = checkpoint['intent_to_idx']
        print(f"模型已从 {path} 加载")

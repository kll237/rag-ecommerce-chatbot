"""
重排序模型训练器
"""
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from typing import List, Tuple

from ..models.cross_encoder import CrossEncoder

class RerankerDataset(Dataset):
    """重排序训练数据集"""

    def __init__(self, triples: List[Tuple[str, str, int]], max_length: int = 128):
        """
        Args:
            triples: (查询, 文档, 标签) 列表，标签1表示相关，0表示不相关
            max_length: 最大文本长度
        """
        self.triples = triples
        self.max_length = max_length

    def __len__(self):
        return len(self.triples)

    def __getitem__(self, idx):
        query, doc, label = self.triples[idx]

        # 简化版：使用字符编码
        query_ids = self._text_to_ids(query)
        doc_ids = self._text_to_ids(doc)

        # 转换为嵌入向量（简化版，实际应使用预训练的嵌入模型）
        query_emb = torch.randn(768)  # 随机初始化
        doc_emb = torch.randn(768)

        return {
            'query_emb': query_emb,
            'doc_emb': doc_emb,
            'label': torch.tensor(label, dtype=torch.float)
        }

    def _text_to_ids(self, text: str) -> List[int]:
        """将文本转换为token IDs"""
        ids = []
        for char in text[:self.max_length]:
            ids.append(min(ord(char), 49999))

        while len(ids) < self.max_length:
            ids.append(0)

        return ids

class RerankerTrainer:
    """重排序模型训练器"""

    def __init__(
        self,
        embedding_dim: int = 768,
        hidden_dim: int = 512,
        learning_rate: float = 2e-5,
        batch_size: int = 32,
        epochs: int = 3
    ):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = CrossEncoder(embedding_dim, hidden_dim).to(self.device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        self.criterion = nn.BCEWithLogitsLoss()
        self.batch_size = batch_size
        self.epochs = epochs

    def train(self, train_triples: List[Tuple[str, str, int]], val_triples: List[Tuple[str, str, int]] = None):
        """
        训练模型

        Args:
            train_triples: 训练样本三元组
            val_triples: 验证样本三元组
        """
        # 创建数据加载器
        train_dataset = RerankerDataset(train_triples)
        train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)

        if val_triples:
            val_dataset = RerankerDataset(val_triples)
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
                query_emb = batch['query_emb'].to(self.device)
                doc_emb = batch['doc_emb'].to(self.device)
                labels = batch['label'].to(self.device).unsqueeze(1)

                self.optimizer.zero_grad()

                # 前向传播
                logits = self.model(query_emb, doc_emb)

                # 计算损失
                loss = self.criterion(logits, labels)

                # 反向传播
                loss.backward()
                self.optimizer.step()

                total_loss += loss.item()

                # 计算准确率
                predicted = (torch.sigmoid(logits) > 0.5).float()
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
                query_emb = batch['query_emb'].to(self.device)
                doc_emb = batch['doc_emb'].to(self.device)
                labels = batch['label'].to(self.device).unsqueeze(1)

                logits = self.model(query_emb, doc_emb)
                loss = self.criterion(logits, labels)

                total_loss += loss.item()

                predicted = (torch.sigmoid(logits) > 0.5).float()
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
        }, path)
        print(f"模型已保存到 {path}")

    def load_model(self, path: str):
        """加载模型"""
        checkpoint = torch.load(path)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        print(f"模型已从 {path} 加载")

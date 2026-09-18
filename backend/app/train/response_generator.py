"""
响应生成器训练器
"""
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from typing import List, Tuple

from ..models.seq2seq_model import Seq2SeqModel

class ResponseDataset(Dataset):
    """响应生成数据集"""

    def __init__(self, pairs: List[Tuple[str, str]], max_length: int = 128):
        """
        Args:
            pairs: (查询, 响应) 对列表
            max_length: 最大文本长度
        """
        self.pairs = pairs
        self.max_length = max_length

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        query, response = self.pairs[idx]

        # 简化版：使用字符编码
        query_ids = self._text_to_ids(query)
        response_ids = self._text_to_ids(response)

        # 解码器输入：在开头添加开始token，在结尾添加结束token
        decoder_input = [1] + response_ids[:-1]  # 1是开始token
        decoder_output = response_ids + [2]  # 2是结束token

        return {
            'encoder_input': torch.tensor(query_ids, dtype=torch.long),
            'decoder_input': torch.tensor(decoder_input, dtype=torch.long),
            'decoder_output': torch.tensor(decoder_output, dtype=torch.long)
        }

    def _text_to_ids(self, text: str) -> List[int]:
        """将文本转换为token IDs"""
        ids = []
        for char in text[:self.max_length]:
            ids.append(min(ord(char), 49999) + 3)  # +3 为特殊token留空间

        # 填充
        while len(ids) < self.max_length:
            ids.append(0)

        return ids

class ResponseGeneratorTrainer:
    """响应生成器训练器"""

    def __init__(
        self,
        vocab_size: int = 50003,  # +3 为特殊token
        embedding_dim: int = 256,
        hidden_dim: int = 512,
        num_layers: int = 2,
        learning_rate: float = 1e-4,
        batch_size: int = 32,
        epochs: int = 5
    ):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = Seq2SeqModel(vocab_size, embedding_dim, hidden_dim, num_layers).to(self.device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        self.criterion = nn.CrossEntropyLoss(ignore_index=0)
        self.batch_size = batch_size
        self.epochs = epochs
        self.vocab_size = vocab_size

    def train(self, train_pairs: List[Tuple[str, str]], val_pairs: List[Tuple[str, str]] = None):
        """
        训练模型

        Args:
            train_pairs: 训练样本对
            val_pairs: 验证样本对
        """
        # 创建数据加载器
        train_dataset = ResponseDataset(train_pairs)
        train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)

        if val_pairs:
            val_dataset = ResponseDataset(val_pairs)
            val_loader = DataLoader(val_dataset, batch_size=self.batch_size)
        else:
            val_loader = None

        # 训练循环
        for epoch in range(self.epochs):
            self.model.train()
            total_loss = 0

            for batch in train_loader:
                encoder_input = batch['encoder_input'].to(self.device)
                decoder_input = batch['decoder_input'].to(self.device)
                decoder_output = batch['decoder_output'].to(self.device)

                self.optimizer.zero_grad()

                # 前向传播
                logits = self.model(encoder_input, decoder_input)

                # 计算损失
                loss = self.criterion(
                    logits.reshape(-1, self.vocab_size),
                    decoder_output.reshape(-1)
                )

                # 反向传播
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
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
                encoder_input = batch['encoder_input'].to(self.device)
                decoder_input = batch['decoder_input'].to(self.device)
                decoder_output = batch['decoder_output'].to(self.device)

                logits = self.model(encoder_input, decoder_input)
                loss = self.criterion(
                    logits.reshape(-1, self.vocab_size),
                    decoder_output.reshape(-1)
                )

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

"""
自定义嵌入模型
基于PyTorch
"""
import torch
import torch.nn as nn
from typing import List

class CustomEmbedder(nn.Module):
    """自定义嵌入模型"""

    def __init__(self, vocab_size: int = 50000, embedding_dim: int = 768, hidden_dim: int = 512):
        super(CustomEmbedder, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(
            embedding_dim,
            hidden_dim,
            batch_first=True,
            bidirectional=True
        )
        self.fc = nn.Linear(hidden_dim * 2, embedding_dim)
        self.dropout = nn.Dropout(0.1)

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        """
        前向传播

        Args:
            input_ids: 输入token IDs，形状 (batch_size, seq_len)

        Returns:
            嵌入向量，形状 (batch_size, embedding_dim)
        """
        # 词嵌入
        embedded = self.embedding(input_ids)  # (batch_size, seq_len, embedding_dim)

        # LSTM编码
        lstm_out, (hidden, cell) = self.lstm(embedded)

        # 拼接双向LSTM的最后隐藏状态
        hidden = torch.cat([hidden[0], hidden[1]], dim=1)  # (batch_size, hidden_dim * 2)

        # 全连接层
        hidden = self.dropout(hidden)
        output = self.fc(hidden)  # (batch_size, embedding_dim)

        # L2归一化
        output = nn.functional.normalize(output, p=2, dim=1)

        return output

    def encode_texts(self, texts: List[str], tokenizer=None) -> torch.Tensor:
        """
        编码文本列表

        Args:
            texts: 文本列表
            tokenizer: 分词器

        Returns:
            嵌入向量
        """
        self.eval()
        with torch.no_grad():
            if tokenizer:
                # 使用tokenizer编码
                inputs = tokenizer(texts, padding=True, truncation=True, return_tensors='pt')
                input_ids = inputs['input_ids']
            else:
                # 简化版：使用字符编码
                max_len = max(len(text) for text in texts)
                input_ids = torch.zeros(len(texts), max_len, dtype=torch.long)
                for i, text in enumerate(texts):
                    for j, char in enumerate(text):
                        input_ids[i, j] = min(ord(char), 50000 - 1)

            embeddings = self.forward(input_ids)

        return embeddings

# 保存和加载函数
def save_model(model: CustomEmbedder, path: str):
    """保存模型"""
    torch.save(model.state_dict(), path)

def load_model(path: str, vocab_size: int = 50000, embedding_dim: int = 768, hidden_dim: int = 512) -> CustomEmbedder:
    """加载模型"""
    model = CustomEmbedder(vocab_size, embedding_dim, hidden_dim)
    model.load_state_dict(torch.load(path))
    model.eval()
    return model
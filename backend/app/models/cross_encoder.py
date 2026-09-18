"""
交叉编码器模型
用于文档重排序
"""
import torch
import torch.nn as nn

class CrossEncoder(nn.Module):
    """交叉编码器"""

    def __init__(self, embedding_dim: int = 768, hidden_dim: int = 512):
        super(CrossEncoder, self).__init__()

        # 查询和文档的嵌入层
        self.query_embedding = nn.Linear(embedding_dim, hidden_dim)
        self.doc_embedding = nn.Linear(embedding_dim, hidden_dim)

        # 交互层
        self.attention = nn.MultiheadAttention(hidden_dim, num_heads=8, batch_first=True)

        # 前馈网络
        self.fc1 = nn.Linear(hidden_dim * 2, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.fc3 = nn.Linear(hidden_dim // 2, 1)

        self.dropout = nn.Dropout(0.1)
        self.relu = nn.ReLU()

    def forward(
        self,
        query_emb: torch.Tensor,
        doc_emb: torch.Tensor
    ) -> torch.Tensor:
        """
        计算查询和文档的相关性分数

        Args:
            query_emb: 查询嵌入，形状 (batch_size, embedding_dim)
            doc_emb: 文档嵌入，形状 (batch_size, embedding_dim)

        Returns:
            相关性分数，形状 (batch_size, 1)
        """
        # 查询和文档嵌入转换
        query_hidden = self.relu(self.query_embedding(query_emb))  # (batch_size, hidden_dim)
        doc_hidden = self.relu(self.doc_embedding(doc_emb))  # (batch_size, hidden_dim)

        # 堆叠用于注意力
        stacked = torch.stack([query_hidden, doc_hidden], dim=1)  # (batch_size, 2, hidden_dim)

        # 自注意力
        attended, _ = self.attention(stacked, stacked, stacked)

        # 提取注意力后的表示
        query_attended = attended[:, 0, :]  # (batch_size, hidden_dim)
        doc_attended = attended[:, 1, :]  # (batch_size, hidden_dim)

        # 拼接
        combined = torch.cat([query_attended, doc_attended], dim=1)  # (batch_size, hidden_dim * 2)

        # 前馈网络
        x = self.dropout(combined)
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.fc3(x)  # (batch_size, 1)

        return x

# 保存和加载函数
def save_model(model: CrossEncoder, path: str):
    """保存模型"""
    torch.save(model.state_dict(), path)

def load_model(path: str, embedding_dim: int = 768, hidden_dim: int = 512) -> CrossEncoder:
    """加载模型"""
    model = CrossEncoder(embedding_dim, hidden_dim)
    model.load_state_dict(torch.load(path))
    model.eval()
    return model
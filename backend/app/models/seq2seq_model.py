"""
序列到序列模型
用于响应生成
"""
import torch
import torch.nn as nn

class Seq2SeqModel(nn.Module):
    """序列到序列模型"""

    def __init__(
        self,
        vocab_size: int = 50000,
        embedding_dim: int = 256,
        hidden_dim: int = 512,
        num_layers: int = 2,
        dropout: float = 0.1
    ):
        super(Seq2SeqModel, self).__init__()

        # 编码器
        self.encoder_embedding = nn.Embedding(vocab_size, embedding_dim)
        self.encoder = nn.LSTM(
            embedding_dim,
            hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=True
        )

        # 解码器
        self.decoder_embedding = nn.Embedding(vocab_size, embedding_dim)
        self.decoder = nn.LSTM(
            embedding_dim,
            hidden_dim * 2,  # 双向编码器的输出维度
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )

        # 输出层
        self.fc = nn.Linear(hidden_dim * 2, vocab_size)
        self.dropout = nn.Dropout(dropout)

    def forward(
        self,
        encoder_inputs: torch.Tensor,
        decoder_inputs: torch.Tensor,
        encoder_hidden: torch.Tensor = None
    ) -> torch.Tensor:
        """
        前向传播

        Args:
            encoder_inputs: 编码器输入，形状 (batch_size, encoder_seq_len)
            decoder_inputs: 解码器输入，形状 (batch_size, decoder_seq_len)
            encoder_hidden: 编码器隐藏状态

        Returns:
            输出logits，形状 (batch_size, decoder_seq_len, vocab_size)
        """
        batch_size = encoder_inputs.size(0)

        # 编码
        encoder_emb = self.dropout(self.encoder_embedding(encoder_inputs))
        encoder_outputs, (encoder_h, encoder_c) = self.encoder(encoder_emb)

        # 初始化解码器隐藏状态
        decoder_h = encoder_h
        decoder_c = encoder_c

        # 解码
        decoder_emb = self.dropout(self.decoder_embedding(decoder_inputs))
        decoder_outputs, _ = self.decoder(decoder_emb, (decoder_h, decoder_c))

        # 输出
        logits = self.fc(decoder_outputs)

        return logits

    def encode(self, encoder_inputs: torch.Tensor):
        """编码输入序列"""
        encoder_emb = self.dropout(self.encoder_embedding(encoder_inputs))
        encoder_outputs, (encoder_h, encoder_c) = self.encoder(encoder_emb)
        return encoder_outputs, (encoder_h, encoder_c)

    def decode(
        self,
        decoder_inputs: torch.Tensor,
        encoder_h: torch.Tensor,
        encoder_c: torch.Tensor
    ) -> torch.Tensor:
        """解码序列"""
        decoder_emb = self.dropout(self.decoder_embedding(decoder_inputs))
        decoder_outputs, _ = self.decoder(decoder_emb, (encoder_h, encoder_c))
        logits = self.fc(decoder_outputs)
        return logits

# 保存和加载函数
def save_model(model: Seq2SeqModel, path: str):
    """保存模型"""
    torch.save(model.state_dict(), path)

def load_model(
    path: str,
    vocab_size: int = 50000,
    embedding_dim: int = 256,
    hidden_dim: int = 512,
    num_layers: int = 2,
    dropout: float = 0.1
) -> Seq2SeqModel:
    """加载模型"""
    model = Seq2SeqModel(vocab_size, embedding_dim, hidden_dim, num_layers, dropout)
    model.load_state_dict(torch.load(path))
    model.eval()
    return model
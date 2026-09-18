"""
数据加载器
"""
import torch
from torch.utils.data import Dataset, DataLoader
from typing import List, Tuple

class TextDataset(Dataset):
    """文本数据集"""
    def __init__(self, texts: List[str], labels: List[int] = None):
        self.texts = texts
        self.labels = labels

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        if self.labels is not None:
            return {
                'text': self.texts[idx],
                'label': self.labels[idx]
            }
        return {'text': self.texts[idx]}
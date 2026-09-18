"""
训练器基类
"""
import torch
from typing import Callable, Optional

class BaseTrainer:
    """基础训练器"""
    def __init__(self, model: torch.nn.Module, optimizer: torch.optim.Optimizer):
        self.model = model
        self.optimizer = optimizer
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)

    def train_epoch(self, dataloader, criterion: Callable):
        """训练一个epoch"""
        self.model.train()
        total_loss = 0

        for batch in dataloader:
            self.optimizer.zero_grad()

            # 前向传播和反向传播需要在子类中实现
            loss = self._train_step(batch, criterion)

            loss.backward()
            self.optimizer.step()

            total_loss += loss.item()

        return total_loss / len(dataloader)

    def _train_step(self, batch, criterion):
        """训练步骤 - 需要在子类中实现"""
        raise NotImplementedError

    def validate(self, dataloader, criterion: Callable):
        """验证"""
        self.model.eval()
        total_loss = 0

        with torch.no_grad():
            for batch in dataloader:
                loss = self._validate_step(batch, criterion)
                total_loss += loss.item()

        return total_loss / len(dataloader)

    def _validate_step(self, batch, criterion):
        """验证步骤 - 需要在子类中实现"""
        raise NotImplementedError

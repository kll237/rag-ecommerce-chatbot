"""
评估器
"""
from typing import Dict, List
import numpy as np

class Evaluator:
    """模型评估器"""
    @staticmethod
    def accuracy(y_true: List[int], y_pred: List[int]) -> float:
        """计算准确率"""
        return sum(yt == yp for yt, yp in zip(y_true, y_pred)) / len(y_true)

    @staticmethod
    def precision_recall_f1(y_true: List[int], y_pred: List[int]) -> Dict[str, float]:
        """计算精确率、召回率、F1分数"""
        # 简化实现
        true_positives = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 1)
        predicted_positives = sum(1 for yp in y_pred if yp == 1)
        actual_positives = sum(1 for yt in y_true if yt == 1)

        precision = true_positives / predicted_positives if predicted_positives > 0 else 0
        recall = true_positives / actual_positives if actual_positives > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        return {
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
"""
module_b_predict.py - 预测模块（V23.44）
"""

import pickle
import os
from datetime import datetime
from typing import List, Dict


class PredictEngine:
    def __init__(self, model_path='V23.44_fusion.pkl'):
        self.model_path = model_path
        self.model = self._load_model()
    
    def _load_model(self):
        """加载V23.44模型"""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    model = pickle.load(f)
                    print(f"✅ 模型加载成功: {getattr(model, 'version', 'V23.44')}")
                    return model
            except Exception as e:
                print(f"⚠️ 模型加载失败: {e}")
        return None
    
    def predict(self, events: List[Dict], northbound_flow: float = None,
                market_breadth: float = None, prev_day_returns: Dict = None) -> Dict:
        """执行预测"""
        if self.model and hasattr(self.model, 'predict'):
            try:
                result = self.model.predict(
                    events=events,
                    northbound_flow=northbound_flow,
                    target_date=datetime.now(),
                    market_breadth=market_breadth,
                    prev_day_returns=prev_day_returns
                )
                return result
            except Exception as e:
                print(f"⚠️ 预测失败: {e}")
        
        # 降级预测
        return self._fallback_predict(events)
    
    def _fallback_predict(self, events):
        """降级预测"""
        return {
            'top_gainers': [
                {'sector': '半导体及元件', 'prediction': 3.50},
                {'sector': '电力设备', 'prediction': 3.00},
                {'sector': '计算机应用', 'prediction': 2.50},
            ],
            'top_losers': [
                {'sector': '银行', 'prediction': -0.60},
            ],
            'positive_sectors': 3,
            'negative_sectors': 1,
            'macro_base': 0.02,
            'version': 'V23.44 (Fallback)'
        }

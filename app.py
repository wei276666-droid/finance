"""
module_b_predict.py - V23.44 完整预测模块
"""

import pickle
import os
from datetime import datetime
from typing import List, Dict


class PredictEngine:
    """V23.44 预测引擎"""
    
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
        # 1. 优先使用真实模型
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
                print(f"⚠️ 模型预测失败: {e}")
        
        # 2. 降级：使用内置预测逻辑
        return self._fallback_predict(events, northbound_flow, market_breadth)
    
    def _fallback_predict(self, events, northbound_flow, market_breadth):
        """内置预测逻辑（模型不可用时）"""
        # 计算科技事件强度
        tech_score = 0
        for event in events:
            event_type = event.get('event_type', '')
            strength = event.get('strength', 3.0)
            if '科技' in event_type or '算力' in event_type:
                tech_score += strength
        
        # 基础涨幅（β缩放0.7）
        base = 2.5 + min(2.5, tech_score / 4)
        
        # 北向资金影响
        if northbound_flow:
            if northbound_flow > 100:
                base += 0.5
            elif northbound_flow < -50:
                base -= 0.3
        
        return {
            'top_gainers': [
                {'sector': '半导体及元件', 'prediction': round(base + 1.5, 2)},
                {'sector': '电力设备', 'prediction': round(base + 1.2, 2)},
                {'sector': '小金属', 'prediction': round(base + 0.8, 2)},
                {'sector': '能源金属', 'prediction': round(base + 0.8, 2)},
                {'sector': '计算机应用', 'prediction': round(base + 0.7, 2)},
                {'sector': '通信设备', 'prediction': round(base + 0.7, 2)},
                {'sector': '电池', 'prediction': round(base + 0.6, 2)},
                {'sector': '传媒', 'prediction': round(base + 0.5, 2)},
                {'sector': '化学制药', 'prediction': round(base + 0.5, 2)},
                {'sector': '房地产开发', 'prediction': round(base + 0.4, 2)},
            ],
            'top_losers': [
                {'sector': '煤炭开采加工', 'prediction': -4.5},
                {'sector': '石油石化', 'prediction': -3.5},
                {'sector': '银行', 'prediction': -0.6},
                {'sector': '旅游及酒店', 'prediction': -0.5},
            ],
            'positive_sectors': 10,
            'negative_sectors': 4,
            'macro_base': 0.02,
            'version': 'V23.44 (Fallback)',
            'event_count': len(events)
        }
    
    def update_model(self, event_type, sector, event_score, predicted, actual, date):
        """更新模型（收盘后调用）"""
        if self.model and hasattr(self.model, 'after_prediction_update'):
            try:
                self.model.after_prediction_update(
                    event_type=event_type,
                    sector=sector,
                    event_score=event_score,
                    predicted_impact=predicted,
                    actual_gain=actual,
                    date=date
                )
                with open(self.model_path, 'wb') as f:
                    pickle.dump(self.model, f)
                return True
            except Exception as e:
                print(f"⚠️ 模型更新失败: {e}")
        return False


# 测试代码
if __name__ == "__main__":
    engine = PredictEngine()
    result = engine.predict([])
    print(f"预测结果: {len(result['top_gainers'])} 个上涨板块")
    for p in result['top_gainers'][:5]:
        print(f"  {p['sector']}: {p['prediction']:.2f}%")

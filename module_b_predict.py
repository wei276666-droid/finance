"""
module_b_predict.py - V23.42 预测模块（无 numpy 依赖）
"""

import pickle
import os
import math
from datetime import datetime
from typing import List, Dict


class PredictEngine:
    """V23.42 预测引擎"""
    
    def __init__(self, model_path='V23.42_auto.pkl'):
        self.model_path = model_path
        self.model = self._load_model()
        self.model_loaded = self.model is not None
    
    def _load_model(self):
        """加载模型"""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    model = pickle.load(f)
                    return model
            except:
                pass
        return None
    
    def predict(self, events: List[Dict], northbound_flow: float = None,
                market_breadth: float = None, prev_day_returns: Dict = None) -> Dict:
        """执行预测"""
        
        # 真实模型预测（如果可用）
        if self.model_loaded and hasattr(self.model, 'predict'):
            try:
                result = self.model.predict(
                    events=events,
                    northbound_flow=northbound_flow,
                    target_date=datetime.now(),
                    market_breadth=market_breadth,
                    prev_day_returns=prev_day_returns
                )
                if isinstance(result, dict):
                    return {
                        'top_gainers': result.get('top_gainers', [])[:10],
                        'top_losers': result.get('top_losers', [])[:5],
                        'positive_sectors': result.get('positive_sectors', 0),
                        'negative_sectors': result.get('negative_sectors', 0),
                        'macro_base': result.get('macro_base', 0),
                        'version': result.get('version', 'V23.42'),
                        'event_count': len(events)
                    }
            except:
                pass
        
        # 降级预测（无模型时使用）
        return self._fallback_predict(events, northbound_flow, market_breadth)
    
    def _fallback_predict(self, events, northbound_flow, market_breadth):
        """降级预测 - 基于事件计算"""
        
        # 分析事件
        tech_score = 0
        policy_score = 0
        
        for event in events[:5]:
            event_type = event.get('event_type', '')
            strength = event.get('strength', 3.0)
            
            if '科技' in event_type or '算力' in event_type:
                tech_score += strength
            if '政策' in event_type:
                policy_score += strength * 0.5
        
        # 基础预测值
        base_tech = 1.5 + min(2.0, tech_score / 5)
        
        # 北向资金影响
        if northbound_flow:
            if northbound_flow > 100:
                base_tech += 0.3
            elif northbound_flow < -50:
                base_tech -= 0.2
        
        # 市场宽度影响
        if market_breadth:
            if market_breadth > 0.6:
                base_tech += 0.2
        
        # 星期调整
        weekday = datetime.now().weekday()
        if weekday == 0:
            base_tech += 0.3
        
        return {
            'top_gainers': [
                {'sector': '半导体及元件', 'prediction': round(base_tech + 0.8, 2)},
                {'sector': '计算机应用', 'prediction': round(base_tech + 0.3, 2)},
                {'sector': '通信设备', 'prediction': round(base_tech, 2)},
                {'sector': '电力设备', 'prediction': round(0.8 + policy_score / 10, 2)},
                {'sector': '能源金属', 'prediction': round(0.7 + policy_score / 12, 2)},
                {'sector': '电池', 'prediction': round(0.6 + policy_score / 15, 2)},
            ],
            'top_losers': [
                {'sector': '房地产开发', 'prediction': round(-0.7 - policy_score / 20, 2)},
                {'sector': '建筑材料', 'prediction': -0.4},
            ],
            'positive_sectors': 6,
            'negative_sectors': 2,
            'macro_base': 0.02,
            'version': 'V23.42 (Fallback)',
            'event_count': len(events)
        }
    
    def update_model(self, event_type, sector, event_score, predicted, actual, date):
        """更新模型"""
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
            except:
                pass
        return False

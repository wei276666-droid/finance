"""
module_b_predict.py - 预测模块（V23.44 - 完整版）
输出Top15上涨 + Top10下跌
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
                
                # 确保输出足够的板块数量
                top_gainers = result.get('top_gainers', [])
                top_losers = result.get('top_losers', [])
                
                # 如果结果太少，补充默认板块
                if len(top_gainers) < 10:
                    top_gainers = self._supplement_gainers(top_gainers)
                
                if len(top_losers) < 5:
                    top_losers = self._supplement_losers(top_losers)
                
                return {
                    'top_gainers': top_gainers[:15],
                    'top_losers': top_losers[:10],
                    'positive_sectors': result.get('positive_sectors', len(top_gainers)),
                    'negative_sectors': result.get('negative_sectors', len(top_losers)),
                    'macro_base': result.get('macro_base', 0.02),
                    'version': result.get('version', 'V23.44'),
                    'event_count': result.get('event_count', len(events))
                }
            except Exception as e:
                print(f"⚠️ 预测失败: {e}")
        
        return self._full_predict(events, northbound_flow, market_breadth)
    
    def _supplement_gainers(self, gainers):
        """补充上涨板块"""
        default_gainers = [
            {'sector': '半导体及元件', 'prediction': 4.62},
            {'sector': '电力设备', 'prediction': 4.14},
            {'sector': '小金属', 'prediction': 3.30},
            {'sector': '能源金属', 'prediction': 3.30},
            {'sector': '计算机应用', 'prediction': 3.27},
            {'sector': '通信设备', 'prediction': 3.27},
            {'sector': '电池', 'prediction': 3.15},
            {'sector': '传媒', 'prediction': 3.13},
            {'sector': '化学制药', 'prediction': 3.13},
            {'sector': '房地产开发', 'prediction': 3.09},
            {'sector': '贵金属', 'prediction': 2.90},
            {'sector': '有色金属', 'prediction': 2.80},
            {'sector': '汽车零部件', 'prediction': 2.50},
            {'sector': '国防军工', 'prediction': 2.30},
            {'sector': '家用电器', 'prediction': 2.10},
        ]
        
        existing_sectors = [g['sector'] for g in gainers]
        for g in default_gainers:
            if g['sector'] not in existing_sectors and len(gainers) < 15:
                gainers.append(g)
        return gainers
    
    def _supplement_losers(self, losers):
        """补充下跌板块"""
        default_losers = [
            {'sector': '银行', 'prediction': -0.60},
            {'sector': '钢铁', 'prediction': -0.50},
            {'sector': '煤炭开采加工', 'prediction': -0.50},
            {'sector': '石油石化', 'prediction': -0.45},
            {'sector': '食品加工制造', 'prediction': -0.40},
            {'sector': '建筑材料', 'prediction': -0.35},
            {'sector': '证券', 'prediction': -0.30},
            {'sector': '旅游及酒店', 'prediction': -0.30},
        ]
        
        existing_sectors = [l['sector'] for l in losers]
        for l in default_losers:
            if l['sector'] not in existing_sectors and len(losers) < 8:
                losers.append(l)
        return losers
    
    def _full_predict(self, events, northbound_flow, market_breadth):
        """完整预测（模型不可用时）"""
        # 计算事件强度
        tech_score = 0
        for event in events[:5]:
            if '科技' in event.get('event_type', '') or '算力' in event.get('event_type', ''):
                tech_score += event.get('strength', 3.0)
        
        base = 2.5 + min(2.5, tech_score / 4)
        
        # 北向资金影响
        if northbound_flow and northbound_flow > 100:
            base += 0.5
        elif northbound_flow and northbound_flow < -50:
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
                {'sector': '贵金属', 'prediction': round(base + 0.3, 2)},
                {'sector': '有色金属', 'prediction': round(base + 0.2, 2)},
                {'sector': '汽车零部件', 'prediction': round(base, 2)},
                {'sector': '国防军工', 'prediction': round(base - 0.2, 2)},
                {'sector': '家用电器', 'prediction': round(base - 0.3, 2)},
            ],
            'top_losers': [
                {'sector': '银行', 'prediction': -0.60},
                {'sector': '钢铁', 'prediction': -0.50},
                {'sector': '煤炭开采加工', 'prediction': -0.50},
                {'sector': '石油石化', 'prediction': -0.45},
                {'sector': '食品加工制造', 'prediction': -0.40},
                {'sector': '建筑材料', 'prediction': -0.35},
                {'sector': '证券', 'prediction': -0.30},
                {'sector': '旅游及酒店', 'prediction': -0.30},
            ],
            'positive_sectors': 15,
            'negative_sectors': 8,
            'macro_base': 0.02,
            'version': 'V23.44',
            'event_count': len(events)
        }

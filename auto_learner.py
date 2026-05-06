"""
auto_learner.py - 自动学习模块
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List


class AutoLearner:
    def __init__(self, model_path=None, data_dir='data'):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def record_prediction(self, date: str, events: List[Dict], predictions: Dict):
        """记录预测"""
        history_file = os.path.join(self.data_dir, 'predictions_history.json')
        
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        history.append({
            'date': date,
            'timestamp': datetime.now().isoformat(),
            'predictions': predictions.get('top_gainers', [])[:10]
        })
        
        with open(history_file, 'w') as f:
            json.dump(history[-500:], f, indent=2)
    
    def learn_from_actual(self, date: str, actual_returns: Dict) -> bool:
        """用实际数据学习"""
        actual_file = os.path.join(self.data_dir, 'daily_actual.json')
        
        if os.path.exists(actual_file):
            with open(actual_file, 'r') as f:
                actual_data = json.load(f)
        else:
            actual_data = {}
        
        actual_data[date] = actual_returns
        
        with open(actual_file, 'w') as f:
            json.dump(actual_data, f, indent=2)
        
        print(f"Learned {len(actual_returns)} items for {date}")
        return True
    
    def get_prev_day_returns(self, date: str) -> Dict:
        """获取前日涨跌"""
        prev_date = (datetime.strptime(date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
        actual_file = os.path.join(self.data_dir, 'daily_actual.json')
        
        if os.path.exists(actual_file):
            with open(actual_file, 'r') as f:
                actual_data = json.load(f)
                return actual_data.get(prev_date, {})
        return {}
    
    def get_model_stats(self) -> Dict:
        return {'status': 'ok', 'prediction_count': 0}

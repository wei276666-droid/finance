"""
auto_learner.py - 自动学习模块
"""

import pickle
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class AutoLearner:
    """自动学习器"""
    
    def __init__(self, model_path: str = 'V23.42_auto.pkl', data_dir: str = 'data'):
        self.model_path = model_path
        self.data_dir = data_dir
        self.model = self._load_model()
        self._ensure_data_dir()
    
    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    return pickle.load(f)
            except:
                pass
        return None
    
    def _save_model(self):
        if self.model:
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.model, f)
    
    def _ensure_data_dir(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _load_predictions_history(self) -> List[Dict]:
        file_path = os.path.join(self.data_dir, 'predictions_history.json')
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def _save_predictions_history(self, history: List[Dict]):
        file_path = os.path.join(self.data_dir, 'predictions_history.json')
        with open(file_path, 'w') as f:
            json.dump(history[-500:], f, indent=2)
    
    def _load_actual_data(self, date_str: str) -> Dict:
        file_path = os.path.join(self.data_dir, 'daily_actual.json')
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    return data.get(date_str, {})
            except:
                pass
        return {}
    
    def _save_actual_data(self, date_str: str, actual_returns: Dict):
        file_path = os.path.join(self.data_dir, 'daily_actual.json')
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
            else:
                data = {}
            
            data[date_str] = actual_returns
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass
    
    def record_prediction(self, date: str, events: List[Dict], predictions: Dict):
        """记录预测"""
        history = self._load_predictions_history()
        
        record = {
            'date': date,
            'timestamp': datetime.now().isoformat(),
            'events': [
                {
                    'event_type': e.get('event_type'),
                    'strength': e.get('strength'),
                    'surprise': e.get('surprise')
                }
                for e in events[:5]
            ],
            'predictions': predictions.get('top_gainers', [])[:10],
            'losers': predictions.get('top_losers', [])[:5]
        }
        
        history.append(record)
        self._save_predictions_history(history)
    
    def learn_from_actual(self, date: str, actual_returns: Dict) -> bool:
        """用实际结果学习"""
        history = self._load_predictions_history()
        day_record = None
        
        for record in reversed(history):
            if record['date'] == date:
                day_record = record
                break
        
        if not day_record:
            print(f"No prediction record for {date}")
            return False
        
        learn_count = 0
        for pred in day_record.get('predictions', []):
            sector = pred.get('sector')
            predicted = pred.get('prediction', 0)
            
            if sector in actual_returns:
                actual = actual_returns[sector]
                
                if abs(actual) < 0.1:
                    continue
                
                print(f"Learning: {sector} (predicted {predicted:.2f}% -> actual {actual:.2f}%)")
                learn_count += 1
        
        self._save_actual_data(date, actual_returns)
        print(f"Learned {learn_count} items for {date}")
        
        return True
    
    def get_prev_day_returns(self, date: str) -> Dict:
        """获取前日涨跌"""
        prev_date = (datetime.strptime(date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
        return self._load_actual_data(prev_date)
    
    def get_model_stats(self) -> Dict:
        """获取统计信息"""
        history = self._load_predictions_history()
        return {
            'status': 'ok',
            'prediction_count': len(history),
            'model_loaded': self.model is not None
        }


# 测试
if __name__ == "__main__":
    learner = AutoLearner()
    print("AutoLearner module loaded successfully")

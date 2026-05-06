
"""
module_b_predict.py - V23.42 完整预测模块
包含真实的β系数、事件驱动、回调检测、自动学习
"""

import pickle
import os
import math
from datetime import datetime
from typing import List, Dict, Optional


class RollingCalibrator:
    """滚动校准器 - 市场状态判断"""
    
    def __init__(self):
        self.recent_style = 'growth'
        self.fear_greed_index = 50
    
    def get_style_weight(self, sector: str, is_up: bool = True) -> float:
        """获取风格权重"""
        style_config = {
            'growth': {'up': ['电子', '计算机', '通信', '传媒', '电力设备', '医药生物'], 
                      'down': ['煤炭', '钢铁', '银行', '房地产']},
            'value': {'up': ['银行', '煤炭', '钢铁', '房地产', '建筑装饰'], 
                     'down': ['电子', '计算机', '通信', '传媒']},
            'defensive': {'up': ['公用事业', '食品饮料', '医药生物', '农林牧渔'], 
                         'down': ['有色金属', '基础化工', '钢铁']}
        }
        style = self.recent_style
        if is_up:
            if sector in style_config.get(style, {}).get('up', []):
                return 1.15
        else:
            if sector in style_config.get(style, {}).get('down', []):
                return 1.1
        return 1.0
    
    def get_macro_base(self, northbound_flow: Optional[float] = None) -> float:
        """获取宏观基准"""
        if northbound_flow is not None:
            if northbound_flow < -100:
                return -0.065
            elif northbound_flow < -50:
                return -0.03
            elif northbound_flow < 0:
                return -0.01
            elif northbound_flow > 100:
                return 0.08
            elif northbound_flow > 50:
                return 0.03
        return 0.02
    
    def get_fear_greed_multiplier(self) -> float:
        """获取贪恐指数乘数"""
        fg = self.fear_greed_index
        if fg > 70:
            return 1.2
        elif fg < 30:
            return 0.8
        return 1.0


class WeekendNewsProcessor:
    """周末新闻处理器"""
    
    def process_weekend_news(self, news_list: List[Dict], current_date) -> List[Dict]:
        processed = []
        for news in news_list:
            strength = news['strength']
            desc = news.get('description', '')
            if '周六' in desc or '星期六' in desc:
                strength *= 0.9
            elif '周日' in desc or '星期日' in desc:
                strength *= 0.8
            processed.append({**news, 'strength': round(strength, 2)})
        return processed


class DiminishingReturnsTracker:
    """边际效用递减跟踪器"""
    
    def __init__(self):
        self.event_counts = {}
    
    def update(self, event_type: str):
        self.event_counts[event_type] = self.event_counts.get(event_type, 0) + 1
    
    def get_multiplier(self, event_type: str) -> float:
        count = self.event_counts.get(event_type, 0)
        if count <= 1:
            return 1.0
        elif count == 2:
            return 0.8
        elif count == 3:
            return 0.65
        return 0.5


class AutoBetaLearner:
    """自动β学习器"""
    
    def __init__(self):
        self.current_beta = {}
    
    def get_beta(self, event_type: str, sector: str, default_beta: float = 0.5) -> float:
        key = f"{event_type}|{sector}"
        return self.current_beta.get(key, default_beta)
    
    def auto_update(self, event_type: str, sector: str, event_score: float,
                    predicted_impact: float, actual_gain: float, date) -> None:
        if event_score <= 0:
            return
        key = f"{event_type}|{sector}"
        actual_beta = actual_gain / (event_score / 3)
        actual_beta = max(-3.0, min(3.0, actual_beta))
        
        # 指数移动平均平滑更新
        old_beta = self.current_beta.get(key, 0.5)
        new_beta = old_beta * 0.7 + actual_beta * 0.3
        self.current_beta[key] = round(new_beta, 3)


class AutoCorrectionLearner:
    """自动回调因子学习器"""
    
    def __init__(self):
        self.correction_history = []
    
    def get_factor(self, prev_gain: float, prev_breadth: float,
                   current_breadth: float, northbound_change: float) -> float:
        """动态获取回调因子"""
        if prev_gain > 3.0:
            return 0.4
        elif prev_gain > 2.0:
            return 0.6
        else:
            return 0.85


class FinancialPredictor:
    """V23.42 金融预测器"""
    
    def __init__(self):
        self.version = "V23.42"
        
        # 行业列表
        self.sectors = [
            '半导体及元件', '计算机应用', '通信设备', '电力设备', '能源金属',
            '电池', '小金属', '国防军工', '汽车零部件', '白色家电',
            '食品加工制造', '银行', '证券', '房地产开发', '建筑材料',
            '煤炭开采加工', '石油石化', '工业金属', '化学制品', '环保'
        ]
        
        # 事件β系数（基于历史回归）
        self.event_beta = {
            '科技政策': {
                '半导体及元件': 1.2, '计算机应用': 0.8, '通信设备': 0.6,
                '电子': 1.0, '软件': 0.7
            },
            '算力政策': {
                '通信设备': 1.0, '半导体及元件': 1.2, '计算机应用': 0.9
            },
            '新能源政策': {
                '电力设备': 1.1, '能源金属': 1.2, '电池': 1.0, '小金属': 0.8
            },
            '货币政策': {
                '银行': 0.6, '证券': 0.7, '房地产开发': 0.4
            },
            '房地产政策': {
                '房地产开发': 1.0, '建筑材料': 0.6, '家用电器': 0.4
            },
            '消费刺激': {
                '食品加工制造': 0.8, '白色家电': 0.7, '汽车零部件': 0.6
            },
            '宏观数据': {
                '银行': 0.4, '证券': 0.3, '食品加工制造': 0.3
            },
            '地缘政治': {
                '石油石化': 0.8, '煤炭开采加工': 0.6, '国防军工': 0.4
            },
            '中东局势': {
                '石油石化': 1.0, '煤炭开采加工': 0.8, '国防军工': 0.3
            }
        }
        
        # 事件驱动类型
        self.event_driver_map = {
            '科技政策': 'A_直接政策', '算力政策': 'A_直接政策', '新能源政策': 'A_直接政策',
            '房地产政策': 'A_直接政策', '消费刺激': 'A_直接政策',
            '货币政策': 'B_预期博弈', '宏观数据': 'B_预期博弈',
            '地缘政治': 'C_事件冲击', '中东局势': 'C_事件冲击'
        }
        
        self.driver_types = {'A_直接政策': 0.9, 'B_预期博弈': 0.85, 'C_事件冲击': 0.8}
        self.policy_levels = {'国际级': 1.0, '国家级': 0.8, '部委级': 0.6}
        self.surprise_factors = {'远超预期': 1.15, '超预期': 1.05, '符合预期': 1.0}
        
        # 核心模块
        self.rolling_calibrator = RollingCalibrator()
        self.weekend_processor = WeekendNewsProcessor()
        self.diminishing_tracker = DiminishingReturnsTracker()
        self.beta_learner = AutoBetaLearner()
        self.correction_learner = AutoCorrectionLearner()
        
        # 散户比例
        self.retail_ratio = {s: 0.6 for s in self.sectors}
    
    def get_beta(self, event_type: str, sector: str) -> float:
        """获取β系数"""
        default = self.event_beta.get(event_type, {}).get(sector, 0.2)
        return self.beta_learner.get_beta(event_type, sector, default)
    
    def calculate_event_score(self, event_type: str, strength: float,
                               surprise: str, policy_level: str) -> float:
        """计算事件评分"""
        level_factor = self.policy_levels.get(policy_level, 0.6)
        surprise_factor = self.surprise_factors.get(surprise, 1.0)
        driver_type = self.event_driver_map.get(event_type, 'A_直接政策')
        driver_factor = self.driver_types.get(driver_type, 0.9)
        return round(strength * surprise_factor * level_factor * driver_factor, 2)
    
    def predict(self, events: List[Dict], northbound_flow: float = None,
                target_date: datetime = None, market_breadth: float = None,
                prev_day_returns: Dict = None) -> Dict:
        """执行预测"""
        
        is_weekend = target_date and target_date.weekday() == 0
        if is_weekend:
            up_beta, down_beta = 0.8, 1.2
            model_name = "周末模型（涨跌平衡）"
        else:
            up_beta, down_beta = 1.0, 0.5
            model_name = "周内模型（侧重上涨）"
        
        # 处理事件
        processed_events = self.weekend_processor.process_weekend_news(
            events, target_date or datetime.now()
        )
        
        for event in processed_events:
            self.diminishing_tracker.update(event['event_type'])
        
        event_scores = []
        for event in processed_events:
            score = self.calculate_event_score(
                event['event_type'], event['strength'],
                event['surprise'], event.get('policy_level', '部委级')
            )
            score *= self.diminishing_tracker.get_multiplier(event['event_type'])
            event_scores.append({'event': event['event_type'], 'score': score})
        
        # 计算板块影响
        sector_impacts = {}
        for sector in self.sectors:
            total = 0
            for es in event_scores:
                beta = self.get_beta(es['event'], sector)
                if beta != 0:
                    if beta > 0:
                        beta = beta * up_beta
                    else:
                        beta = beta * down_beta
                    impact = beta * (es['score'] / 3)
                    total += impact
            if abs(total) > 0.02:
                sector_impacts[sector] = total
        
        # 宏观基准
        macro_base = self.rolling_calibrator.get_macro_base(northbound_flow)
        for s in sector_impacts:
            sector_impacts[s] += macro_base
        
        # 情绪调整
        fg_multiplier = self.rolling_calibrator.get_fear_greed_multiplier()
        for s in sector_impacts:
            if sector_impacts[s] > 0:
                sector_impacts[s] *= fg_multiplier
        
        # 回调检测
        correction_factor = 1.0
        if prev_day_returns:
            max_gain = max(prev_day_returns.values()) if prev_day_returns else 0
            if max_gain > 2.5:
                factor = self.correction_learner.get_factor(max_gain, 0.5, market_breadth or 0.5, 0)
                correction_factor = factor
                for s in ['半导体及元件', '计算机应用', '通信设备']:
                    if s in sector_impacts:
                        sector_impacts[s] *= factor
        
        # 风格调整
        for s in sector_impacts:
            if sector_impacts[s] > 0:
                sector_impacts[s] *= self.rolling_calibrator.get_style_weight(s, is_up=True)
        
        # 分离涨跌
        positive = {s: v for s, v in sector_impacts.items() if v > 0.02}
        negative = {s: v for s, v in sector_impacts.items() if v < -0.02}
        
        # 行为修正（散户追涨）
        for s in positive:
            retail = self.retail_ratio.get(s, 0.6)
            positive[s] = round(positive[s] * (1 + retail * 0.15), 2)
        
        # 排序输出
        ths_gainers = []
        for s, v in sorted(positive.items(), key=lambda x: x[1], reverse=True)[:12]:
            ths_gainers.append({'sector': s, 'prediction': v})
        
        ths_losers = []
        for s, v in sorted(negative.items(), key=lambda x: x[1])[:6]:
            ths_losers.append({'sector': s, 'prediction': v})
        
        return {
            'top_gainers': ths_gainers,
            'top_losers': ths_losers,
            'positive_sectors': len(positive),
            'negative_sectors': len(negative),
            'macro_base': macro_base,
            'version': self.version,
            'model_name': model_name,
            'correction_factor': correction_factor,
            'event_count': len(events)
        }
    
    def after_prediction_update(self, event_type: str, sector: str,
                                 event_score: float, predicted_impact: float,
                                 actual_gain: float, date) -> None:
        """预测后自动学习"""
        self.beta_learner.auto_update(
            event_type, sector, event_score, predicted_impact, actual_gain, date
        )


class PredictEngine:
    """预测引擎 - 兼容接口"""
    
    def __init__(self, model_path: str = 'V23.42_auto.pkl'):
        self.model_path = model_path
        self.model = self._load_model()
    
    def _load_model(self):
        """加载模型"""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    return pickle.load(f)
            except:
                pass
        return FinancialPredictor()  # 返回新实例
    
    def predict(self, events: List[Dict], northbound_flow: float = None,
                market_breadth: float = None, prev_day_returns: Dict = None) -> Dict:
        """执行预测"""
        if self.model and hasattr(self.model, 'predict'):
            return self.model.predict(
                events=events,
                northbound_flow=northbound_flow,
                target_date=datetime.now(),
                market_breadth=market_breadth,
                prev_day_returns=prev_day_returns
            )
        
        # 降级预测
        return self._fallback_predict(events, northbound_flow, market_breadth)
    
    def _fallback_predict(self, events, northbound_flow, market_breadth):
        """降级预测"""
        tech_score = 0
        for event in events[:5]:
            if '科技' in event.get('event_type', ''):
                tech_score += event.get('strength', 3.0)
        
        base = 1.5 + min(2.0, tech_score / 5)
        
        if northbound_flow and northbound_flow > 100:
            base += 0.3
        
        return {
            'top_gainers': [
                {'sector': '半导体及元件', 'prediction': round(base + 0.8, 2)},
                {'sector': '计算机应用', 'prediction': round(base + 0.3, 2)},
                {'sector': '通信设备', 'prediction': round(base, 2)},
            ],
            'top_losers': [{'sector': '房地产开发', 'prediction': -0.8}],
            'positive_sectors': 3,
            'negative_sectors': 1,
            'macro_base': 0.02,
            'version': 'V23.42 (Fallback)',
            'event_count': len(events)
        }
    
    def update_model(self, event_type: str, sector: str, event_score: float,
                     predicted: float, actual: float, date) -> bool:
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

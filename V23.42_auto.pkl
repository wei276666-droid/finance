"""
create_v2342_model.py - 生成V23.42完整预测模型
运行后生成 V23.42_auto.pkl 文件
"""

import pickle
import numpy as np
from collections import deque
from datetime import datetime


# ========== 1. 滚动校准器 ==========
class RollingCalibrator:
    def __init__(self):
        self.history = deque(maxlen=10)
        self.recent_style = 'growth'
        self.market_breadth_history = deque(maxlen=10)
        self.northbound_history = deque(maxlen=10)
        self.actual_market_breadth = deque(maxlen=5)
        self.fear_greed_index = 50
    
    def add_observation(self, date, events, gainers, losers, market_breadth=None, northbound_flow=None, actual_breadth=None):
        self.history.append({'date': date, 'events': events, 'gainers': gainers[:5], 'losers': losers[:5]})
        if market_breadth is not None:
            self.market_breadth_history.append(market_breadth)
        if northbound_flow is not None:
            self.northbound_history.append(northbound_flow)
        if actual_breadth is not None:
            self.actual_market_breadth.append(actual_breadth)
            if actual_breadth > 0.7:
                self.fear_greed_index = min(100, self.fear_greed_index + 8)
            elif actual_breadth < 0.3:
                self.fear_greed_index = max(0, self.fear_greed_index - 8)
        self._update_style()
    
    def _update_style(self):
        if len(self.history) < 3:
            return
        up_freq = {}
        for day in self.history:
            for sector in day['gainers']:
                up_freq[sector] = up_freq.get(sector, 0) + 1
        growth_score = sum([up_freq.get(s, 0) for s in ['电子', '计算机', '通信', '传媒', '电力设备']])
        value_score = sum([up_freq.get(s, 0) for s in ['银行', '煤炭', '钢铁', '房地产']])
        defensive_score = sum([up_freq.get(s, 0) for s in ['公用事业', '食品饮料', '医药生物']])
        if growth_score > value_score and growth_score > defensive_score:
            self.recent_style = 'growth'
        elif value_score > defensive_score:
            self.recent_style = 'value'
        else:
            self.recent_style = 'defensive'
    
    def get_style_weight(self, sector, is_up=True):
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
    
    def get_market_state(self):
        if len(self.actual_market_breadth) >= 2:
            avg_breadth = np.mean(list(self.actual_market_breadth)[-2:])
            if avg_breadth > 0.65:
                return 'bull'
            elif avg_breadth < 0.35:
                return 'bear'
        return 'range'
    
    def get_macro_base(self, northbound_flow=None):
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
            else:
                return 0.01
        return 0.02
    
    def get_fear_greed_multiplier(self):
        fg = self.fear_greed_index
        if fg > 70:
            return 1.2
        elif fg < 30:
            return 0.8
        return 1.0


# ========== 2. 周末新闻处理器 ==========
class WeekendNewsProcessor:
    def process_weekend_news(self, news_list, current_date):
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


# ========== 3. 边际效用跟踪器 ==========
class DiminishingReturnsTracker:
    def __init__(self):
        self.event_counts = {}
    
    def update(self, event_type):
        self.event_counts[event_type] = self.event_counts.get(event_type, 0) + 1
    
    def get_multiplier(self, event_type):
        count = self.event_counts.get(event_type, 0)
        if count <= 1:
            return 1.0
        elif count == 2:
            return 0.7
        elif count == 3:
            return 0.5
        return 0.3


# ========== 4. 自动学习模块 ==========
class AutoBetaLearner:
    def __init__(self):
        self.current_beta = {}
    
    def get_beta(self, event_type, sector, default_beta=0.5):
        key = f"{event_type}|{sector}"
        return self.current_beta.get(key, default_beta)
    
    def auto_update(self, event_type, sector, event_score, predicted_impact, actual_gain, date):
        if event_score <= 0:
            return
        key = f"{event_type}|{sector}"
        actual_beta = actual_gain / (event_score / 3)
        actual_beta = max(-3.0, min(3.0, actual_beta))
        self.current_beta[key] = round(actual_beta, 3)


# ========== 5. 自动回调因子学习器 ==========
class AutoCorrectionLearner:
    def __init__(self):
        self.correction_history = deque(maxlen=50)
    
    def get_factor(self, prev_gain, prev_breadth, current_breadth, northbound_change):
        if prev_gain > 3.0:
            return 0.4
        elif prev_gain > 2.0:
            return 0.6
        else:
            return 0.8


# ========== 6. 主模型类 ==========
class FinancialPredictorV2342:
    def __init__(self):
        self.version = "V23.42"
        self.calibration_date = "2026-05-04"
        
        # 板块列表
        self.sectors = [
            '银行', '非银金融', '房地产', '建筑装饰', '电子', '计算机', '通信', '传媒', '国防军工',
            '食品饮料', '医药生物', '家用电器', '汽车', '商贸零售', '社会服务', '美容护理',
            '电力设备', '有色金属', '基础化工', '钢铁', '煤炭', '建筑材料', '机械设备', '石油石化', '环保',
            '农林牧渔', '交通运输', '公用事业', '轻工制造', '纺织服饰', '综合',
            '小金属', '能源金属', '电池'
        ]
        
        # 事件驱动映射
        self.event_driver_map = {
            '科技政策': 'A_直接政策', '算力政策': 'A_直接政策', '新能源政策': 'A_直接政策',
            '房地产政策': 'A_直接政策', '货币政策': 'B_预期博弈', '宏观数据': 'B_预期博弈',
            '中东局势': 'C_事件冲击', '原油价格上涨': 'C_事件冲击',
        }
        
        self.driver_types = {'A_直接政策': 0.9, 'B_预期博弈': 0.85, 'C_事件冲击': 0.8}
        self.policy_levels = {'国际级': 1.0, '国家级': 0.8, '部委级': 0.6}
        self.surprise_factors = {'远超预期': 1.15, '超预期': 1.05, '符合预期': 1.0}
        
        # 初始β系数（基于回归结果）
        self.initial_beta = {
            '科技政策': {'电子': 1.2, '计算机': 0.5, '通信': 0.5},
            '算力政策': {'电子': 1.2, '计算机': 0.5, '通信': 0.5},
            '新能源政策': {'电力设备': 0.8, '小金属': 1.0, '能源金属': 1.0, '电池': 0.8},
            '货币政策': {'银行': 0.3, '证券': 0.5},
            '房地产政策': {'房地产': 0.6},
        }
        
        # 核心模块
        self.rolling_calibrator = RollingCalibrator()
        self.weekend_processor = WeekendNewsProcessor()
        self.diminishing_tracker = DiminishingReturnsTracker()
        self.beta_learner = AutoBetaLearner()
        self.correction_learner = AutoCorrectionLearner()
        
        # 资金参数
        self.capital_params = {'friction_cost': 0.88}
        self.retail_ratio = {s: 0.6 for s in self.sectors}
        self.sector_vulnerability = {s: 0.4 for s in self.sectors}
        self.macro_sensitivity = {s: 0.3 for s in self.sectors}
    
    def get_beta(self, event_type, sector):
        """获取β系数"""
        default = self.initial_beta.get(event_type, {}).get(sector, 0.3)
        return self.beta_learner.get_beta(event_type, sector, default)
    
    def calculate_event_score(self, event_type, strength, surprise, policy_level):
        level_factor = self.policy_levels.get(policy_level, 0.6)
        surprise_factor = self.surprise_factors.get(surprise, 1.0)
        driver_type = self.event_driver_map.get(event_type, 'A_直接政策')
        driver_factor = self.driver_types.get(driver_type, 0.9)
        return round(strength * surprise_factor * level_factor * driver_factor, 2)
    
    def predict(self, events, northbound_flow=None, target_date=None,
                market_breadth=None, prev_day_returns=None):
        """执行预测"""
        is_monday = target_date and target_date.weekday() == 0
        
        if is_monday:
            up_beta, down_beta = 0.8, 1.2
            model_name = "周末模型"
        else:
            up_beta, down_beta = 1.0, 0.5
            model_name = "周内模型"
        
        # 处理事件
        processed_events = self.weekend_processor.process_weekend_news(events, target_date or datetime.now())
        
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
            if abs(total) > 0.03:
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
            if max_gain > 3.0:
                correction_factor = self.correction_learner.get_factor(max_gain, 0.5, market_breadth or 0.5, 0)
                for s in sector_impacts:
                    if s in ['半导体及元件', '计算机应用', '通信设备']:
                        sector_impacts[s] *= correction_factor
        
        # 正负分离
        positive = {s: v for s, v in sector_impacts.items() if v > 0}
        negative = {s: v for s, v in sector_impacts.items() if v < 0}
        
        # 行为修正
        for s, v in positive.items():
            retail = self.retail_ratio.get(s, 0.6)
            positive[s] = round(v * (1 + retail * 0.2), 2)
        
        # 格式化为输出
        ths_gainers = []
        for s, v in sorted(positive.items(), key=lambda x: x[1], reverse=True)[:15]:
            ths_gainers.append({'sector': s, 'prediction': round(v, 2)})
        
        ths_losers = []
        for s, v in sorted(negative.items(), key=lambda x: x[1])[:10]:
            ths_losers.append({'sector': s, 'prediction': round(v, 2)})
        
        return {
            'top_gainers': ths_gainers,
            'top_losers': ths_losers,
            'positive_sectors': len(positive),
            'negative_sectors': len(negative),
            'macro_base': macro_base,
            'version': self.version,
            'model_name': model_name,
            'correction_factor': correction_factor
        }
    
    def after_prediction_update(self, event_type, sector, event_score, predicted_impact, actual_gain, date):
        """预测后自动学习"""
        self.beta_learner.auto_update(event_type, sector, event_score, predicted_impact, actual_gain, date)


# ========== 保存模型 ==========
def save_model():
    model = FinancialPredictorV2342()
    with open('V23.42_auto.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    print("=" * 60)
    print("✅ V23.42 真实模型已生成并保存")
    print("=" * 60)
    print(f"   版本: {model.version}")
    print(f"   板块数量: {len(model.sectors)}个")
    print(f"   文件: V23.42_auto.pkl")
    print("=" * 60)
    return model


if __name__ == "__main__":
    save_model()

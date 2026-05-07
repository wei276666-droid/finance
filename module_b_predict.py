def _v2344_predict(self, events, northbound_flow, market_breadth):
    """V23.44 预测逻辑"""
    # 计算事件强度
    tech_score = 0
    for event in events:
        if '科技' in event.get('event_type', '') or '算力' in event.get('event_type', ''):
            tech_score += event.get('strength', 3.0)
    
    # 基础涨幅
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
        'version': 'V23.44'
    }

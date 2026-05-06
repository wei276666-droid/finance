"""
module_a_news.py - 境外可用的新闻采集模块
使用yfinance（Yahoo Finance）获取新闻
"""

import yfinance as yf
from datetime import datetime
from typing import List, Dict


class UnifiedNewsCollector:
    def __init__(self):
        self.session = None
    
    def fetch_and_process(self) -> List[Dict]:
        """采集新闻并转换为事件格式"""
        events = []
        
        # 方案1：通过yfinance获取市场新闻
        try:
            # 获取S&P 500相关新闻作为市场参考
            market = yf.Ticker("^GSPC")
            news_list = market.news
            
            for item in news_list[:20]:
                event = self._parse_yfinance_news(item)
                if event:
                    events.append(event)
        except Exception as e:
            print(f"yfinance新闻获取失败: {e}")
        
        # 如果没获取到，返回备用模拟数据
        if not events:
            events = self._mock_events()
        
        return events
    
    def _parse_yfinance_news(self, item: dict) -> Dict:
        """解析yfinance新闻"""
        title = item.get('title', '')
        link = item.get('link', '')
        publisher = item.get('publisher', '')
        
        # 分类
        event_type = '其他'
        if any(kw in title for kw in ['科技', 'AI', '芯片', '半导体']):
            event_type = '科技政策'
        elif any(kw in title for kw in ['新能源', '光伏', '锂电']):
            event_type = '新能源政策'
        elif any(kw in title for kw in ['房地产', '楼市']):
            event_type = '房地产政策'
        elif any(kw in title for kw in ['央行', '降息', '通胀']):
            event_type = '货币政策'
        
        # 强度评估
        strength = 3.0
        if any(kw in title for kw in ['重磅', '重大', '突破']):
            strength = 4.0
        
        return {
            'event_type': event_type,
            'strength': strength,
            'surprise': '符合预期',
            'policy_level': '国际级',
            'description': title[:150],
            'source': publisher,
            'url': link
        }
    
    def _mock_events(self) -> List[Dict]:
        """备用模拟数据"""
        return [
            {'event_type': '科技政策', 'strength': 3.5, 'surprise': '超预期', 
             'policy_level': '国家级', 'description': 'AI产业发展持续推进'},
            {'event_type': '货币政策', 'strength': 3.0, 'surprise': '符合预期',
             'policy_level': '国家级', 'description': '美联储维持利率不变预期增强'},
        ]
    
    def get_market_data(self) -> Dict:
        """获取市场数据（通过yfinance）"""
        market_data = {
            'northbound_flow': 0,
            'market_breadth': 0.5,
            'sp500_change': 0,
            'nasdaq_change': 0
        }
        
        try:
            # 获取S&P 500
            sp500 = yf.Ticker("^GSPC")
            hist = sp500.history(period="2d")
            if len(hist) >= 2:
                prev_close = hist['Close'].iloc[-2]
                curr_close = hist['Close'].iloc[-1]
                market_data['sp500_change'] = (curr_close - prev_close) / prev_close * 100
            
            # 获取纳斯达克
            nasdaq = yf.Ticker("^IXIC")
            hist = nasdaq.history(period="2d")
            if len(hist) >= 2:
                prev_close = hist['Close'].iloc[-2]
                curr_close = hist['Close'].iloc[-1]
                market_data['nasdaq_change'] = (curr_close - prev_close) / prev_close * 100
        except:
            pass
        
        return market_data


# 测试代码
if __name__ == '__main__':
    collector = UnifiedNewsCollector()
    events = collector.fetch_and_process()
    print(f"获取到 {len(events)} 条新闻")
    for e in events[:3]:
        print(f"  - {e['description'][:60]}...")

"""
module_a_news.py - 使用 yfinance 获取新闻和市场数据
yfinance 在 Render 上已验证可用
"""

import yfinance as yf
from datetime import datetime
from typing import List, Dict


class UnifiedNewsCollector:
    """使用 yfinance 的新闻采集器"""
    
    def __init__(self):
        # 使用多个股票代码获取新闻
        self.tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMD', 'INTC']
    
    def fetch_and_process(self) -> List[Dict]:
        """获取新闻并转换为事件格式"""
        events = []
        
        for ticker in self.tickers:
            try:
                stock = yf.Ticker(ticker)
                news_list = stock.news
                
                for news in news_list[:3]:  # 每个股票取前3条
                    event = self._parse_news(news, ticker)
                    if event:
                        events.append(event)
            except Exception as e:
                print(f"获取 {ticker} 新闻失败: {e}")
                continue
        
        # 去重（基于标题）
        seen = set()
        unique_events = []
        for event in events:
            title = event.get('description', '')
            if title not in seen:
                seen.add(title)
                unique_events.append(event)
        
        # 如果没有获取到新闻，使用降级数据
        if not unique_events:
            print("使用降级新闻数据")
            return self._fallback_events()
        
        print(f"✅ 获取到 {len(unique_events)} 条新闻")
        return unique_events[:15]
    
    def _parse_news(self, news: Dict, ticker: str) -> Dict:
        """解析 yfinance 新闻为事件格式"""
        title = news.get('title', '')
        link = news.get('link', '')
        publisher = news.get('publisher', '')
        content = news.get('content', '')
        
        text = (title + content).lower()
        
        # 事件分类
        event_type = self._classify_event(text)
        if event_type == '其他':
            return None
        
        # 强度评估
        strength = self._assess_strength(text)
        
        return {
            'event_type': event_type,
            'strength': strength,
            'surprise': '符合预期',
            'policy_level': '国际级',
            'description': title[:150],
            'source': publisher,
            'url': link,
            'related_ticker': ticker
        }
    
    def _classify_event(self, text: str) -> str:
        """事件分类"""
        keywords = {
            '科技政策': ['tech', 'ai', '芯片', '半导体', '人工智能', 'algorithm', 'software', 'nvidia', 'amd'],
            '新能源政策': ['新能源', 'solar', 'wind', 'ev', '电动车', 'battery', '锂电', 'tesla'],
            '货币政策': ['fed', '央行', 'interest', '利率', '降息', '加息', 'inflation', 'federal'],
            '宏观数据': ['gdp', '就业', '失业', '财报', 'earnings', 'revenue', 'profit'],
            '地缘政治': ['war', 'conflict', '制裁', 'tariff', 'trade', '中东'],
        }
        
        for event_type, kw_list in keywords.items():
            for kw in kw_list:
                if kw in text:
                    return event_type
        return '科技政策'  # 默认分类
    
    def _assess_strength(self, text: str) -> float:
        """评估强度"""
        if any(kw in text for kw in ['重磅', '重大', '突破', '里程碑', 'surge', 'record high']):
            return 4.5
        if any(kw in text for kw in ['大涨', '飙升', '创新高', 'beat', 'exceed']):
            return 4.0
        if any(kw in text for kw in ['上涨', '利好', '提振', 'gain', 'rise']):
            return 3.5
        return 3.0
    
    def _fallback_events(self) -> List[Dict]:
        """降级新闻数据"""
        return [
            {
                'event_type': '科技政策',
                'strength': 4.0,
                'surprise': '超预期',
                'policy_level': '国家级',
                'description': '国常会研究推进人工智能产业发展'
            },
            {
                'event_type': '货币政策',
                'strength': 3.0,
                'surprise': '符合预期',
                'policy_level': '国家级',
                'description': '央行开展MLF操作保持流动性合理充裕'
            }
        ]
    
    def get_market_data(self) -> Dict:
        """获取市场数据"""
        market_data = {
            'northbound_flow': 50,
            'market_breadth': 0.55,
            'sp500_change': 0,
            'nasdaq_change': 0,
            'dji_change': 0
        }
        
        # 获取指数行情
        try:
            # 标普500
            sp500 = yf.Ticker("^GSPC")
            hist = sp500.history(period="2d")
            if len(hist) >= 2:
                prev_close = hist['Close'].iloc[-2]
                curr_close = hist['Close'].iloc[-1]
                market_data['sp500_change'] = round((curr_close - prev_close) / prev_close * 100, 2)
        except Exception as e:
            print(f"获取标普500失败: {e}")
        
        try:
            # 纳斯达克
            nasdaq = yf.Ticker("^IXIC")
            hist = nasdaq.history(period="2d")
            if len(hist) >= 2:
                prev_close = hist['Close'].iloc[-2]
                curr_close = hist['Close'].iloc[-1]
                market_data['nasdaq_change'] = round((curr_close - prev_close) / prev_close * 100, 2)
        except Exception as e:
            print(f"获取纳斯达克失败: {e}")
        
        return market_data


# 测试代码
if __name__ == "__main__":
    collector = UnifiedNewsCollector()
    events = collector.fetch_and_process()
    print(f"\n获取到 {len(events)} 条新闻事件")
    for e in events[:5]:
        print(f"  - {e['event_type']}: {e['description'][:60]}...")

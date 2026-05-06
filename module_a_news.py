"""
module_a_news.py - FCS API 新闻采集模块
支持新闻获取、指数行情、市场数据
"""

import requests
import os
from datetime import datetime
from typing import List, Dict, Optional


class FCSNewsCollector:
    """FCS API 新闻采集器"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 FCS API 客户端
        API Key 从环境变量获取，或直接传入
        """
        self.api_key = api_key or os.environ.get('FCS_API_KEY', 'mnYHRqd0uLgSjKcpMhhaRM')
        self.base_url = "https://api-v4.fcsapi.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        })
    
    def get_market_news(self, limit: int = 20) -> List[Dict]:
        """
        获取市场新闻
        端点: /news/global?access_key=KEY&limit=20
        """
        url = f"{self.base_url}/news/global"
        params = {
            'access_key': self.api_key,
            'limit': limit
        }
        
        try:
            response = self.session.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get('status'):
                    return data.get('response', [])
            return []
        except Exception as e:
            print(f"新闻获取失败: {e}")
            return []
    
    def get_company_news(self, symbol: str = "AAPL", limit: int = 10) -> List[Dict]:
        """
        获取个股新闻
        端点: /stock/news?symbol=AAPL&access_key=KEY&limit=10
        """
        url = f"{self.base_url}/stock/news"
        params = {
            'access_key': self.api_key,
            'symbol': symbol,
            'limit': limit
        }
        
        try:
            response = self.session.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get('status'):
                    return data.get('response', [])
            return []
        except Exception as e:
            print(f"个股新闻获取失败: {e}")
            return []
    
    def get_index_quote(self, symbol: str = "NASDAQ") -> Dict:
        """
        获取指数行情
        端点: /stock/indices/latest?symbol=NASDAQ&access_key=KEY
        """
        url = f"{self.base_url}/stock/indices/latest"
        params = {
            'access_key': self.api_key,
            'symbol': symbol
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') and data.get('response'):
                    return data['response'][0]
            return {}
        except Exception as e:
            print(f"指数行情获取失败: {e}")
            return {}
    
    def get_stock_quote(self, symbol: str = "AAPL") -> Dict:
        """
        获取个股实时行情
        端点: /stock/latest?symbol=AAPL&access_key=KEY
        """
        url = f"{self.base_url}/stock/latest"
        params = {
            'access_key': self.api_key,
            'symbol': symbol
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') and data.get('response'):
                    return data['response'][0]
            return {}
        except Exception as e:
            print(f"个股行情获取失败: {e}")
            return {}


class UnifiedNewsCollector:
    """统一新闻采集器 - 封装 FCS API"""
    
    def __init__(self):
        self.fcs = FCSNewsCollector()
    
    def fetch_and_process(self) -> List[Dict]:
        """
        采集新闻并转换为模型事件格式
        """
        events = []
        
        # 获取市场新闻
        news_list = self.fcs.get_market_news(limit=20)
        
        for news in news_list:
            event = self._parse_news(news)
            if event:
                events.append(event)
        
        # 如果没有获取到新闻，返回模拟数据
        if not events:
            events = self._fallback_events()
        
        return events
    
    def _parse_news(self, news: Dict) -> Optional[Dict]:
        """解析新闻为事件格式"""
        title = news.get('title', '')
        content = news.get('content', '')
        
        # 事件分类
        event_type = self._classify_event(title, content)
        if event_type == '其他':
            return None
        
        # 强度评估
        strength = self._assess_strength(title, content)
        
        return {
            'event_type': event_type,
            'strength': strength,
            'surprise': '符合预期',
            'policy_level': '国际级',
            'description': title[:100],
            'source': news.get('source', 'FCS API'),
            'url': news.get('url', '')
        }
    
    def _classify_event(self, title: str, content: str) -> str:
        """事件分类"""
        text = (title + content).lower()
        
        if any(kw in text for kw in ['tech', 'ai', '芯片', '半导体', '人工智能']):
            return '科技政策'
        if any(kw in text for kw in ['新能源', 'solar', 'wind', 'ev', '电动车']):
            return '新能源政策'
        if any(kw in text for kw in ['real estate', 'property', '房地产', '楼市']):
            return '房地产政策'
        if any(kw in text for kw in ['fed', '央行', 'interest', '利率', '降息']):
            return '货币政策'
        if any(kw in text for kw in ['oil', '石油', '原油', 'gas']):
            return '原油价格上涨'
        
        return '其他'
    
    def _assess_strength(self, title: str, content: str) -> float:
        """评估事件强度"""
        text = (title + content).lower()
        
        if any(kw in text for kw in ['重磅', '重大', '突破', '里程碑']):
            return 4.5
        if any(kw in text for kw in ['大涨', '飙升', '创新高']):
            return 4.0
        if any(kw in text for kw in ['上涨', '利好', '提振']):
            return 3.5
        return 3.0
    
    def _fallback_events(self) -> List[Dict]:
        """降级新闻（API失败时使用）"""
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
        """获取市场辅助数据（指数行情等）"""
        market_data = {
            'northbound_flow': 0,
            'market_breadth': 0.5,
            'sp500_change': 0,
            'nasdaq_change': 0
        }
        
        # 获取纳斯达克指数
        nasdaq = self.fcs.get_index_quote('NASDAQ')
        if nasdaq:
            try:
                cp = nasdaq.get('cp', '0%')
                market_data['nasdaq_change'] = float(cp.replace('%', ''))
            except:
                pass
        
        # 获取标普500
        sp500 = self.fcs.get_index_quote('SPX')
        if sp500:
            try:
                cp = sp500.get('cp', '0%')
                market_data['sp500_change'] = float(cp.replace('%', ''))
            except:
                pass
        
        return market_data

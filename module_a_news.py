"""
module_a_news.py - EODHD API 新闻采集模块
需要设置环境变量 EODHD_API_KEY
免费版：20次/天，足够个人使用
"""

import os
from typing import List, Dict
from datetime import datetime

try:
    from eodhd import APIClient
    EODHD_AVAILABLE = True
except ImportError:
    EODHD_AVAILABLE = False
    print("⚠️ eodhd 库未安装，请运行: pip install eodhd")


class UnifiedNewsCollector:
    def __init__(self):
        self.api_key = os.environ.get('EODHD_API_KEY', '')
        self.client = None
        
        if self.api_key and EODHD_AVAILABLE:
            try:
                # 初始化客户端
                self.client = APIClient(self.api_key)
                print("✅ EODHD API 客户端初始化成功")
            except Exception as e:
                print(f"⚠️ EODHD 初始化失败: {e}")
        else:
            if not self.api_key:
                print("⚠️ EODHD_API_KEY 未设置，使用模拟数据")
            elif not EODHD_AVAILABLE:
                print("⚠️ eodhd 库未安装，使用模拟数据")
    
    def fetch_and_process(self) -> List[Dict]:
        """获取新闻并转换为事件格式"""
        if not self.client:
            return self._fallback_events()
        
        events = []
        
        try:
            # 获取美国主要股票的新闻（使用多个美股代码）
            symbols = ['AAPL.US', 'MSFT.US', 'GOOGL.US', 'TSLA.US', 'NVDA.US']
            
            for symbol in symbols:
                try:
                    # EODHD 新闻 API
                    news_list = self.client.news(symbol, limit=3)
                    
                    for news in news_list:
                        event = self._parse_news(news, symbol)
                        if event:
                            events.append(event)
                except Exception as e:
                    print(f"获取 {symbol} 新闻失败: {e}")
                    continue
            
            # 去重
            seen_titles = set()
            unique_events = []
            for e in events:
                if e['description'] not in seen_titles:
                    seen_titles.add(e['description'])
                    unique_events.append(e)
            
            if unique_events:
                print(f"✅ EODHD: 获取到 {len(unique_events)} 条新闻")
                return unique_events[:15]
                
        except Exception as e:
            print(f"⚠️ EODHD 新闻获取失败: {e}")
        
        return self._fallback_events()
    
    def _parse_news(self, news: Dict, symbol: str) -> Dict:
        """解析新闻"""
        # EODHD 返回的新闻格式
        title = news.get('title', '')
        content = news.get('content', '')
        date = news.get('date', '')
        source = news.get('source', 'EODHD')
        
        text = (title + content).lower()
        
        # 事件分类
        event_type = self._classify_event(text)
        
        # 强度评估
        strength = self._assess_strength(text)
        
        # 惊喜程度
        surprise = '超预期' if any(kw in text for kw in ['beat', 'exceed', '超预期']) else '符合预期'
        
        return {
            'event_type': event_type,
            'strength': strength,
            'surprise': surprise,
            'policy_level': '国际级',
            'description': title[:150],
            'source': source,
            'date': date,
            'symbol': symbol
        }
    
    def _classify_event(self, text: str) -> str:
        """事件分类"""
        keywords = {
            '科技政策': ['tech', 'ai', '芯片', '半导体', '人工智能', 'nvidia', 'amd'],
            '新能源政策': ['新能源', 'solar', 'wind', 'ev', '电动车', 'battery', '锂电', 'tesla'],
            '货币政策': ['fed', '美联储', '央行', 'interest', '利率', '降息', '加息', '通胀'],
            '房地产政策': ['real estate', 'property', '房地产', '楼市', 'housing'],
            '宏观数据': ['gdp', '就业', '失业', '财报', 'earnings', 'revenue', 'profit'],
            '地缘政治': ['war', 'conflict', '制裁', 'tariff', 'trade', '中东'],
        }
        
        for event_type, kw_list in keywords.items():
            for kw in kw_list:
                if kw in text:
                    return event_type
        return '宏观数据'  # 默认分类
    
    def _assess_strength(self, text: str) -> float:
        """评估强度"""
        high_keywords = ['重磅', '重大', '突破', '里程碑', 'landmark', 'breakthrough']
        medium_keywords = ['大涨', '飙升', '创新高', 'surge', 'record', 'beat']
        low_keywords = ['上涨', '利好', '提振', 'gain', 'rise', 'positive']
        
        if any(kw in text for kw in high_keywords):
            return 4.5
        if any(kw in text for kw in medium_keywords):
            return 4.0
        if any(kw in text for kw in low_keywords):
            return 3.5
        return 3.0
    
    def _fallback_events(self) -> List[Dict]:
        """降级数据（API失败时使用）"""
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
        return {
            'northbound_flow': 50,
            'market_breadth': 0.55,
            'up_count': 2800,
            'down_count': 2400
        }

"""
module_a_news.py - FCS API 新闻采集模块（修正版）
"""

import requests
import os
import json
from datetime import datetime
from typing import List, Dict, Optional


class FCSNewsCollector:
    """FCS API 新闻采集器 - 修正版"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 FCS API 客户端
        """
        # 支持环境变量和直接传入
        self.api_key = api_key or os.environ.get('FCS_API_KEY', 'rkpZZVOkIH7GIzBUZmu9HWmKx7dYP')
        self.base_url = "https://api.fcsapi.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        })
        
        # 调试信息
        print(f"FCS API Key 长度: {len(self.api_key) if self.api_key else 0}")
        print(f"FCS API Key 是否为空: {self.api_key == ''}")
    
    def test_connection(self) -> bool:
        """测试 API 连接"""
        if not self.api_key:
            print("❌ API Key 未设置")
            return False
        
        # 尝试多个端点
        endpoints = [
            f"{self.base_url}/v1/news",
            f"{self.base_url}/v1/news/global",
            f"{self.base_url}/news/global",
        ]
        
        for url in endpoints:
            params = {
                'access_key': self.api_key,
                'limit': 1,
                'format': 'json'
            }
            
            try:
                print(f"尝试连接: {url}")
                response = self.session.get(url, params=params, timeout=10)
                print(f"状态码: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"响应: {json.dumps(data, ensure_ascii=False)[:200]}")
                    if data.get('status') or data.get('code') == 200:
                        print(f"✅ API 连接成功: {url}")
                        return True
                    else:
                        print(f"⚠️ API 返回错误: {data}")
                else:
                    print(f"❌ HTTP 错误: {response.status_code}")
            except Exception as e:
                print(f"❌ 连接失败: {e}")
        
        return False
    
    def get_global_news(self, limit: int = 20) -> List[Dict]:
        """获取全球市场新闻"""
        if not self.api_key:
            print("⚠️ API Key 未设置，使用降级数据")
            return []
        
        # 使用正确的端点
        url = f"{self.base_url}/v1/news"
        
        params = {
            'access_key': self.api_key,
            'limit': limit,
            'format': 'json'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=15)
            print(f"新闻请求状态: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"新闻响应: {json.dumps(data, ensure_ascii=False)[:300]}")
                
                # 处理不同响应格式
                if data.get('status') or data.get('code') == 200:
                    news_data = data.get('response', data.get('data', []))
                    if news_data:
                        print(f"✅ 获取到 {len(news_data)} 条新闻")
                        return news_data
                else:
                    print(f"⚠️ API 错误: {data.get('message', '未知错误')}")
            else:
                print(f"❌ HTTP 错误: {response.status_code}")
        except Exception as e:
            print(f"❌ 新闻获取异常: {e}")
        
        return []


class UnifiedNewsCollector:
    """统一新闻采集器"""
    
    def __init__(self):
        self.fcs = FCSNewsCollector()
        # 测试连接
        self.api_available = self.fcs.test_connection()
    
    def fetch_and_process(self) -> List[Dict]:
        """采集新闻并转换为事件格式"""
        
        # 如果 API 可用，尝试获取真实新闻
        if self.api_available:
            news_list = self.fcs.get_global_news(limit=20)
            if news_list:
                events = []
                for news in news_list:
                    event = self._parse_news(news)
                    if event:
                        events.append(event)
                if events:
                    print(f"✅ 使用真实新闻，共 {len(events)} 条事件")
                    return events
        
        # 降级：使用模拟数据
        print("⚠️ 使用降级新闻数据")
        return self._fallback_events()
    
    def _parse_news(self, news: Dict) -> Optional[Dict]:
        """解析新闻为事件格式"""
        title = news.get('title', '')
        content = news.get('content', '') or news.get('description', '')
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
            'description': title[:100],
            'source': news.get('source', 'FCS API'),
            'url': news.get('url', '')
        }
    
    def _classify_event(self, text: str) -> str:
        """事件分类"""
        keywords = {
            '科技政策': ['tech', 'ai', '芯片', '半导体', '人工智能', 'algorithm', 'software'],
            '新能源政策': ['新能源', 'solar', 'wind', 'ev', '电动车', 'battery', '锂电'],
            '房地产政策': ['real estate', 'property', '房地产', '楼市', 'housing'],
            '货币政策': ['fed', '央行', 'interest', '利率', '降息', '加息', 'inflation'],
            '原油价格上涨': ['oil', '石油', '原油', 'gas', '能源'],
            '宏观数据': ['gdp', '就业', '失业', '财报', 'earnings'],
        }
        
        for event_type, kw_list in keywords.items():
            for kw in kw_list:
                if kw in text:
                    return event_type
        return '其他'
    
    def _assess_strength(self, text: str) -> float:
        """评估强度"""
        if any(kw in text for kw in ['重磅', '重大', '突破', '里程碑', 'landmark']):
            return 4.5
        if any(kw in text for kw in ['大涨', '飙升', '创新高', 'surge', 'record']):
            return 4.0
        if any(kw in text for kw in ['上涨', '利好', '提振', 'boost', 'rally']):
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
            },
            {
                'event_type': '房地产政策',
                'strength': 2.5,
                'surprise': '符合预期',
                'policy_level': '部委级',
                'description': '多地优化房地产调控政策'
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


# 测试代码
if __name__ == "__main__":
    collector = UnifiedNewsCollector()
    events = collector.fetch_and_process()
    print(f"\n最终获取 {len(events)} 条事件")
    for e in events[:3]:
        print(f"  - {e['event_type']}: {e['description'][:50]}...")

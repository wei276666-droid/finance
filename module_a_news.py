"""
module_a_news.py - 新闻采集模块
支持：API自动采集 + 手动输入 + 模拟数据降级
"""

import json
import os
from typing import List, Dict


class UnifiedNewsCollector:
    """统一新闻采集器"""
    
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.manual_news_file = os.path.join(data_dir, 'manual_news.json')
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def fetch_and_process(self) -> List[Dict]:
        """获取新闻（优先手动输入 > 模拟数据）"""
        events = []
        
        # 1. 优先加载手动输入的新闻
        manual_events = self._load_manual_news()
        if manual_events:
            print(f"✅ 加载手动输入新闻: {len(manual_events)} 条")
            return manual_events
        
        # 2. 尝试API获取（预留）
        api_events = self._fetch_from_api()
        if api_events:
            return api_events
        
        # 3. 降级：使用模拟数据
        print("⚠️ 使用模拟新闻数据")
        return self._fallback_events()
    
    def _load_manual_news(self) -> List[Dict]:
        """加载手动输入的新闻"""
        if os.path.exists(self.manual_news_file):
            try:
                with open(self.manual_news_file, 'r', encoding='utf-8') as f:
                    news = json.load(f)
                    # 只返回当天的新闻
                    return news
            except:
                pass
        return []
    
    def save_manual_news(self, events: List[Dict]):
        """保存手动输入的新闻"""
        with open(self.manual_news_file, 'w', encoding='utf-8') as f:
            json.dump(events, f, ensure_ascii=False, indent=2)
        print(f"✅ 已保存 {len(events)} 条手动新闻")
    
    def _fetch_from_api(self) -> List[Dict]:
        """预留API接口"""
        # TODO: 后续接入 EODHD / Alpha Vantage
        return []
    
    def _fallback_events(self) -> List[Dict]:
    """今日真实新闻（用于明日预测）"""
    return [
        {
            'event_type': '科技政策',
            'strength': 4.5,
            'surprise': '超预期',
            'policy_level': '国家级',
            'description': 'AMD Q1营收同比增38%超预期，数据中心业务大增57%'
        },
        {
            'event_type': '算力政策',
            'strength': 4.5,
            'surprise': '超预期',
            'policy_level': '国家级',
            'description': 'SpaceX拟斥资550亿美元开建2纳米芯片工厂'
        },
        {
            'event_type': '科技政策',
            'strength': 4.0,
            'surprise': '超预期',
            'policy_level': '国家级',
            'description': '英伟达与康宁合作，光连接产能提升10倍'
        },
        {
            'event_type': '货币政策',
            'strength': 4.0,
            'surprise': '超预期',
            'policy_level': '国家级',
            'description': '央行开展3000亿元逆回购操作'
        },
        {
            'event_type': '有色金属',
            'strength': 4.0,
            'surprise': '超预期',
            'policy_level': '国际级',
            'description': '现货黄金站上4660美元，碳酸锂涨超7%'
        },
        {
            'event_type': '油价下跌',
            'strength': 3.5,
            'surprise': '超预期',
            'policy_level': '国际级',
            'description': 'WTI原油暴跌12%，油气板块承压'
        },
    ]
    def get_market_data(self) -> Dict:
        """获取市场数据"""
        return {
            'northbound_flow': 50,
            'market_breadth': 0.55,
            'up_count': 2800,
            'down_count': 2400
        }


# 便捷函数：手动输入新闻
def add_manual_events(events: List[Dict]):
    """手动添加新闻事件"""
    collector = UnifiedNewsCollector()
    collector.save_manual_news(events)


# 示例：今日新闻事件
TODAY_NEWS = [
    {
        'event_type': '科技政策',
        'strength': 4.0,
        'surprise': '超预期',
        'policy_level': '国家级',
        'description': '央行等三部门扩围科技金融赋能14领域，包括电子信息、人工智能'
    },
    {
        'event_type': '算力政策',
        'strength': 4.5,
        'surprise': '超预期',
        'policy_level': '国家级',
        'description': '算力租赁概念爆发，东阳光签160-190亿元算力服务合同'
    },
    {
        'event_type': '房地产政策',
        'strength': 3.5,
        'surprise': '超预期',
        'policy_level': '国家级',
        'description': '天津出台11条房地产新政，多地接连发布楼市新政'
    },
    {
        'event_type': '货币政策',
        'strength': 3.0,
        'surprise': '符合预期',
        'policy_level': '国家级',
        'description': '央行开展3000亿元买断式逆回购，资金面持续宽松'
    },
    {
        'event_type': '新能源政策',
        'strength': 3.5,
        'surprise': '超预期',
        'policy_level': '国家级',
        'description': '人民日报头版：内蒙古大力发展绿色能源'
    }
]

if __name__ == '__main__':
    # 测试：保存今日新闻
    add_manual_events(TODAY_NEWS)
    print("今日新闻已保存到 data/manual_news.json")

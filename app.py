"""
app.py - Flask Web应用主程序
"""

import json
import os
from datetime import datetime
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

from module_a_news import UnifiedNewsCollector
from module_b_predict import PredictEngine

app = Flask(__name__)
CORS(app)

# 初始化模块
news_collector = UnifiedNewsCollector()
predict_engine = PredictEngine()

# 数据目录
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

HISTORY_FILE = os.path.join(DATA_DIR, 'predictions_history.json')


def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return []


def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history[-500:], f, indent=2)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/predict', methods=['GET'])
def get_predictions():
    """获取预测结果"""
    try:
        # 1. 采集新闻
        events = news_collector.fetch_and_process()
        
        # 2. 获取市场数据
        market_data = news_collector.get_market_data()
        
        # 3. 执行预测
        predictions = predict_engine.predict(
            events=events,
            northbound_flow=market_data.get('northbound_flow'),
            market_breadth=market_data.get('market_breadth')
        )
        
        # 4. 记录预测历史
        today = datetime.now().strftime('%Y-%m-%d')
        history = load_history()
        history.append({
            'date': today,
            'timestamp': datetime.now().isoformat(),
            'events': [{'type': e.get('event_type'), 'strength': e.get('strength')} for e in events[:5]],
            'predictions': predictions.get('top_gainers', [])[:10],
            'losers': predictions.get('top_losers', [])[:5]
        })
        save_history(history)
        
        return jsonify({
            'code': 0,
            'data': {
                'top_gainers': predictions.get('top_gainers', [])[:10],
                'top_losers': predictions.get('top_losers', [])[:5],
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'summary': {
                    'positive_count': predictions.get('positive_sectors', 0),
                    'negative_count': predictions.get('negative_sectors', 0),
                    'macro_base': predictions.get('macro_base', 0),
                    'event_count': len(events)
                }
            }
        })
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/news/manual', methods=['POST'])
def add_manual_news():
    """手动添加新闻事件（收盘后使用）"""
    try:
        data = request.get_json()
        events = data.get('events', [])
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        if not events:
            return jsonify({'code': -1, 'message': 'events required'}), 400
        
        # 保存手动新闻
        news_collector.save_manual_news(events)
        
        # 记录到预测历史
        history = load_history()
        history.append({
            'date': date,
            'timestamp': datetime.now().isoformat(),
            'events': events,
            'is_manual': True
        })
        save_history(history)
        
        return jsonify({'code': 0, 'message': f'已添加 {len(events)} 条新闻', 'date': date})
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/learn', methods=['POST'])
def learn_from_actual():
    """学习API - 记录实际数据"""
    try:
        data = request.get_json()
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        actual_returns = data.get('actual_returns', {})
        
        if not actual_returns:
            return jsonify({'code': -1, 'message': 'actual_returns required'}), 400
        
        actual_file = os.path.join(DATA_DIR, 'daily_actual.json')
        if os.path.exists(actual_file):
            with open(actual_file, 'r') as f:
                actual_data = json.load(f)
        else:
            actual_data = {}
        
        actual_data[date] = actual_returns
        
        with open(actual_file, 'w') as f:
            json.dump(actual_data, f, indent=2)
        
        # 更新预测历史
        history = load_history()
        for record in history:
            if record.get('date') == date:
                record['actual'] = actual_returns
                break
        save_history(history)
        
        return jsonify({'code': 0, 'message': f'已保存 {date} 的实际数据'})
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/news/current', methods=['GET'])
def get_current_news():
    """获取当前使用的新闻"""
    events = news_collector.fetch_and_process()
    return jsonify({'code': 0, 'events': events})


@app.route('/api/stats', methods=['GET'])
def get_stats():
    history = load_history()
    return jsonify({
        'code': 0,
        'data': {
            'prediction_count': len(history),
            'status': 'ok'
        }
    })


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'version': 'V23.42'
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

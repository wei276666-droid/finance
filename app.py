"""
app.py - 逐步添加功能
"""

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from datetime import datetime
import json
import os

# 导入您的模块
from module_a_news import UnifiedNewsCollector
from module_b_predict import PredictEngine

app = Flask(__name__)
CORS(app)

# 初始化
news_collector = UnifiedNewsCollector()
predict_engine = PredictEngine()
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


@app.route('/')
def index():
    """返回前端页面"""
    try:
        return render_template('index.html')
    except:
        return jsonify({'status': 'ok', 'message': 'Financial Predictor API'})


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})


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
        
        return jsonify({
            'code': 0,
            'data': {
                'top_gainers': predictions.get('top_gainers', [])[:10],
                'top_losers': predictions.get('top_losers', [])[:5],
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'summary': {
                    'positive_count': predictions.get('positive_sectors', 0),
                    'negative_count': predictions.get('negative_sectors', 0),
                    'macro_base': predictions.get('macro_base', 0)
                }
            }
        })
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
        
        return jsonify({'code': 0, 'message': f'已保存 {date} 的实际数据'})
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

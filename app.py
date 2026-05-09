import json
import os
import requests
from datetime import datetime
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

# 导入你的模块
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

# ================== 页面 ==================
@app.route('/')
def index():
    return render_template('index.html')

# ================== 预测 API ==================
@app.route('/api/predict', methods=['GET'])
def get_predictions():
    try:
        events = news_collector.fetch_and_process()
        market_data = news_collector.get_market_data()
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
                    'macro_base': predictions.get('macro_base', 0),
                }
            }
        })
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)}), 500

# ================== 学习 API ==================
@app.route('/api/learn', methods=['POST'])
def learn_from_actual():
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

        # 【关键修复】调用模型的自动学习方法
        for sector, gain in actual_returns.items():
            if predict_engine.model and hasattr(predict_engine.model, 'after_prediction_update'):
                # 这里简单关联到第一个事件（可根据需要优化）
                event_type = '科技政策' if gain > 0 else '银行利空'
                predict_engine.model.after_prediction_update(
                    event_type=event_type,
                    sector=sector,
                    event_score=4.0,
                    predicted_impact=0,
                    actual_gain=gain,
                    date=datetime.strptime(date, '%Y-%m-%d')
                )

        # 保存模型
        with open('V23.44_fusion.pkl', 'wb') as f:
            pickle.dump(predict_engine.model, f)

        return jsonify({'code': 0, 'message': f'已保存 {date} 的实际数据并更新模型'})
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)}), 500

# ================== 健康检查 ==================
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

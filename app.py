
"""
app.py - 最小化版本
"""

from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)  # 必须叫 app
CORS(app)


@app.route('/')
def index():
    return jsonify({'status': 'ok', 'message': 'Financial Predictor API'})


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})


@app.route('/api/predict', methods=['GET'])
def get_predictions():
    return jsonify({
        'code': 0,
        'data': {
            'top_gainers': [
                {'sector': '半导体及元件', 'prediction': 4.50},
                {'sector': '通信设备', 'prediction': 3.80},
                {'sector': '计算机应用', 'prediction': 3.20},
            ],
            'top_losers': [
                {'sector': '煤炭开采加工', 'prediction': -3.50},
            ],
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'summary': {
                'positive_count': 3,
                'negative_count': 1,
                'macro_base': 0.02
            }
        }
    })


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

from flask import Flask, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/predict', methods=['GET'])
def get_predictions():
    return jsonify({
        'code': 0,
        'data': {
            'top_gainers': [
                {'sector': '半导体及元件', 'prediction': 2.50},
                {'sector': '计算机应用', 'prediction': 1.80},
                {'sector': '通信设备', 'prediction': 1.20},
            ],
            'top_losers': [
                {'sector': '房地产开发', 'prediction': -0.80},
            ],
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'summary': {'positive_count': 3, 'negative_count': 1, 'macro_base': 0.02}
        }
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

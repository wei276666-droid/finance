"""
app.py - Flask Web应用主程序
"""

import json
import os
from datetime import datetime
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
    weekday = datetime.now().weekday()
    is_monday = weekday == 0
    
    if is_monday:
        tech_base = 2.0
    else:
        tech_base = 1.5
    
    predictions_data = {
        'top_gainers': [
            {'sector': '半导体及元件', 'prediction': round(tech_base + 0.5, 2)},
            {'sector': '计算机应用', 'prediction': round(tech_base + 0.2, 2)},
            {'sector': '通信设备', 'prediction': round(tech_base, 2)},
            {'sector': '电力设备', 'prediction': round(tech_base - 0.3, 2)},
            {'sector': '房地产开发', 'prediction': round(tech_base - 0.5, 2)},
        ],
        'top_losers': [
            {'sector': '银行', 'prediction': -0.5},
            {'sector': '石油石化', 'prediction': -0.3},
        ],
        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'summary': {
            'positive_count': 5,
            'negative_count': 2,
            'macro_base': 0.02
        }
    }
    
    # 记录预测历史
    history = load_history()
    history.append({
        'date': datetime.now().strftime('%Y-%m-%d'),
        'timestamp': datetime.now().isoformat(),
        'predictions': predictions_data['top_gainers']
    })
    save_history(history)
    
    return jsonify({'code': 0, 'data': predictions_data})


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
        
        return jsonify({'code': 0, 'message': f'已保存 {date} 的实际数据'})
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)}), 500


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
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

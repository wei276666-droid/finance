"""
app.py - Flask Web应用主程序
提供预测API、学习API、前端页面
"""

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from datetime import datetime
import os

from module_a_news import UnifiedNewsCollector
from module_b_predict import PredictEngine
from auto_learner import AutoLearner

app = Flask(__name__)
CORS(app)

# 初始化模块
news_collector = UnifiedNewsCollector()
predict_engine = PredictEngine()
auto_learner = AutoLearner()


# ========== 页面 ==========
@app.route('/')
def index():
    """返回前端页面"""
    return render_template('index.html')


# ========== 预测API ==========
@app.route('/api/predict', methods=['GET'])
def get_predictions():
    """获取预测结果"""
    try:
        # 1. 采集新闻
        events = news_collector.fetch_and_process()
        
        # 2. 获取市场数据
        market_data = news_collector.get_market_data()
        
        # 3. 获取前日实际数据（用于回调检测）
        today = datetime.now().strftime('%Y-%m-%d')
        prev_returns = auto_learner.get_prev_day_returns(today)
        
        # 4. 执行预测
        predictions = predict_engine.predict(
            events=events,
            northbound_flow=market_data.get('northbound_flow'),
            market_breadth=market_data.get('market_breadth'),
            prev_day_returns=prev_returns
        )
        
        # 5. 记录预测（供收盘学习使用）
        auto_learner.record_prediction(
            date=today,
            events=events,
            predictions=predictions
        )
        
        # 6. 返回结果
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': {
                'top_gainers': predictions.get('top_gainers', [])[:10],
                'top_losers': predictions.get('top_losers', [])[:5],
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'summary': {
                    'positive_count': predictions.get('positive_sectors', 0),
                    'negative_count': predictions.get('negative_sectors', 0),
                    'macro_base': predictions.get('macro_base', 0),
                    'event_count': predictions.get('event_count', 0)
                }
            }
        })
        
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)}), 500


# ========== 学习API（收盘后调用） ==========
@app.route('/api/learn', methods=['POST'])
def learn_from_actual():
    """收盘后学习API - 用实际数据更新模型"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'code': -1, 'message': '请提供JSON数据'}), 400
        
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        actual_returns = data.get('actual_returns', {})
        
        if not actual_returns:
            return jsonify({'code': -1, 'message': 'actual_returns 不能为空'}), 400
        
        success = auto_learner.learn_from_actual(date, actual_returns)
        
        if success:
            return jsonify({
                'code': 0,
                'message': '学习完成，模型已更新',
                'date': date
            })
        else:
            return jsonify({
                'code': -1,
                'message': f'未找到 {date} 的预测记录，请确保当天先调用过预测API'
            }), 404
            
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)}), 500


# ========== 统计API ==========
@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取模型统计信息"""
    try:
        stats = auto_learner.get_model_stats()
        return jsonify({
            'code': 0,
            'data': stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)}), 500


# ========== 健康检查 ==========
@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'version': 'V23.42'
    })


# ========== 手动触发学习（用于测试） ==========
@app.route('/api/learn/manual', methods=['POST'])
def manual_learn():
    """手动触发学习（测试用）"""
    try:
        data = request.get_json()
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        actual_returns = data.get('actual_returns', {})
        
        if not actual_returns:
            return jsonify({'code': -1, 'message': '请提供 actual_returns'}), 400
        
        # 直接学习，不检查预测记录
        learner = AutoLearner()
        learner._save_actual_data(date, actual_returns)
        
        return jsonify({
            'code': 0,
            'message': f'已保存 {date} 的实际数据',
            'date': date
        })
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)}), 500


if __name__ == '__main__':
    # 生产环境使用 gunicorn，不需要运行
    # 本地测试用
    app.run(host='0.0.0.0', port=5000, debug=False)

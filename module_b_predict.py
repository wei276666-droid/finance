"""
app.py - Flask主程序
"""

from flask import Flask, jsonify, render_template
from flask_cors import CORS
from datetime import datetime

from module_a_news import UnifiedNewsCollector
from module_b_predict import PredictEngine

app = Flask(__name__)
CORS(app)

news_collector = UnifiedNewsCollector()
predict_engine = PredictEngine()


@app.route('/')
def index():
    return render_template('index.html')


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
            'message': 'success',
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


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

"""
app.py - 添加自动学习接口
"""

import json
import os
import requests
from datetime import datetime
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

# ... 原有代码 ...

@app.route('/api/auto_learn', methods=['GET'])
def auto_learn():
    """
    自动学习接口 - 供 cron-job.org 调用
    自动获取今日实际数据并执行学习
    """
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 1. 获取今日实际涨跌数据
    actual_returns = fetch_actual_returns()
    
    if not actual_returns:
        return jsonify({'code': -1, 'message': f'未获取到{today}的实际数据'})
    
    # 2. 调用内部学习接口
    try:
        response = requests.post(
            'http://localhost:5000/api/learn',
            json={'date': today, 'actual_returns': actual_returns},
            timeout=30
        )
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)})


def fetch_actual_returns():
    """
    获取今日实际板块涨跌数据
    方案：从 data/daily_actual.json 读取（您每天手动更新）
    """
    data_file = os.path.join('data', 'daily_actual.json')
    today = datetime.now().strftime('%Y-%m-%d')
    
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
                return all_data.get(today, {})
        except:
            pass
    
    return {}


# 可选：添加手动更新实际数据的接口
@app.route('/api/update_actual', methods=['POST'])
def update_actual():
    """手动更新今日实际数据"""
    try:
        data = request.get_json()
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        actual_returns = data.get('actual_returns', {})
        
        if not actual_returns:
            return jsonify({'code': -1, 'message': 'actual_returns required'}), 400
        
        data_file = os.path.join('data', 'daily_actual.json')
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
        else:
            all_data = {}
        
        all_data[date] = actual_returns
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        return jsonify({'code': 0, 'message': f'已保存 {date} 的实际数据'})
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)}), 500

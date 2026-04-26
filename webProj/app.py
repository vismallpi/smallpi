from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import pytz

# 设置时区为北京时间
beijing_tz = pytz.timezone('Asia/Shanghai')

app = Flask(__name__)

# 初始化数据库
def init_db():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            text TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            priority TEXT DEFAULT 'medium',
            date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # 尝试添加 created_at 列，如果已经存在会报错，忽略
    try:
        cursor.execute('ALTER TABLE tasks ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
    except:
        pass
    # 尝试添加 priority 列，如果已经存在会报错，忽略
    try:
        cursor.execute("ALTER TABLE tasks ADD COLUMN priority TEXT DEFAULT 'medium'")
    except:
        pass
    conn.commit()
    conn.close()

init_db()

# 获取所有任务
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, text, completed, priority, date, created_at FROM tasks ORDER BY created_at DESC')
    tasks = cursor.fetchall()
    conn.close()
    
    result = []
    for task in tasks:
        result.append({
            'id': task[0],
            'text': task[1],
            'completed': bool(task[2]),
            'priority': task[3] or 'medium',
            'date': task[4],
            'created_at': task[5]
        })
    return jsonify(result)

# 添加新任务
@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    now = datetime.now(beijing_tz)
    task = {
        'id': str(int(now.timestamp() * 1000)),
        'text': data['text'],
        'completed': False,
        'priority': 'medium',
        'date': now.isoformat().split('T')[0],
        'created_at': now.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO tasks (id, text, completed, priority, date, created_at) VALUES (?, ?, ?, ?, ?, ?)',
        (task['id'], task['text'], int(task['completed']), task['priority'], task['date'], task['created_at'])
    )
    conn.commit()
    conn.close()
    
    return jsonify(task)

# 切换任务完成状态
@app.route('/api/tasks/<task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT completed FROM tasks WHERE id = ?', (task_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return jsonify({'error': 'Task not found'}), 404
    
    new_completed = 1 - result[0]
    cursor.execute('UPDATE tasks SET completed = ? WHERE id = ?', (new_completed, task_id))
    conn.commit()
    conn.close()
    
    return jsonify({'id': task_id, 'completed': bool(new_completed)})

# 删除任务
@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    
    return jsonify({'success': deleted})

# 更新任务文字
@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    text = data.get('text')
    
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE tasks SET text = ? WHERE id = ?', (text, task_id))
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    
    return jsonify({'success': updated, 'id': task_id, 'text': text})

# 更新任务优先级
@app.route('/api/tasks/<task_id>/priority', methods=['PUT'])
def update_task_priority(task_id):
    data = request.get_json()
    priority = data.get('priority')
    
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE tasks SET priority = ? WHERE id = ?', (priority, task_id))
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    
    return jsonify({'success': updated, 'id': task_id, 'priority': priority})

# 飞书语音识别API
@app.route('/api/recognize', methods=['POST'])
def recognize_speech():
    import os
    import requests
    
    # 飞书开发者凭证
    FEISHU_APP_ID = "cli_a9481491f1f89cc5"
    FEISHU_APP_SECRET = "kvurwkY09mOSWJgzhEwr0bjcY5PxkXIw"
    
    # 获取飞书tenant_access_token
    token_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    token_response = requests.post(
        token_url,
        json={
            "app_id": FEISHU_APP_ID,
            "app_secret": FEISHU_APP_SECRET
        }
    )
    
    try:
        token_data = token_response.json()
    except:
        return jsonify({
            'success': False,
            'error': f"获取飞书token失败，响应不是JSON: {token_response.text}"
        })
    
    if token_data.get('code') != 0:
        return jsonify({
            'success': False,
            'error': f"获取飞书token失败: {token_data.get('msg')}"
        })
    
    access_token = token_data['tenant_access_token']
    
    # 直接读取请求body中的二进制音频数据
    audio_data = request.get_data()
    
    if len(audio_data) == 0:
        return jsonify({'success': False, 'error': '音频数据为空'})
    
    # 调用飞书语音识别API - 直接发送二进制数据，符合飞书要求
    recognize_url = "https://open.feishu.cn/open-apis/asr/v1/recognize"
    content_type = request.headers.get('Content-Type', 'audio/wav')
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': content_type
    }
    
    recognize_response = requests.post(
        recognize_url,
        headers=headers,
        data=audio_data
    )
    
    try:
        recognize_data = recognize_response.json()
    except:
        return jsonify({
            'success': False,
            'error': f"飞书API返回非JSON响应: {recognize_response.text}"
        })
    
    if recognize_data.get('code') != 0:
        return jsonify({
            'success': False,
            'error': f"语音识别失败: {recognize_data.get('msg')} (code: {recognize_data.get('code')})"
        })
    
    # 返回识别结果
    return jsonify({
        'success': True,
        'text': recognize_data.get('text', '')
    })

# 静态文件 - 待办清单
@app.route('/')
@app.route('/notion-style-todo.html')
def index():
    return open('notion-style-todo.html', 'r', encoding='utf-8').read()

# 商务英语词汇背单词网站
@app.route('/vocab')
@app.route('/vocab.html')
@app.route('/business-vocab')
def vocab():
    return open('vocab.html', 'r', encoding='utf-8').read()

# ====================
# 页面标题存储（后端存储）
# ====================
@app.route('/api/page-title', methods=['GET'])
def get_page_title():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    # 创建表如果不存在
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS page_config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')
    cursor.execute('SELECT value FROM page_config WHERE key = ?', ('page_title',))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return jsonify({'success': True, 'title': result[0]})
    else:
        return jsonify({'success': True, 'title': 'Tasks'})

@app.route('/api/page-title', methods=['POST'])
def save_page_title():
    data = request.get_json()
    title = data.get('title', 'Tasks')
    
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS page_config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')
    # 插入或替换
    cursor.execute('''
        REPLACE INTO page_config (key, value) VALUES (?, ?)
    ''', ('page_title', title))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

if __name__ == '__main__':
    # 同时启用 HTTP (8081) 和 HTTPS (8080)
    import threading
    def run_http():
        app.run(host='0.0.0.0', port=8081, debug=False)
    threading.Thread(target=run_http, daemon=True).start()
    # 启用HTTPS，使用自签名证书
    app.run(host='0.0.0.0', port=8080, debug=False, ssl_context=('cert.pem', 'key.pem'))

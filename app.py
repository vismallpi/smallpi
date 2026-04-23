from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

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
            date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # 尝试添加 created_at 列，如果已经存在会报错，忽略
    try:
        cursor.execute('ALTER TABLE tasks ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
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
    cursor.execute('SELECT id, text, completed, date, created_at FROM tasks ORDER BY created_at DESC')
    tasks = cursor.fetchall()
    conn.close()
    
    result = []
    for task in tasks:
        result.append({
            'id': task[0],
            'text': task[1],
            'completed': bool(task[2]),
            'date': task[3],
            'created_at': task[4]
        })
    return jsonify(result)

# 添加新任务
@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    task = {
        'id': str(int(datetime.now().timestamp() * 1000)),
        'text': data['text'],
        'completed': False,
        'date': datetime.now().isoformat().split('T')[0]
    }
    
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO tasks (id, text, completed, date) VALUES (?, ?, ?, ?)',
        (task['id'], task['text'], int(task['completed']), task['date'])
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

# 静态文件
@app.route('/')
@app.route('/notion-style-todo.html')
def index():
    return open('notion-style-todo.html', 'r', encoding='utf-8').read()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)

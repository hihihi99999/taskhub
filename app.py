import streamlit as st
import sqlite3
from datetime import datetime

# データベースの初期化
def init_db():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            time INTEGER NOT NULL,
            completed BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# データベース接続のヘルパー関数
def get_db():
    conn = sqlite3.connect('tasks.db')
    conn.row_factory = sqlite3.Row
    return conn

# タスクの追加
def add_task(date, description, time):
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO tasks (date, description, time, completed) VALUES (?, ?, ?, ?)',
             (date, description, time, False))
    conn.commit()
    conn.close()

# タスクの更新
def update_task(task_id, date, description, time, completed):
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE tasks SET date=?, description=?, time=?, completed=? WHERE id=?',
             (date, description, time, completed, task_id))
    conn.commit()
    conn.close()

# タスクの削除
def delete_task(task_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM tasks WHERE id=?', (task_id,))
    conn.commit()
    conn.close()

# タスク時間の調整
def adjust_time(task_id, adjustment):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT time FROM tasks WHERE id=?', (task_id,))
    current_time = c.fetchone()['time']
    new_time = max(0, current_time + adjustment)
    
    c.execute('UPDATE tasks SET time=? WHERE id=?', (new_time, task_id))
    conn.commit()
    conn.close()
    return new_time

# メインアプリケーション
def main():
    st.title('タスク管理アプリ')
    
    # データベースの初期化
    init_db()
    
    # サイドバーでタスク追加
    st.sidebar.header('新規タスク追加')
    with st.sidebar.form('add_task_form'):
        date = st.date_input('日付')
        description = st.text_input('タスクの説明')
        time = st.number_input('予定時間（分）', min_value=0, step=15)
        submit = st.form_submit_button('タスクを追加')
        
        if submit and description:
            add_task(date.strftime('%Y-%m-%d'), description, time)
            st.success('タスクが追加されました！')
            st.rerun()
    
    # メインエリアでタスク一覧表示
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM tasks ORDER BY date')
    tasks = [dict(task) for task in c.fetchall()]
    conn.close()
    
    if not tasks:
        st.info('タスクがありません。新しいタスクを追加してください。')
    else:
        for task in tasks:
            # 完了したタスクのタイトルに取り消し線を追加
            title = f"{task['date']} - {task['description']} ({task['time']}分)"
            if task['completed']:
                title = f"{task['date']} - ~~{task['description']}~~ ({task['time']}分)"
            with st.expander(title, expanded=True):
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                # タスクの詳細と編集
                with col1:
                    # 完了したタスクには取り消し線を表示
                    if task['completed']:
                        st.markdown(f"~~{task['description']}~~")
                    new_description = st.text_input('説明', task['description'], key=f"desc_{task['id']}")
                    if new_description != task['description']:
                        update_task(task['id'], task['date'], new_description, task['time'], task['completed'])
                        st.rerun()
                
                # 時間調整ボタン
                with col2:
                    if st.button('-15分', key=f"minus15_{task['id']}"):
                        adjust_time(task['id'], -15)
                        st.rerun()
                    if st.button('+15分', key=f"plus15_{task['id']}"):
                        adjust_time(task['id'], 15)
                        st.rerun()
                
                # 完了状態の切り替え
                with col3:
                    completed = st.checkbox('完了', value=task['completed'], key=f"complete_{task['id']}")
                    if completed != task['completed']:
                        update_task(task['id'], task['date'], task['description'], task['time'], completed)
                        st.rerun()
                
                # 削除ボタン
                with col4:
                    if st.button('削除', key=f"delete_{task['id']}"):
                        delete_task(task['id'])
                        st.rerun()

if __name__ == '__main__':
    main()

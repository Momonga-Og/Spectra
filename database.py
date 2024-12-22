import sqlite3
from datetime import datetime

DATABASE_FILE = 'data.db'

def log_voice_activity(user_id, username, channel_id, channel_name, server_id, server_name, join_time, leave_time):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Calculate time spent in seconds
    time_spent = (datetime.strptime(leave_time, '%Y-%m-%d %H:%M:%S') - datetime.strptime(join_time, '%Y-%m-%d %H:%M:%S')).total_seconds()
    
    cursor.execute('''
        INSERT INTO voice_activity (user_id, username, channel_id, channel_name, server_id, server_name, join_time, leave_time, time_spent)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, username, channel_id, channel_name, server_id, server_name, join_time, leave_time, int(time_spent)))
    
    conn.commit()
    conn.close()

def get_all_voice_activity():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM voice_activity')
    data = cursor.fetchall()
    
    conn.close()
    return data

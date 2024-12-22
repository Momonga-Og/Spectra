import sqlite3
from datetime import datetime

DATABASE_FILE = 'data.db'

def initialize_database():
    """Initializes the database and ensures the required table exists."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Create the voice_activity table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS voice_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            channel_id INTEGER NOT NULL,
            channel_name TEXT NOT NULL,
            server_id INTEGER NOT NULL,
            server_name TEXT NOT NULL,
            join_time TEXT NOT NULL,
            leave_time TEXT,
            time_spent INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()

def log_voice_activity(user_id, username, channel_id, channel_name, server_id, server_name, join_time, leave_time):
    """Logs voice activity into the database."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # Calculate time spent in seconds
        time_spent = (datetime.strptime(leave_time, '%Y-%m-%d %H:%M:%S') - datetime.strptime(join_time, '%Y-%m-%d %H:%M:%S')).total_seconds()
        
        cursor.execute('''
            INSERT INTO voice_activity (user_id, username, channel_id, channel_name, server_id, server_name, join_time, leave_time, time_spent)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, username, channel_id, channel_name, server_id, server_name, join_time, leave_time, int(time_spent)))
        
        conn.commit()
    except Exception as e:
        print(f"Error logging voice activity: {e}")
    finally:
        conn.close()

def get_all_voice_activity():
    """Retrieves all voice activity records from the database."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM voice_activity')
        data = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching voice activity: {e}")
        data = []
    finally:
        conn.close()
    
    return data

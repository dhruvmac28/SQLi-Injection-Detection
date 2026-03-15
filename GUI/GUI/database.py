import sqlite3
import os
from datetime import datetime

# Get the path to the database file (created in the same directory as this script)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'security_logs.db')

def init_db():
    """Initializes the database and creates the logs table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            query TEXT NOT NULL,
            severity_score REAL NOT NULL,
            is_malicious BOOLEAN NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def log_query(query, severity_score, is_malicious):
    """Logs a query to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO security_logs (timestamp, query, severity_score, is_malicious)
        VALUES (?, ?, ?, ?)
    ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), query, severity_score, is_malicious))
    conn.commit()
    conn.close()

def get_recent_logs(limit=100):
    """Retrieves the most recent logs from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT timestamp, query, severity_score, is_malicious 
        FROM security_logs 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_stats():
    """Calculates simple stats for the dashboard."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM security_logs")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM security_logs WHERE is_malicious = 1")
    blocked = cursor.fetchone()[0]
    
    conn.close()
    return {"total_queries": total, "blocked_attacks": blocked}

# Ensure the DB is initialized when this file is imported
init_db()

# database.py
import sqlite3
import json

DB_FILE = "arkheionx.db"

def initialize_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alpha_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            source TEXT NOT NULL,
            signal_type TEXT NOT NULL,
            metadata TEXT,
            confidence_level TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("[DB] Database initialized.")

def log_signal(source, signal_type, metadata, confidence):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    metadata_json = json.dumps(metadata)
    cursor.execute('''
        INSERT INTO alpha_signals (source, signal_type, metadata, confidence_level)
        VALUES (?, ?, ?, ?)
    ''', (source, signal_type, metadata_json, confidence))
    conn.commit()
    conn.close()
    print(f"[DB] Signal logged from: {source}")
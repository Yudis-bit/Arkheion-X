"""
ARKHEION-X: Correlator Engine v0.1
This agent acts as the central brain, analyzing signals from other engines
to find high-value, correlated intelligence.
"""
import sqlite3
import json
import time
import logging

# --- Configuration ---
DB_FILE = "arkheionx.db"
POLLING_INTERVAL = 60  # Check for correlations every 60 seconds
CORRELATION_WINDOW_HOURS = 24 # How far back to look for connections (in hours)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def find_correlations():
    """Queries the database and looks for connections between different signals."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # 1. Get the latest sensitive commit signals
        cursor.execute(f"""
            SELECT metadata FROM alpha_signals
            WHERE source = 'Code-Intel'
            AND timestamp > datetime('now', '-{CORRELATION_WINDOW_HOURS} hours')
        """)
        
        sensitive_commits = cursor.fetchall()

        if not sensitive_commits:
            logging.info("No new sensitive commits to analyze. Standing by.")
            return

        for commit_data_json in sensitive_commits:
            commit_data = json.loads(commit_data_json[0])
            repo = commit_data.get('repository')
            
            # Simple logic for now: if a repo has a sensitive commit,
            # we check for ANY large whale movement in the same time window.
            # A future version would map repos to specific whale addresses.
            
            # 2. Check for any large whale movement in the same window
            cursor.execute(f"""
                SELECT metadata FROM alpha_signals
                WHERE source = 'Smart Money Tracker'
                AND confidence_level = 'CRITICAL'
                AND timestamp > datetime('now', '-{CORRELATION_WINDOW_HOURS} hours')
            """)
            
            smart_money_moves = cursor.fetchall()

            if smart_money_moves:
                logging.critical("="*50)
                logging.critical("!!! CRITICAL ALPHA SIGNAL: CORRELATION DETECTED !!!")
                logging.critical(f"  Sensitive commit found in repo: {repo}")
                logging.critical(f"  Commit Message: \"{commit_data.get('commit_message', '').strip()}\"")
                logging.critical(f"  Potentially related Smart Money movements found: {len(smart_money_moves)}")
                
                for move_data_json in smart_money_moves:
                    move_data = json.loads(move_data_json[0])
                    logging.warning(f"    - Fresh wallet {move_data.get('to')} accumulated {move_data.get('amount')} {move_data.get('token')}")
                
                logging.critical("="*50)
                # In a real product, this would trigger a high-priority alert.
        
        conn.close()

    except sqlite3.Error as e:
        logging.error(f"Database error during correlation: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

def main_loop():
    logging.info("Correlator Engine v0.1 Activated. Awaiting signals...")
    while True:
        find_correlations()
        time.sleep(POLLING_INTERVAL)

if __name__ == "__main__":
    main_loop() 
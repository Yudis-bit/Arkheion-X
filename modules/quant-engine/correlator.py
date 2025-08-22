"""
ARKHEION-X: Correlator Engine v1.1 (Module Edition)

This script acts as the central brain. It has been refactored to be
importable by a main controller script (main.py). Its purpose is to
periodically analyze the signals database to find actionable correlations.
"""
import sqlite3
import json
import time
import logging

# Import local database utilities
from database import initialize_db

# --- Configuration ---
DB_FILE = "modules/quant-engine/arkheionx.db" # Updated path for root execution
POLLING_INTERVAL = 60  # Check for correlations every 60 seconds
CORRELATION_WINDOW_HOURS = 24 # How far back to look for connections

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# --- Global Variables ---
# To avoid spamming alerts for the same correlation repeatedly
processed_correlations = set()

def find_correlations():
    """Queries the database and looks for connections between different signals."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # 1. Get recent sensitive commits that we haven't processed yet
        cursor.execute(f"""
            SELECT rowid, metadata FROM alpha_signals
            WHERE source = 'Off-Chain Agent'
            AND timestamp > datetime('now', '-{CORRELATION_WINDOW_HOURS} hours')
        """)
        
        sensitive_commits = cursor.fetchall()

        for commit_id, commit_data_json in sensitive_commits:
            if commit_id in processed_correlations:
                continue # Skip if we've already alerted for this commit

            commit_data = json.loads(commit_data_json)
            repo = commit_data.get('repository')
            
            # Simple logic for now: Check for any critical smart money moves in the same window
            cursor.execute(f"""
                SELECT metadata FROM alpha_signals
                WHERE source = 'On-Chain Agent'
                AND confidence_level = 'CRITICAL'
                AND timestamp > datetime('now', '-{CORRELATION_WINDOW_HOURS} hours')
            """)
            
            smart_money_moves = cursor.fetchall()

            if smart_money_moves:
                log_correlation_alert(repo, commit_data, smart_money_moves)
                processed_correlations.add(commit_id) # Mark this commit as processed
        
        conn.close()

    except sqlite3.Error as e:
        logging.error(f"CORRELATOR AGENT: Database error during correlation: {e}")
    except Exception as e:
        logging.error(f"CORRELATOR AGENT: An unexpected error occurred: {e}", exc_info=True)

def log_correlation_alert(repo, commit_data, smart_money_moves):
    """Formats and logs a critical correlation alert."""
    logging.critical("="*60)
    logging.critical("!!! CRITICAL ALPHA SIGNAL: ON-CHAIN & OFF-CHAIN CORRELATION !!!")
    logging.critical(f"  Description: A sensitive code change was detected around the same time as significant smart money activity.")
    logging.critical(f"  Off-Chain Signal: Sensitive commit in repo -> {repo}")
    logging.critical(f"  Commit Message: \"{commit_data.get('commit_message', '').strip()}\"")
    logging.critical(f"  On-Chain Signal(s): Found {len(smart_money_moves)} related 'Fresh Wallet' movements.")
    
    for move_data_json in smart_money_moves[:3]: # Log max 3 examples to keep it clean
        move_data = json.loads(move_data_json[0])
        logging.warning(f"    - Fresh wallet '{move_data.get('to')[:10]}...' accumulated {move_data.get('amount')} {move_data.get('token')}")
    
    logging.critical("="*60)
    # This is where a high-priority Telegram alert would be sent.

def start_correlation_analysis():
    """
    This is the main function to be called by main.py to start the agent.
    """
    initialize_db()
    logging.info("CORRELATOR AGENT: Analysis patrol started. Awaiting signals...")
    
    while True:
        try:
            # logging.info("CORRELATOR AGENT: Running correlation analysis cycle...")
            find_correlations()
            time.sleep(POLLING_INTERVAL)
        except KeyboardInterrupt:
            logging.info("CORRELATOR AGENT: Shutdown signal received. Terminating patrol.")
            break

if __name__ == "__main__":
    # This block allows the script to be run standalone for testing purposes.
    print("--- Running Correlator Agent in standalone test mode ---")
    start_correlation_analysis()
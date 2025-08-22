"""
ARKHEION-X: Code-Intel Engine v1.1 (Module Edition)

This script acts as the off-chain intelligence agent. It has been refactored
to be importable by a main controller script (main.py). Its primary function
is to monitor GitHub repositories for significant commits.
"""
import os
import time
import requests
import logging
from dotenv import load_dotenv

# Import local database utilities
from database import initialize_db, log_signal

# --- Configuration ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# --- Global Variables ---
# Will be initialized by the start function
GITHUB_PAT = None
last_seen_commits = {}

# A list of target repositories (owner/repo) to monitor.
TARGET_REPOS = [
    "Uniswap/v3-core",
    "aave/aave-v3-core",
    "lidofinance/lido-dao",
    "smartcontractkit/chainlink", # Corrected repo name
    # Add more high-value repositories here
]

# Keywords that can indicate significant, potentially market-moving events.
SENSITIVE_KEYWORDS = ["fix", "patch", "exploit", "vulnerability", "security", "emergency", "hotfix", "critical"]

# Polling interval in seconds.
POLLING_INTERVAL = 300 # 5 minutes

def check_repos():
    """Polls all target repositories for new, sensitive commits."""
    headers = {'Authorization': f'token {GITHUB_PAT}'}
    
    for repo in TARGET_REPOS:
        try:
            url = f"https://api.github.com/repos/{repo}/commits"
            response = requests.get(url, headers=headers, params={'per_page': 1})
            response.raise_for_status()
            
            latest_commit = response.json()[0]
            commit_sha = latest_commit['sha']
            commit_message = latest_commit['commit']['message'].lower()

            if last_seen_commits.get(repo) != commit_sha:
                logging.info(f"OFF-CHAIN AGENT: New commit found for {repo}: {commit_sha[:7]}")
                last_seen_commits[repo] = commit_sha
                
                found_keywords = [keyword for keyword in SENSITIVE_KEYWORDS if keyword in commit_message]
                
                if found_keywords:
                    logging.warning(f"OFF-CHAIN AGENT: SENSITIVE COMMIT DETECTED in {repo}!")
                    signal_metadata = {
                        "repository": repo,
                        "commit_sha": commit_sha,
                        "commit_message": latest_commit['commit']['message'],
                        "keywords_found": found_keywords,
                        "commit_url": latest_commit['html_url']
                    }
                    log_signal("Off-Chain Agent", "Sensitive Commit", signal_metadata, "HIGH")

        except requests.exceptions.HTTPError as e:
             if e.response.status_code == 404:
                 logging.error(f"OFF-CHAIN AGENT: Repository not found: {repo}. Please check the name.")
             else:
                 logging.error(f"OFF-CHAIN AGENT: HTTP Error for {repo}: {e}")
        except (IndexError, KeyError):
            logging.warning(f"OFF-CHAIN AGENT: Could not parse commit data for {repo}.")
        except Exception as e:
            logging.error(f"OFF-CHAIN AGENT: An unexpected error occurred for repo {repo}: {e}")

def start_offchain_patrol():
    """
    This is the main function to be called by main.py to start the agent.
    """
    global GITHUB_PAT
    GITHUB_PAT = os.getenv("GITHUB_PAT")

    if not GITHUB_PAT:
        logging.critical("OFF-CHAIN AGENT: GITHUB_PAT not found in .env file. Terminating patrol.")
        return

    initialize_db()
    logging.info("OFF-CHAIN AGENT: Patrol started.")
    
    # Run once at the beginning to populate initial state
    logging.info("OFF-CHAIN AGENT: Running initial repository check...")
    check_repos()

    while True:
        try:
            logging.info(f"OFF-CHAIN AGENT: Patrol finished. Sleeping for {POLLING_INTERVAL} seconds.")
            time.sleep(POLLING_INTERVAL)
            logging.info("OFF-CHAIN AGENT: Running repository patrol...")
            check_repos()
        except KeyboardInterrupt:
            logging.info("OFF-CHAIN AGENT: Shutdown signal received. Terminating patrol.")
            break

if __name__ == "__main__":
    # This block allows the script to be run standalone for testing purposes.
    print("--- Running Off-Chain Agent in standalone test mode ---")
    start_offchain_patrol()
"""
ARKHEION-X: Code-Intel Engine v1.0
This agent monitors important GitHub repositories for keywords in commit
messages that could indicate significant, unannounced events.
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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

GITHUB_PAT = os.getenv("GITHUB_PAT")

# A list of target repositories (owner/repo) to monitor.
TARGET_REPOS = [
    "Uniswap/v3-core",
    "aave/aave-v3-core",
    "lidofinance/lido-dao",
    "Chainlink/contracts",
    # Add more high-value repositories here
]

# Keywords that can indicate significant, potentially market-moving events.
SENSITIVE_KEYWORDS = ["fix", "patch", "exploit", "vulnerability", "security", "emergency", "hotfix", "critical"]

# Polling interval in seconds. Set higher to respect API rate limits.
POLLING_INTERVAL = 300 # 5 minutes

# In-memory storage to track the last seen commit for each repo.
last_seen_commits = {}

def check_repos():
    """Polls all target repositories for new, sensitive commits."""
    headers = {'Authorization': f'token {GITHUB_PAT}'}

    for repo in TARGET_REPOS:
        try:
            url = f"https://api.github.com/repos/{repo}/commits"
            # We only need the most recent commit to check for new activity.
            response = requests.get(url, headers=headers, params={'per_page': 1})
            response.raise_for_status() # Raise an error for bad responses (4xx or 5xx)

            latest_commit = response.json()[0]
            commit_sha = latest_commit['sha']
            commit_message = latest_commit['commit']['message'].lower()

            # If we haven't seen this commit before, it's new.
            if last_seen_commits.get(repo) != commit_sha:
                logging.info(f"New commit found for {repo}: {commit_sha[:7]}")
                last_seen_commits[repo] = commit_sha # Update the last seen commit

                found_keywords = [keyword for keyword in SENSITIVE_KEYWORDS if keyword in commit_message]

                if found_keywords:
                    logging.warning(f"SENSITIVE COMMIT DETECTED in {repo}!")
                    signal_metadata = {
                        "repository": repo,
                        "commit_sha": commit_sha,
                        "commit_message": latest_commit['commit']['message'],
                        "keywords_found": found_keywords,
                        "commit_url": latest_commit['html_url']
                    }
                    log_signal("Code-Intel", "Sensitive Commit", signal_metadata, "HIGH")

        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch commits for {repo}: {e}")
        except (IndexError, KeyError):
            logging.warning(f"Could not parse commit data for {repo}. It might be empty.")
        except Exception as e:
            logging.error(f"An unexpected error occurred for repo {repo}: {e}")

def main_loop():
    logging.info("Code-Intel Engine v1.0 Activated.")
    while True:
        logging.info("Running repository patrol...")
        check_repos()
        logging.info(f"Patrol finished. Sleeping for {POLLING_INTERVAL} seconds.")
        time.sleep(POLLING_INTERVAL)

if __name__ == "__main__":
    if not GITHUB_PAT:
        logging.critical("GITHUB_PAT not found in .env file. Aborting mission.")
        exit()
    # Initialize the database to ensure the table exists
    initialize_db()
    main_loop()
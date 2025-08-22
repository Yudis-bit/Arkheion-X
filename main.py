"""
ARKHEION-X: Main Application Controller (Trinity Engine) v1.2

This is the central entry point for the ARKHEION-X intelligence ecosystem.
Includes a direct path injection to bypass stubborn environment/import issues.
"""
import sys
import os
import threading
import time
import logging

# --- Direct Path Injection (The Hotwire) ---
# This is the final, brute-force solution to the ModuleNotFoundError.
# We are manually adding the specific module directory to Python's search path.
module_path = os.path.join(os.getcwd(), 'modules', 'quant-engine')
if module_path not in sys.path:
    sys.path.insert(0, module_path)

# Now that Python knows exactly where to look, we can import directly.
from engine import start_onchain_patrol
from code_intel import start_offchain_patrol
from correlator import start_correlation_analysis

# --- Centralized Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(threadName)-16s] - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    logging.info("Initializing ARKHEION-X Unified Intelligence System...")

    agents = {
        "OnChain-Agent": threading.Thread(target=start_onchain_patrol, daemon=True),
        "OffChain-Agent": threading.Thread(target=start_offchain_patrol, daemon=True),
        "Correlator-Agent": threading.Thread(target=start_correlation_analysis, daemon=True),
    }
    
    for name, thread in agents.items():
        thread.name = name
        logging.info(f"Launching agent: {name}...")
        thread.start()
        time.sleep(2)

    logging.info("All agents are operational. System is live. Monitoring...")
    
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logging.info("Shutdown signal received. Terminating all agent patrols.")
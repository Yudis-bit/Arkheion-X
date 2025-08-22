"""
ARKHEION-X: Quant Engine v1.2 (Module Edition)

This script acts as the on-chain intelligence agent. It has been refactored
to be importable by a main controller script (main.py). Its primary function
is to monitor blockchain events and log signals to a shared database.
"""
import os
import time
import json
import logging
from dotenv import load_dotenv
from web3 import Web3

# Import local database utilities
from database import initialize_db, log_signal

# --- Configuration ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# A list of RPC URLs provides redundancy.
RPC_URLS = [
    os.getenv("ARBITRUM_RPC_URL"),
    "https://arbitrum.public.blockpi.network/v1/rpc/public",
    "https://api.zan.top/node/v1/arb/one/public",
]

# A dictionary of target ERC20 tokens to monitor.
TARGET_TOKENS = {
    "USDC": {"address": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831", "decimals": 6},
    "ARB": {"address": "0x912CE59144191C1204E64559FE8253a0e49E6548", "decimals": 18},
}

# --- Thresholds ---
MIN_TRANSFER_VALUE_USD = 10000
FRESH_WALLET_TX_COUNT = 5
POLLING_INTERVAL = 10

# --- Global Variables ---
# These will be initialized by the start_onchain_patrol function
w3 = None
erc20_abi = None

def connect_to_rpc():
    """Attempts to connect to a list of RPC URLs."""
    for url in RPC_URLS:
        try:
            provider = Web3.HTTPProvider(url)
            web3_instance = Web3(provider)
            if web3_instance.is_connected():
                logging.info(f"ON-CHAIN AGENT: Successfully connected to RPC: {url}")
                return web3_instance
        except Exception:
            logging.warning(f"ON-CHAIN AGENT: Failed to connect to {url}. Trying next...")
    return None

def handle_event(event, token_name, token_config):
    """Processes a single Transfer event."""
    args = event['args']
    amount = args['value'] / (10**token_config['decimals'])
    value_usd = amount if token_name in ["USDC", "USDT"] else amount * 1 # Placeholder price
    if value_usd < MIN_TRANSFER_VALUE_USD:
        return

    tx_hash = event['transactionHash'].hex()
    sender = args['from']
    receiver = args['to']
    logging.info(f"ON-CHAIN AGENT: Significant Transfer Detected: {amount:,.2f} {token_name}")

    try:
        tx_count = w3.eth.get_transaction_count(receiver)
        is_fresh_wallet = tx_count < FRESH_WALLET_TX_COUNT
    except Exception:
        tx_count = 'unknown'
        is_fresh_wallet = False

    confidence = "HIGH"
    signal_type = "Large Token Transfer"
    
    if is_fresh_wallet:
        confidence = "CRITICAL"
        signal_type = "Fresh Wallet Accumulation"
        logging.warning(f"ON-CHAIN AGENT: SMART MONEY ALERT! Receiver {receiver} is a fresh wallet (tx count: {tx_count})")

    metadata = {
        "token": token_name, "from": sender, "to": receiver,
        "amount": f"{amount:,.2f}", "value_usd_est": f"${value_usd:,.2f}",
        "tx_hash": tx_hash, "receiver_tx_count": tx_count
    }
    log_signal("On-Chain Agent", signal_type, metadata, confidence)

def start_onchain_patrol():
    """
    This is the main function to be called by main.py to start the agent.
    It handles initialization and the main event loop.
    """
    global w3, erc20_abi # We need to modify the global variables
    
    # --- Initialization Step ---
    w3 = connect_to_rpc()
    if not w3:
        logging.critical("ON-CHAIN AGENT: Could not establish RPC connection. Terminating patrol.")
        return

    try:
        with open('modules/quant-engine/erc20_abi.json', 'r') as f:
            erc20_abi = json.load(f)
    except FileNotFoundError:
        logging.critical("ON-CHAIN AGENT: erc20_abi.json not found. Terminating patrol.")
        return

    initialize_db()
    logging.info(f"ON-CHAIN AGENT: Patrol started. Monitoring {len(TARGET_TOKENS)} tokens...")
    latest_block = w3.eth.block_number

    # --- Main Patrol Loop ---
    while True:
        try:
            new_block = w3.eth.block_number
            if new_block > latest_block:
                # To make logs cleaner, we only log when a scan happens on new blocks
                # logging.info(f"ON-CHAIN AGENT: Scanning blocks from {latest_block + 1} to {new_block}...")
                for token_name, config in TARGET_TOKENS.items():
                    contract = w3.eth.contract(address=config['address'], abi=erc20_abi)
                    transfer_logs = contract.events.Transfer.get_logs(
                        from_block=latest_block + 1,
                        to_block=new_block
                    )
                    if transfer_logs:
                        for event in transfer_logs:
                            handle_event(event, token_name, config)
                latest_block = new_block
            
            time.sleep(POLLING_INTERVAL)

        except KeyboardInterrupt:
            logging.info("ON-CHAIN AGENT: Shutdown signal received. Terminating patrol.")
            break
        except Exception as e:
            logging.error(f"ON-CHAIN AGENT: An unexpected error occurred: {e}", exc_info=True)
            time.sleep(POLLING_INTERVAL * 2)

if __name__ == "__main__":
    # This block allows the script to be run standalone for testing purposes.
    # The main application will import and call start_onchain_patrol() directly.
    print("--- Running On-Chain Agent in standalone test mode ---")
    start_onchain_patrol()
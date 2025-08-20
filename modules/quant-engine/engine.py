"""
ARKHEION-X: Quant Engine v1.1
This script monitors a blockchain for significant ERC20 token transfers,
with a specific focus on detecting potential "smart money" movements
involving fresh wallets.
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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# A list of RPC URLs provides redundancy. If one fails, the script tries the next.
RPC_URLS = [
    os.getenv("ARBITRUM_RPC_URL"),
    "https://arbitrum.public.blockpi.network/v1/rpc/public",
    "https://api.zan.top/node/v1/arb/one/public",
]

# A dictionary of target ERC20 tokens to monitor.
# Easily extendable by adding new tokens with their contract address and decimals.
TARGET_TOKENS = {
    "USDC": {"address": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831", "decimals": 6},
    "ARB": {"address": "0x912CE59144191C1204E64559FE8253a0e49E6548", "decimals": 18},
}

# --- Thresholds ---
MIN_TRANSFER_VALUE_USD = 10000  # Minimum value in USD to trigger an alert.
FRESH_WALLET_TX_COUNT = 5      # A wallet with fewer transactions is considered "fresh".
POLLING_INTERVAL = 10          # Seconds between polling for new blocks.

# --- Global Variables & Setup ---
w3 = None
erc20_abi = None

def connect_to_rpc():
    """Attempts to connect to a list of RPC URLs, returning the first successful connection."""
    for url in RPC_URLS:
        try:
            provider = Web3.HTTPProvider(url)
            web3_instance = Web3(provider)
            if web3_instance.is_connected():
                logging.info(f"Successfully connected to RPC: {url}")
                return web3_instance
        except Exception:
            logging.warning(f"Failed to connect to {url}. Trying next...")
    return None

def handle_event(event, token_name, token_config):
    """Processes a single Transfer event and logs it if it meets the criteria."""
    args = event['args']
    amount = args['value'] / (10**token_config['decimals'])
    
    # NOTE: Simple price assumption for non-stablecoins. A real-world upgrade
    # would involve integrating a price feed API (e.g., CoinGecko).
    value_usd = amount if token_name in ["USDC", "USDT"] else amount * 1
    
    if value_usd < MIN_TRANSFER_VALUE_USD:
        return

    tx_hash = event['transactionHash'].hex()
    sender = args['from']
    receiver = args['to']
    logging.info(f"Significant Transfer Detected: {amount:,.2f} {token_name}")

    try:
        tx_count = w3.eth.get_transaction_count(receiver)
        is_fresh_wallet = tx_count < FRESH_WALLET_TX_COUNT
    except Exception as e:
        logging.warning(f"Could not check transaction count for {receiver}: {e}")
        tx_count = 'unknown'
        is_fresh_wallet = False

    confidence = "HIGH"
    signal_type = "Large Token Transfer"
    
    if is_fresh_wallet:
        confidence = "CRITICAL"
        signal_type = "Fresh Wallet Accumulation"
        logging.warning(f"SMART MONEY ALERT: Receiver {receiver} is a fresh wallet (tx count: {tx_count})")

    metadata = {
        "token": token_name, "from": sender, "to": receiver,
        "amount": f"{amount:,.2f}", "value_usd_est": f"${value_usd:,.2f}",
        "tx_hash": tx_hash, "receiver_tx_count": tx_count
    }
    log_signal("Smart Money Tracker", signal_type, metadata, confidence)

def main_patrol_loop():
    """
    Main event loop that polls for new blocks and fetches event logs
    for all target tokens.
    """
    logging.info("Starting event patrol...")
    latest_block = w3.eth.block_number

    while True:
        try:
            new_block = w3.eth.block_number
            if new_block > latest_block:
                logging.info(f"Scanning blocks from {latest_block + 1} to {new_block}...")
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
            logging.info("Shutdown signal received. Exiting.")
            break
        except Exception as e:
            logging.error(f"An unexpected error occurred in the main loop: {e}", exc_info=True)
            time.sleep(POLLING_INTERVAL * 2)

if __name__ == "__main__":
    w3 = connect_to_rpc()
    if not w3:
        logging.critical("Could not establish RPC connection. Aborting mission.")
        exit()

    try:
        with open('erc20_abi.json', 'r') as f:
            erc20_abi = json.load(f)
    except FileNotFoundError:
        logging.critical("erc20_abi.json not found. Aborting mission.")
        exit()

    initialize_db()
    logging.info(f"Quant Engine v1.1 Activated. Monitoring {len(TARGET_TOKENS)} tokens...")
    main_patrol_loop()
import asyncio
import aiohttp
import json
import os
from datetime import datetime

CUSTOM_WALLETS_FILE = "data/custom_tracked_wallets.json"
CUSTOM_TRACKER_RESULTS = "data/custom_tracker_results.json"

API_KEYS = {
    "helius": "77ded072-5330-4df7-b26f-b59c419499c4",
    "alchemy1": "NuBdUiCxSiGRTuHzQRcFz",
    "alchemy2": "dw_ir0Yc-E-vOKQaWep19",
}

# -------------------------------
# Helper Functions
# -------------------------------
async def fetch_json(session, url, method="GET", payload=None):
    try:
        if method == "GET":
            async with session.get(url, timeout=30) as r:
                return await r.json()
        else:
            async with session.post(url, json=payload, timeout=30) as r:
                return await r.json()
    except Exception as e:
        print(f"❌ Fetch error: {e}")
        return {}

async def fetch_wallet_tokens(session, wallet):
    """Fetch SPL token balances for a wallet"""
    alchemy_key = API_KEYS["alchemy1"]  # simple rotation
    url = f"https://solana-mainnet.g.alchemy.com/v2/{alchemy_key}"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [
            wallet,
            {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
            {"encoding": "jsonParsed"}
        ]
    }

    data = await fetch_json(session, url, method="POST", payload=payload)
    tokens = []

    for acc in data.get("result", {}).get("value", []):
        parsed = acc.get("account", {}).get("data", {}).get("parsed", {}).get("info", {})
        mint = parsed.get("mint")
        amount = parsed.get("tokenAmount", {}).get("uiAmount", 0)
        if mint and amount > 0:
            tokens.append({
                "mint": mint,
                "amount": amount
            })
    return tokens

def calculate_status(first_amount, current_amount):
    if current_amount == 0:
        return "SOLD"
    elif current_amount < first_amount:
        return "PARTIAL"
    elif current_amount > first_amount:
        return "BOUGHT_MORE"
    else:
        return "HOLDING"

# -------------------------------
# Custom Wallet Management
# -------------------------------
def load_custom_wallets():
    if os.path.exists(CUSTOM_WALLETS_FILE):
        with open(CUSTOM_WALLETS_FILE, "r") as f:
            return json.load(f)
    return []

def save_custom_wallets(wallets):
    os.makedirs("data", exist_ok=True)
    with open(CUSTOM_WALLETS_FILE, "w") as f:
        json.dump(wallets, f, indent=2)

def add_custom_wallet(wallet_address, name=""):
    wallets = load_custom_wallets()
    for w in wallets:
        if w.get("address") == wallet_address:
            return {"success": False, "message": "Wallet already in tracking list"}
    wallets.append({
        "address": wallet_address,
        "name": name or f"Wallet {len(wallets)+1}",
        "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_custom_wallets(wallets)
    return {"success": True, "message": "Wallet added successfully", "wallets": wallets}

def remove_custom_wallet(wallet_address):
    wallets = load_custom_wallets()
    original_count = len(wallets)
    wallets = [w for w in wallets if w.get("address") != wallet_address]
    if len(wallets) == original_count:
        return {"success": False, "message": "Wallet not found"}
    save_custom_wallets(wallets)
    return {"success": True, "message": "Wallet removed", "wallets": wallets}

def get_custom_wallets():
    return load_custom_wallets()

# -------------------------------
# Scan Custom Wallets
# -------------------------------
async def parse_wallet(wallet):
    async with aiohttp.ClientSession() as session:
        tokens = await fetch_wallet_tokens(session, wallet)

    wallet_data = {}
    for t in tokens:
        mint = t["mint"]
        amount = t["amount"]

        first_purchase = amount  # Replace with real transaction history if needed
        status = calculate_status(first_purchase, amount)

        wallet_data[mint] = {
            "purchase_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "first_amount": first_purchase,
            "current_amount": amount,
            "status": status
        }
    return wallet_data

async def scan_custom_wallets_async():
    wallets = load_custom_wallets()
    results = []

    tasks = [parse_wallet(w.get("address")) for w in wallets]
    wallets_data = await asyncio.gather(*tasks)

    for w, data in zip(wallets, wallets_data):
        results.append({
            "wallet_address": w.get("address"),
            "wallet_name": w.get("name"),
            "tokens": data,
            "scanned_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    os.makedirs("data", exist_ok=True)
    with open(CUSTOM_TRACKER_RESULTS, "w") as f:
        json.dump(results, f, indent=2)

    return {"success": True, "message": "Custom scan complete", "results": results}

def scan_custom_wallets():
    return asyncio.run(scan_custom_wallets_async())

def get_custom_tracker_results():
    if os.path.exists(CUSTOM_TRACKER_RESULTS):
        with open(CUSTOM_TRACKER_RESULTS, "r") as f:
            return json.load(f)
    return []

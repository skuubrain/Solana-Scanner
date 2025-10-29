import json
import os
from datetime import datetime

CUSTOM_WALLETS_FILE = "data/custom_tracked_wallets.json"
CUSTOM_TRACKER_RESULTS = "data/custom_tracker_results.json"

def load_custom_wallets():
    if os.path.exists(CUSTOM_WALLETS_FILE):
        try:
            with open(CUSTOM_WALLETS_FILE, "r") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except:
            return []
    return []

def save_custom_wallets(wallets):
    os.makedirs("data", exist_ok=True)
    with open(CUSTOM_WALLETS_FILE, "w") as f:
        json.dump(wallets, f, indent=2)

def add_custom_wallet(wallet_address, name=""):
    wallets = load_custom_wallets()
    for w in wallets:
        if w.get("address") == wallet_address:
            return {"success": False, "message": "Wallet already tracked"}

    wallets.append({
        "address": wallet_address,
        "name": name or f"Wallet {len(wallets)+1}",
        "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_custom_wallets(wallets)
    return {"success": True, "message": "Wallet added", "wallets": wallets}

def remove_custom_wallet(wallet_address):
    wallets = load_custom_wallets()
    wallets = [w for w in wallets if w.get("address") != wallet_address]
    save_custom_wallets(wallets)
    return {"success": True, "wallets": wallets}

def get_custom_wallets():
    return load_custom_wallets()

def scan_custom_wallets():
    wallets = load_custom_wallets()
    if not wallets:
        return {"success": False, "message": "No wallets to scan", "results": []}

    results = []
    for w in wallets:
        results.append({
            "wallet_address": w["address"],
            "tokens_bought": [{
                "token": "TOKEN_XYZ",
                "first_purchase": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "HOLDING",
                "amount_remaining": 70.25
            }],
            "total_tokens": 1,
            "scanned_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    os.makedirs("data", exist_ok=True)
    with open(CUSTOM_TRACKER_RESULTS, "w") as f:
        json.dump(results, f, indent=2)
    return {"success": True, "results": results}

def get_custom_tracker_results():
    if os.path.exists(CUSTOM_TRACKER_RESULTS):
        try:
            with open(CUSTOM_TRACKER_RESULTS, "r") as f:
                return json.load(f)
        except:
            return []
    return []

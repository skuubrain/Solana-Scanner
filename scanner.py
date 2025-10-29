import asyncio
import aiohttp
import json
import os
from datetime import datetime

# -------------------------------
# CONFIG / API KEYS
# -------------------------------
DATA_FILE = "data/co_purchase_results.json"

API_KEYS = {
    "helius": "77ded072-5330-4df7-b26f-b59c419499c4",
    "alchemy1": "NuBdUiCxSiGRTuHzQRcFz",
    "alchemy2": "dw_ir0Yc-E-vOKQaWep19",
    "soltracker1": "c89d3b53-74e2-42ac-8c0c-8b4f393d60bb",
    "soltracker2": "e6d255f4-d3ce-457f-b149-883b2f3e93e2",
}

# Example selected wallets
SELECTED_WALLETS = [
    "wallet_A",
    "wallet_B",
    "wallet_C"
]

# -------------------------------
# HELPER FUNCTIONS
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
        print(f"❌ Fetch error for {url}: {e}")
        return {}

# -------------------------------
# FETCH WALLET TOKEN ACCOUNTS
# -------------------------------
async def fetch_wallet_tokens(session, wallet):
    """
    Fetch SPL token balances for a wallet using Alchemy API (async)
    """
    alchemy_key = API_KEYS["alchemy1"]  # simple rotation logic can be added
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

# -------------------------------
# DETERMINE HOLDING STATUS
# -------------------------------
def calculate_status(first_amount, current_amount):
    """
    Determine HOLDING / PARTIAL / SOLD / BOUGHT MORE
    """
    if current_amount == 0:
        return "SOLD"
    elif current_amount < first_amount:
        return "PARTIAL"
    elif current_amount > first_amount:
        return "BOUGHT_MORE"
    else:
        return "HOLDING"

# -------------------------------
# SCAN A SINGLE WALLET
# -------------------------------
async def parse_wallet(wallet):
    async with aiohttp.ClientSession() as session:
        tokens = await fetch_wallet_tokens(session, wallet)

    wallet_data = {}
    for t in tokens:
        mint = t["mint"]
        amount = t["amount"]

        # For demo, assume first purchase = amount (replace with real history if needed)
        first_purchase = amount
        status = calculate_status(first_purchase, amount)

        wallet_data[mint] = {
            "purchase_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "first_amount": first_purchase,
            "current_amount": amount,
            "status": status
        }
    return wallet_data

# -------------------------------
# RUN CO-PURCHASE SCAN
# -------------------------------
async def run_scanner():
    results = {}
    tasks = [parse_wallet(w) for w in SELECTED_WALLETS]
    wallets_data = await asyncio.gather(*tasks)

    # Aggregate by token
    token_summary = {}
    for wallet, data in zip(SELECTED_WALLETS, wallets_data):
        for mint, info in data.items():
            if mint not in token_summary:
                token_summary[mint] = {"token": mint, "wallets": {}}
            token_summary[mint]["wallets"][wallet] = info

    # Save results
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(list(token_summary.values()), f, indent=2)

    return {"success": True, "message": "Scan complete", "results": token_summary}

# -------------------------------
# RUNNER FUNCTIONS
# -------------------------------
def run_co_purchase_scan():
    return asyncio.run(run_scanner())

def load_co_purchase_results():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

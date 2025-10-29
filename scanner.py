import asyncio
import aiohttp
import json
from datetime import datetime
import os

DATA_FILE = "data/co_purchase_results.json"

API_KEYS = {
    "helius": "77ded072-5330-4df7-b26f-b59c419499c4",
    "alchemy1": "NuBdUiCxSiGRTuHzQRcFz",
    "alchemy2": "dw_ir0Yc-E-vOKQaWep19",
    "soltracker1": "c89d3b53-74e2-42ac-8c0c-8b4f393d60bb",
    "soltracker2": "e6d255f4-d3ce-457f-b149-883b2f3e93e2",
}

SOLTRACKER_URL = "https://status.solanatracker.io"

async def fetch_wallet_data(session, wallet):
    """Mock wallet data fetch – replace with real Solana API later."""
    await asyncio.sleep(0.3)
    return {
        "wallet": wallet,
        "token": "TOKEN_XYZ",
        "purchase_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "HOLDING",
        "amount_remaining": round(100 * 0.5, 2)
    }

async def run_scanner():
    wallets = ["wallet_A", "wallet_B", "wallet_C"]
    results = []

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_wallet_data(session, w) for w in wallets]
        results = await asyncio.gather(*tasks)

    token_summary = {}
    for r in results:
        t = r["token"]
        if t not in token_summary:
            token_summary[t] = {"token": t, "wallets": {}}
        token_summary[t]["wallets"][r["wallet"]] = {
            "purchase_time": r["purchase_time"],
            "status": r["status"],
            "amount_remaining": r["amount_remaining"]
        }

    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(list(token_summary.values()), f, indent=2)

    return {"success": True, "message": "Scan complete", "results": token_summary}

def load_co_purchase_results():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def run_co_purchase_scan():
    return asyncio.run(run_scanner())

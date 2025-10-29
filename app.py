from flask import Flask, render_template, jsonify, request
from scanner import run_co_purchase_scan, load_co_purchase_results
from wallet_tracker import (
    get_custom_tracker_results,
    scan_custom_wallets,
    add_custom_wallet,
    remove_custom_wallet,
    get_custom_wallets
)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    result = run_co_purchase_scan()
    return jsonify(result)

@app.route('/co_purchase')
def co_purchase():
    return jsonify(load_co_purchase_results())

@app.route('/custom_scan', methods=['POST'])
def custom_scan():
    result = scan_custom_wallets()
    return jsonify(result)

@app.route('/custom_results')
def custom_results():
    return jsonify(get_custom_tracker_results())

@app.route('/add_wallet', methods=['POST'])
def add_wallet():
    data = request.get_json()
    wallet = data.get("wallet")
    name = data.get("name", "")
    return jsonify(add_custom_wallet(wallet, name))

@app.route('/remove_wallet', methods=['POST'])
def remove_wallet():
    data = request.get_json()
    wallet = data.get("wallet")
    return jsonify(remove_custom_wallet(wallet))

@app.route('/wallets')
def wallets():
    return jsonify(get_custom_wallets())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

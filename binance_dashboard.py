# binance_dashboard.py
# Contains Binance wallet logic and dashboard UI

import json
import requests
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import os

WALLETS_FILE = "binance_wallets.json"

def save_binance_wallet(app, name, api_key, api_secret):
    wallets = load_all_wallets()
    wallets[name] = {
        "api_key": api_key,
        "api_secret": api_secret
    }
    with open(WALLETS_FILE, "w") as f:
        json.dump(wallets, f, indent=4)
    update_wallet_combo(app)
    QMessageBox.information(app, "Success", f"Wallet '{name}' saved.")

def load_all_wallets():
    if not os.path.exists(WALLETS_FILE):
        return {}
    with open(WALLETS_FILE, "r") as f:
        return json.load(f)

def update_wallet_combo(app):
    wallets = load_all_wallets()
    app.wallet_combo.clear()
    app.wallet_combo.addItems(wallets.keys())

def load_selected_wallet(app, name):
    wallets = load_all_wallets()
    wallet = wallets.get(name)
    if wallet:
        app.api_key_input.setText(wallet["api_key"])
        app.api_secret_input.setText(wallet["api_secret"])
    else:
        QMessageBox.warning(app, "Error", f"Wallet '{name}' not found.")

def refresh_wallet(app):
    name = app.wallet_combo.currentText()
    wallets = load_all_wallets()
    wallet = wallets.get(name)
    if not wallet:
        QMessageBox.warning(app, "Error", "No wallet selected.")
        return

    api_key = wallet["api_key"]
    api_secret = wallet["api_secret"]

    # Example: Get account info from Binance API (public endpoint for demonstration)
    url = "https://api.binance.com/api/v3/account"
    headers = {
        "X-MBX-APIKEY": api_key
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            balances = data.get("balances", [])
            app.wallet_table.setRowCount(len(balances))
            for i, bal in enumerate(balances):
                asset_item = QTableWidgetItem(bal["asset"])
                free_item = QTableWidgetItem(str(bal["free"]))
                locked_item = QTableWidgetItem(str(bal["locked"]))
                app.wallet_table.setItem(i, 0, asset_item)
                app.wallet_table.setItem(i, 1, free_item)
                app.wallet_table.setItem(i, 2, locked_item)
            # Optionally update a chart
            assets = [b["asset"] for b in balances]
            values = [float(b["free"]) for b in balances]
            app.figure.clear()
            ax = app.figure.add_subplot(111)
            ax.bar(assets, values)
            ax.set_title("Asset Distribution")
            app.canvas.draw()
        else:
            QMessageBox.warning(app, "API Error", f"Failed to fetch wallet data: {response.text}")
    except Exception as e:
        QMessageBox.critical(app, "Error", str(e))

import sys
import os
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLineEdit, QRadioButton, QButtonGroup, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QScrollArea, QTextEdit, QComboBox
)
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from fpdf import FPDF

class FinanceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Personal Finance Tracker (Qt)")
        self.data = []
        self.json_file = "finance_data.json"
        self.init_ui()
        self.load_data()

        # Apply modern dark stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #232629;
            }
            QTabWidget::pane {
                border: 1px solid #444;
                border-radius: 8px;
                background: #232629;
            }
            QTabBar::tab {
                background: #232629;
                color: #fff;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 8px 20px;
                margin: 2px;
                font-size: 15px;
            }
            QTabBar::tab:selected {
                background: #2d3136;
                color: #00c3ff;
                font-weight: bold;
            }
            QLabel {
                color: #fff;
                font-size: 14px;
            }
            QPushButton {
                background-color: #00c3ff;
                color: #fff;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #009ad6;
            }
            QLineEdit, QComboBox {
                background: #2d3136;
                color: #fff;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 6px;
                font-size: 14px;
            }
            QTableWidget {
                background: #232629;
                color: #fff;
                gridline-color: #444;
                font-size: 13px;
                border-radius: 8px;
            }
            QHeaderView::section {
                background: #2d3136;
                color: #00c3ff;
                font-weight: bold;
                border: none;
                padding: 8px;
            }
            QTableWidget::item:selected {
                background: #00c3ff;
                color: #232629;
            }
        """)

    def init_ui(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # --- Finance Data Tab ---
        self.tab_data = QWidget()
        self.tabs.addTab(self.tab_data, "Finance Data")
        data_layout = QVBoxLayout(self.tab_data)

        # Input Form
        form = QFormLayout()
        self.entries = {}
        # Month dropdown
        from PySide6.QtWidgets import QComboBox
        self.entries["Month"] = QComboBox()
        self.entries["Month"].addItems([
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ])
        form.addRow("Month", self.entries["Month"])
        # Other fields
        for label in ["Salary", "Phone Bill", "Petrol Money", "Annual Rent", "Living Expenses", "Debt Amount"]:
            self.entries[label] = QLineEdit()
            form.addRow(label, self.entries[label])

        # Debt Type
        self.debt_type_group = QButtonGroup()
        self.rb_personal = QRadioButton("Personal")
        self.rb_personal.setStyleSheet("color: #ffffff;")
        self.rb_housing = QRadioButton("Housing")
        self.rb_housing.setStyleSheet("color: #ffffff;")
        self.rb_personal.setChecked(True)
        self.debt_type_group.addButton(self.rb_personal)
        self.debt_type_group.addButton(self.rb_housing)
        debt_type_layout = QHBoxLayout()
        debt_type_layout.addWidget(self.rb_personal)
        debt_type_layout.addWidget(self.rb_housing)
        form.addRow("Debt Type", debt_type_layout)

        # Savings %
        self.savings_pct_label = QLabel("0.00")
        form.addRow("Savings %", self.savings_pct_label)

        # Add Data Button
        self.btn_add = QPushButton("Add Month Data")
        form.addRow(self.btn_add)

        form_widget = QWidget()
        form_widget.setLayout(form)
        data_layout.addWidget(form_widget)

        # Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Month", "Salary", "Expenses", "Savings", "Invested"])
        self.table.horizontalHeader().setStretchLastSection(True)
        data_layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_chart = QPushButton("Show Chart")
        self.btn_pdf = QPushButton("Export PDF")
        self.btn_logs = QPushButton("Show Logs")
        self.btn_delete = QPushButton("Delete Entry")
        self.btn_clear = QPushButton("Clear Database")
        btn_layout.addWidget(self.btn_chart)
        btn_layout.addWidget(self.btn_pdf)
        btn_layout.addWidget(self.btn_logs)
        btn_layout.addWidget(self.btn_delete)
        data_layout.addLayout(btn_layout)
        data_layout.addWidget(self.btn_clear)

        # --- Investment Growth Tab ---
        self.tab_growth = QWidget()
        self.tabs.addTab(self.tab_growth, "Investment Growth")
        growth_layout = QVBoxLayout(self.tab_growth)

        growth_form = QFormLayout()
        self.cagr_entry = QLineEdit()
        self.period_entry = QLineEdit()
        self.btn_growth = QPushButton("Show Growth Graph")
        self.final_value_label = QLabel("0.00")
        self.total_invested_label = QLabel("0.00")
        growth_form.addRow("CAGR (%)", self.cagr_entry)
        growth_form.addRow("Period (months)", self.period_entry)
        growth_form.addRow(self.btn_growth)
        growth_form.addRow("Final Value", self.final_value_label)
        growth_form.addRow("Total Invested", self.total_invested_label)
        growth_form_widget = QWidget()
        growth_form_widget.setLayout(growth_form)
        growth_layout.addWidget(growth_form_widget)

        self.growth_canvas = None

        # --- Binance Wallet Dashboard Tab ---
        self.tab_binance = QWidget()
        self.tabs.addTab(self.tab_binance, "Binance Dashboard")
        binance_layout = QVBoxLayout(self.tab_binance)


        # Multiple wallet support
        self.wallet_name_entry = QLineEdit()
        self.wallet_name_entry.setPlaceholderText("Wallet Name")
        self.api_key_entry = QLineEdit()
        self.api_secret_entry = QLineEdit()
        self.api_secret_entry.setEchoMode(QLineEdit.Password)
        self.btn_save_api = QPushButton("Save Wallet")
        self.wallet_select_combo = QComboBox()
        self.btn_load_wallet = QPushButton("Load Selected Wallet")

        api_form = QFormLayout()
        api_form.addRow("Wallet Name", self.wallet_name_entry)
        api_form.addRow("API Key", self.api_key_entry)
        api_form.addRow("API Secret", self.api_secret_entry)
        api_form.addRow(self.btn_save_api)
        api_form.addRow("Select Wallet", self.wallet_select_combo)
        api_form.addRow(self.btn_load_wallet)
        api_form_widget = QWidget()
        api_form_widget.setLayout(api_form)
        binance_layout.addWidget(api_form_widget)


        # --- Binance Dashboard UI ---
        # --- Sleek Binance Dashboard UI ---
        self.wallet_summary_label = QLabel("Total Holdings: AED 0.00 | Wallet PnL: 0.00%")
        self.wallet_summary_label.setStyleSheet("font-weight: bold; font-size: 18px; margin-bottom: 16px; color: #00c3ff;")
        binance_layout.addWidget(self.wallet_summary_label)

        self.wallet_table = QTableWidget()
        self.wallet_table.setColumnCount(6)
        self.wallet_table.setHorizontalHeaderLabels([
            "Asset", "Total", "Price (USD)", "Price (AED)", "Daily PnL (%)", "Holding Value (AED)"
        ])
        self.wallet_table.horizontalHeader().setStretchLastSection(True)
        self.wallet_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.wallet_table.setAlternatingRowColors(True)
        self.wallet_table.setStyleSheet("alternate-background-color: #2d3136; background-color: #232629;")
        binance_layout.addWidget(self.wallet_table)

        # Loading animation
        self.loading_label = QLabel("")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("font-size: 15px; color: #00c3ff; margin: 10px;")
        binance_layout.addWidget(self.loading_label)

        # Refresh button
        self.btn_refresh_wallet = QPushButton("Refresh Wallet")
        binance_layout.addWidget(self.btn_refresh_wallet)

        # Signals for API key save and wallet refresh

        self.btn_save_api.clicked.connect(self.save_binance_wallet)
        self.btn_load_wallet.clicked.connect(self.load_selected_wallet)
        self.btn_refresh_wallet.clicked.connect(self.refresh_wallet)

        self.wallets = self.load_all_wallets()
        self.update_wallet_combo()
        self.current_wallet = None


        # --- Signals ---
        for entry in ["Salary", "Phone Bill", "Petrol Money", "Annual Rent", "Living Expenses", "Debt Amount"]:
            self.entries[entry].textChanged.connect(self.update_savings_pct)
        self.rb_personal.toggled.connect(self.update_savings_pct)
        self.rb_housing.toggled.connect(self.update_savings_pct)
        self.btn_add.clicked.connect(self.add_data)
        self.btn_chart.clicked.connect(self.show_chart)
        self.btn_pdf.clicked.connect(self.export_pdf)
        self.btn_logs.clicked.connect(self.show_logs)
        self.btn_delete.clicked.connect(self.delete_entry)
        self.btn_clear.clicked.connect(self.clear_database)
        self.btn_growth.clicked.connect(self.show_growth_graph)



    def save_binance_wallet(self):
        # Save wallet credentials with a name
        name = self.wallet_name_entry.text().strip()
        api_key = self.api_key_entry.text().strip()
        api_secret = self.api_secret_entry.text().strip()
        if not name or not api_key or not api_secret:
            QMessageBox.warning(self, "Warning", "Please enter wallet name, API key, and secret.")
            return
        self.wallets[name] = {"api_key": api_key, "api_secret": api_secret}
        try:
            with open("binance_wallets.json", "w") as f:
                json.dump(self.wallets, f)
            QMessageBox.information(self, "Success", f"Wallet '{name}' saved.")
            self.update_wallet_combo()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save wallet: {e}")

    def load_all_wallets(self):
        # Load all wallets from file
        try:
            with open("binance_wallets.json", "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def update_wallet_combo(self):
        self.wallet_select_combo.clear()
        for name in self.wallets.keys():
            self.wallet_select_combo.addItem(name)

    def load_selected_wallet(self):
        name = self.wallet_select_combo.currentText()
        if name in self.wallets:
            self.current_wallet = self.wallets[name]
            QMessageBox.information(self, "Loaded", f"Loaded wallet: {name}")
        else:
            QMessageBox.warning(self, "Warning", "Selected wallet not found.")

    def refresh_wallet(self):
        self.loading_label.setText("Fetching wallet data... Please wait.")
        QApplication.processEvents()
        # Use selected wallet
        if not self.current_wallet:
            self.loading_label.setText("")
            self.wallet_summary_label.setText("No wallet selected. Please select a wallet above.")
            self.wallet_table.setRowCount(0)
            return
        api_key = self.current_wallet.get("api_key")
        api_secret = self.current_wallet.get("api_secret")
        try:
            import requests
            from urllib.parse import urlencode
            import hmac, hashlib, time
            base_url = "https://api.binance.com"
            endpoint = "/api/v3/account"
            timestamp = int(time.time() * 1000)
            query = urlencode({"timestamp": timestamp})
            signature = hmac.new(api_secret.encode(), query.encode(), hashlib.sha256).hexdigest()
            headers = {"X-MBX-APIKEY": api_key}
            url = f"{base_url}{endpoint}?{query}&signature={signature}"
            resp = requests.get(url, headers=headers)
            if resp.status_code != 200:
                self.loading_label.setText("")
                self.wallet_summary_label.setText(f"Failed to fetch wallet: {resp.text}")
                self.wallet_table.setRowCount(0)
                return
            data = resp.json()
            balances = [b for b in data["balances"] if float(b["free"]) > 0 or float(b["locked"]) > 0]
            if not balances:
                self.loading_label.setText("")
                self.wallet_summary_label.setText("No assets found in wallet.")
                self.wallet_table.setRowCount(0)
                return

            # Get USD-AED conversion rate
            try:
                forex_resp = requests.get("https://api.exchangerate.host/latest?base=USD&symbols=AED")
                usd_to_aed = forex_resp.json()["rates"]["AED"] if forex_resp.status_code == 200 else 3.67
            except Exception:
                usd_to_aed = 3.67  # fallback

            # Prepare table data and summary
            self.wallet_table.setRowCount(0)
            total_aed = 0.0
            total_pnl = 0.0
            asset_count = 0
            for b in balances:
                asset = b['asset']
                free = float(b['free'])
                locked = float(b['locked'])
                total = free + locked
                if asset == "USDT":
                    price = 1.0
                    price_aed = price * usd_to_aed
                    daily_pnl = 0.0
                else:
                    symbol = asset + "USDT"
                    ticker_url = f"{base_url}/api/v3/ticker/24hr?symbol={symbol}"
                    ticker_resp = requests.get(ticker_url)
                    if ticker_resp.status_code == 200:
                        ticker = ticker_resp.json()
                        price = float(ticker.get("lastPrice", 0))
                        price_aed = price * usd_to_aed
                        daily_pnl = float(ticker.get("priceChangePercent", 0))
                    else:
                        price = 0.0
                        price_aed = 0.0
                        daily_pnl = 0.0
                holding_value_aed = total * price_aed
                total_aed += holding_value_aed
                total_pnl += daily_pnl
                asset_count += 1
                row = self.wallet_table.rowCount()
                self.wallet_table.insertRow(row)
                self.wallet_table.setItem(row, 0, QTableWidgetItem(asset))
                self.wallet_table.setItem(row, 1, QTableWidgetItem(f"{total:.6f}"))
                self.wallet_table.setItem(row, 2, QTableWidgetItem(f"${price:.2f}"))
                self.wallet_table.setItem(row, 3, QTableWidgetItem(f"AED {price_aed:.2f}"))
                self.wallet_table.setItem(row, 4, QTableWidgetItem(f"{daily_pnl:.2f}%"))
                self.wallet_table.setItem(row, 5, QTableWidgetItem(f"AED {holding_value_aed:.2f}"))

            avg_pnl = total_pnl / asset_count if asset_count > 0 else 0.0
            self.wallet_summary_label.setText(f"Total Holdings: AED {total_aed:,.2f} | Wallet PnL: {avg_pnl:.2f}%")
            self.loading_label.setText("")
        except Exception as e:
            self.loading_label.setText("")
            self.wallet_summary_label.setText(f"Error: {e}")
            self.wallet_table.setRowCount(0)

    def load_data(self):
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, "r") as f:
                    self.data = json.load(f)
                for d in self.data:
                    self.add_table_row(d)
            except Exception:
                self.data = []

    def save_data(self):
        try:
            with open(self.json_file, "w") as f:
                json.dump(self.data, f)
        except Exception:
            pass

    def clear_database(self):
        self.data = []
        self.table.setRowCount(0)
        if os.path.exists(self.json_file):
            os.remove(self.json_file)

    def add_data(self):
        try:
            month = self.entries["Month"].currentText()
            salary = float(self.entries["Salary"].text())
            phone = float(self.entries["Phone Bill"].text())
            petrol = float(self.entries["Petrol Money"].text())
            annual_rent = float(self.entries["Annual Rent"].text())
            living = float(self.entries["Living Expenses"].text())
            debt_amt = float(self.entries["Debt Amount"].text())
            debt_type = "personal" if self.rb_personal.isChecked() else "housing"

            monthly_rent = annual_rent / 12
            term = 4 if debt_type == "personal" else 25
            interest_rate = 7.49 / 100
            months = term * 12
            monthly_interest = interest_rate / 12
            if monthly_interest > 0:
                monthly_debt = (debt_amt * monthly_interest * (1 + monthly_interest) ** months) / ((1 + monthly_interest) ** months - 1)
            else:
                monthly_debt = debt_amt / months

            total_expenses = phone + petrol + monthly_rent + living + monthly_debt
            remaining = salary - total_expenses
            savings_pct = (remaining / salary * 100) if salary > 0 else 0
            savings = remaining * (savings_pct / 100) if savings_pct > 0 else 0
            investable = remaining - savings

            log = (
                f"Month: {month}\n"
                f"Salary: {salary:.2f}\n"
                f"Phone Bill: {phone:.2f}\n"
                f"Petrol Money: {petrol:.2f}\n"
                f"Annual Rent: {annual_rent:.2f}\n"
                f"Monthly Rent: {monthly_rent:.2f}\n"
                f"Living Expenses: {living:.2f}\n"
                f"Debt Amount: {debt_amt:.2f}\n"
                f"Debt Type: {debt_type}\n"
                f"Debt Term (years): {term}\n"
                f"Interest Rate: {interest_rate*100:.2f}%\n"
                f"Monthly Debt Payment: {monthly_debt:.2f}\n"
                f"Total Expenses: {total_expenses:.2f}\n"
                f"Remaining after Expenses: {remaining:.2f}\n"
                f"Savings %: {savings_pct:.2f}\n"
                f"Savings: {savings:.2f}\n"
                f"Invested: {investable:.2f}\n"
            )
            entry = {
                "Month": month,
                "Salary": salary,
                "Expenses": total_expenses,
                "Savings": savings,
                "Invested": investable,
                "Log": log
            }
            self.data.append(entry)
            self.add_table_row(entry)
            self.savings_pct_label.setText(f"{savings_pct:.2f}")
            self.save_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Invalid input: {e}")

    def add_table_row(self, d):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(str(d["Month"])))
        self.table.setItem(row, 1, QTableWidgetItem(f"{d['Salary']:.2f}"))
        self.table.setItem(row, 2, QTableWidgetItem(f"{d['Expenses']:.2f}"))
        self.table.setItem(row, 3, QTableWidgetItem(f"{d['Savings']:.2f}"))
        self.table.setItem(row, 4, QTableWidgetItem(f"{d['Invested']:.2f}"))

    def update_savings_pct(self):
        try:
            salary = float(self.entries["Salary"].text()) if self.entries["Salary"].text() else 0
            phone = float(self.entries["Phone Bill"].text()) if self.entries["Phone Bill"].text() else 0
            petrol = float(self.entries["Petrol Money"].text()) if self.entries["Petrol Money"].text() else 0
            annual_rent = float(self.entries["Annual Rent"].text()) if self.entries["Annual Rent"].text() else 0
            living = float(self.entries["Living Expenses"].text()) if self.entries["Living Expenses"].text() else 0
            debt_amt = float(self.entries["Debt Amount"].text()) if self.entries["Debt Amount"].text() else 0
            debt_type = "personal" if self.rb_personal.isChecked() else "housing"
            monthly_rent = annual_rent / 12 if annual_rent else 0
            term = 4 if debt_type == "personal" else 25
            interest_rate = 7.49 / 100
            months = term * 12
            monthly_interest = interest_rate / 12
            if monthly_interest > 0 and months > 0:
                monthly_debt = (debt_amt * monthly_interest * (1 + monthly_interest) ** months) / ((1 + monthly_interest) ** months - 1)
            elif months > 0:
                monthly_debt = debt_amt / months
            else:
                monthly_debt = 0
            total_expenses = phone + petrol + monthly_rent + living + monthly_debt
            remaining = salary - total_expenses
            savings_pct = (remaining / salary * 100) if salary > 0 else 0
            self.savings_pct_label.setText(f"{savings_pct:.2f}")
        except Exception:
            self.savings_pct_label.setText("0.00")


    def show_logs(self):
        if not self.data:
            QMessageBox.information(self, "Info", "No logs to show.")
            return
        self.log_win = QWidget()
        self.log_win.setWindowTitle("Calculation Logs")
        self.log_win.resize(600, 400)
        layout = QVBoxLayout(self.log_win)
        text = QTextEdit()
        text.setReadOnly(True)
        for i, d in enumerate(self.data):
            text.append(f"Entry {i+1}:\n{d['Log']}\n{'-'*50}\n")
        layout.addWidget(text)
        self.log_win.show()
        self.log_win.raise_()

    def delete_entry(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Info", "No entry selected to delete.")
            return
        self.table.removeRow(row)
        del self.data[row]
        self.save_data()

    def show_chart(self):
        if not self.data:
            QMessageBox.information(self, "Info", "No data to plot.")
            return
        months = [d["Month"] for d in self.data]
        expenses = [d["Expenses"] for d in self.data]
        savings = [d["Savings"] for d in self.data]
        invested = [d["Invested"] for d in self.data]

        x = list(range(len(months)))
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(x, expenses, label="Expenses")
        ax.plot(x, savings, label="Savings")
        ax.plot(x, invested, label="Invested")
        ax.set_xlabel("Month")
        ax.set_ylabel("Amount")
        ax.set_title("Monthly Finance Overview")
        ax.set_xticks(x)
        ax.set_xticklabels(months, rotation=45)
        ax.legend()
        ax.grid(True)
        plt.tight_layout()

        # Remove old canvas if exists
        if hasattr(self, 'chart_canvas') and self.chart_canvas is not None:
            self.chart_canvas.setParent(None)
            self.chart_canvas = None

        self.chart_win = QWidget()
        self.chart_win.setWindowTitle("Finance Chart")
        layout = QVBoxLayout()
        self.chart_win.setLayout(layout)
        self.chart_canvas = FigureCanvas(fig)
        layout.addWidget(self.chart_canvas)
        self.chart_win.resize(700, 500)
        self.chart_win.show()
        self.chart_win.raise_()

    def show_growth_graph(self):
        try:
            cagr = float(self.cagr_entry.text()) / 100
            period = int(self.period_entry.text())
            invested_monthly = [d["Invested"] for d in self.data]
            if not invested_monthly or period <= 0:
                QMessageBox.information(self, "Info", "No investment data or invalid period.")
                return
            growth = []
            invested_cumulative = []
            total = 0
            invested_total = 0
            for month in range(period):
                if month < len(invested_monthly):
                    total += invested_monthly[month]
                    invested_total += invested_monthly[month]
                total *= (1 + cagr / 12)
                growth.append(total)
                invested_cumulative.append(invested_total)
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot(range(1, period+1), invested_cumulative, label="Total Invested", linestyle="--")
            ax.plot(range(1, period+1), growth, label="Actual Value", linewidth=2)
            ax.set_xlabel("Month")
            ax.set_ylabel("Value")
            ax.set_title("Investment Growth Over Time")
            ax.legend()
            ax.grid(True)
            plt.tight_layout()
            # Remove all previous FigureCanvas widgets from layout except the form
            layout = self.tab_growth.layout()
            for i in reversed(range(layout.count())):
                widget = layout.itemAt(i).widget()
                if isinstance(widget, FigureCanvasQTAgg):
                    layout.removeWidget(widget)
                    widget.setParent(None)
            self.growth_canvas = FigureCanvas(fig)
            layout.addWidget(self.growth_canvas)
            self.final_value_label.setText(f"{growth[-1]:.2f}" if growth else "0.00")
            self.total_invested_label.setText(f"{invested_cumulative[-1]:.2f}" if invested_cumulative else "0.00")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Growth graph error: {e}")

    def export_pdf(self):
        if not self.data:
            QMessageBox.information(self, "Info", "No data to export.")
            return
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Personal Finance Report", ln=True, align="C")
        pdf.ln(10)
        for d in self.data:
            pdf.cell(0, 10, txt=f"Month: {d['Month']}, Salary: {d['Salary']:.2f}, Expenses: {d['Expenses']:.2f}, Savings: {d['Savings']:.2f}, Invested: {d['Invested']:.2f}", ln=True)
        try:
            pdf.output("finance_report.pdf")
            QMessageBox.information(self, "Success", "PDF exported as finance_report.pdf")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"PDF export failed: {e}")

if __name__ == "__main__":
    from ui import setup_main_tabs
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setWindowTitle("Personal Finance Tracker (Qt)")
    setup_main_tabs(win)
    win.resize(700, 900)
    win.show()
    sys.exit(app.exec())
# ui.py
# Contains UI setup for the FinanceApp

from PySide6.QtWidgets import (
    QTabWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QRadioButton, QButtonGroup, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QTextEdit, QComboBox, QWidget
)
from PySide6.QtCore import Qt

def setup_main_tabs(app):
    app.tabs = QTabWidget()
    app.setCentralWidget(app.tabs)

    # --- Finance Data Tab ---
    app.tab_data = QWidget()
    app.tabs.addTab(app.tab_data, "Finance Data")
    data_layout = QVBoxLayout(app.tab_data)

    form = QFormLayout()
    app.entries = {}
    app.entries["Month"] = QComboBox()
    app.entries["Month"].addItems([
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ])
    form.addRow("Month", app.entries["Month"])
    for label in ["Salary", "Phone Bill", "Petrol Money", "Annual Rent", "Living Expenses", "Debt Amount"]:
        app.entries[label] = QLineEdit()
        form.addRow(label, app.entries[label])

    app.debt_type_group = QButtonGroup()
    app.rb_personal = QRadioButton("Personal")
    app.rb_personal.setStyleSheet("color: #ffffff;")
    app.rb_housing = QRadioButton("Housing")
    app.rb_housing.setStyleSheet("color: #ffffff;")
    app.rb_personal.setChecked(True)
    app.debt_type_group.addButton(app.rb_personal)
    app.debt_type_group.addButton(app.rb_housing)
    debt_type_layout = QHBoxLayout()
    debt_type_layout.addWidget(app.rb_personal)
    debt_type_layout.addWidget(app.rb_housing)
    form.addRow("Debt Type", debt_type_layout)

    app.savings_pct_label = QLabel("0.00")
    form.addRow("Savings %", app.savings_pct_label)

    app.btn_add = QPushButton("Add Month Data")
    form.addRow(app.btn_add)

    form_widget = QWidget()
    form_widget.setLayout(form)
    data_layout.addWidget(form_widget)

    app.table = QTableWidget(0, 5)
    app.table.setHorizontalHeaderLabels(["Month", "Salary", "Expenses", "Savings", "Invested"])
    app.table.horizontalHeader().setStretchLastSection(True)
    data_layout.addWidget(app.table)

    btn_layout = QHBoxLayout()
    app.btn_chart = QPushButton("Show Chart")
    app.btn_pdf = QPushButton("Export PDF")
    app.btn_logs = QPushButton("Show Logs")
    app.btn_delete = QPushButton("Delete Entry")
    app.btn_clear = QPushButton("Clear Database")
    btn_layout.addWidget(app.btn_chart)
    btn_layout.addWidget(app.btn_pdf)
    btn_layout.addWidget(app.btn_logs)
    btn_layout.addWidget(app.btn_delete)
    data_layout.addLayout(btn_layout)
    data_layout.addWidget(app.btn_clear)

    # --- Investment Growth Tab ---
    app.tab_growth = QWidget()
    app.tabs.addTab(app.tab_growth, "Investment Growth")
    growth_layout = QVBoxLayout(app.tab_growth)

    growth_form = QFormLayout()
    app.cagr_entry = QLineEdit()
    app.period_entry = QLineEdit()
    app.btn_growth = QPushButton("Show Growth Graph")
    app.final_value_label = QLabel("0.00")
    app.total_invested_label = QLabel("0.00")
    growth_form.addRow("CAGR (%)", app.cagr_entry)
    growth_form.addRow("Period (months)", app.period_entry)
    growth_form.addRow(app.btn_growth)
    growth_form.addRow("Final Value", app.final_value_label)
    growth_form.addRow("Total Invested", app.total_invested_label)
    growth_form_widget = QWidget()
    growth_form_widget.setLayout(growth_form)
    growth_layout.addWidget(growth_form_widget)

    app.growth_canvas = None

    # --- Binance Wallet Dashboard Tab ---
    app.tab_binance = QWidget()
    app.tabs.addTab(app.tab_binance, "Binance Dashboard")
    binance_layout = QVBoxLayout(app.tab_binance)

    app.wallet_name_entry = QLineEdit()
    app.wallet_name_entry.setPlaceholderText("Wallet Name")
    app.api_key_entry = QLineEdit()
    app.api_secret_entry = QLineEdit()
    app.api_secret_entry.setEchoMode(QLineEdit.Password)
    app.btn_save_api = QPushButton("Save Wallet")
    app.wallet_select_combo = QComboBox()
    app.btn_load_wallet = QPushButton("Load Selected Wallet")

    api_form = QFormLayout()
    api_form.addRow("Wallet Name", app.wallet_name_entry)
    api_form.addRow("API Key", app.api_key_entry)
    api_form.addRow("API Secret", app.api_secret_entry)
    api_form.addRow(app.btn_save_api)
    api_form.addRow("Select Wallet", app.wallet_select_combo)
    api_form.addRow(app.btn_load_wallet)
    api_form_widget = QWidget()
    api_form_widget.setLayout(api_form)
    binance_layout.addWidget(api_form_widget)

    app.wallet_summary_label = QLabel("Total Holdings: AED 0.00 | Wallet PnL: 0.00%")
    app.wallet_summary_label.setStyleSheet("font-weight: bold; font-size: 18px; margin-bottom: 16px; color: #00c3ff;")
    binance_layout.addWidget(app.wallet_summary_label)

    app.wallet_table = QTableWidget()
    app.wallet_table.setColumnCount(6)
    app.wallet_table.setHorizontalHeaderLabels([
        "Asset", "Total", "Price (USD)", "Price (AED)", "Daily PnL (%)", "Holding Value (AED)"
    ])
    app.wallet_table.horizontalHeader().setStretchLastSection(True)
    app.wallet_table.setEditTriggers(QTableWidget.NoEditTriggers)
    app.wallet_table.setAlternatingRowColors(True)
    app.wallet_table.setStyleSheet("alternate-background-color: #2d3136; background-color: #232629;")
    binance_layout.addWidget(app.wallet_table)

    app.loading_label = QLabel("")
    app.loading_label.setAlignment(Qt.AlignCenter)
    app.loading_label.setStyleSheet("font-size: 15px; color: #00c3ff; margin: 10px;")
    binance_layout.addWidget(app.loading_label)

    app.btn_refresh_wallet = QPushButton("Refresh Wallet")
    binance_layout.addWidget(app.btn_refresh_wallet)

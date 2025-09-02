import sys
import os
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLineEdit, QRadioButton, QButtonGroup, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QScrollArea, QTextEdit
)
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from fpdf import FPDF

class FinanceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Personal Finance Tracker (Qt)")
        self.data = []
        self.json_file = "finance_data.json"
        self.init_ui()
        self.load_data()

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
        self.rb_housing = QRadioButton("Housing")
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

        self.chart_win = QWidget()
        self.chart_win.setWindowTitle("Finance Chart")
        layout = QVBoxLayout()
        self.chart_win.setLayout(layout)
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
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
            if self.growth_canvas:
                self.growth_canvas.setParent(None)
            self.growth_canvas = FigureCanvas(fig)
            self.tab_growth.layout().addWidget(self.growth_canvas)
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
    app = QApplication(sys.argv)
    win = FinanceApp()
    win.resize(900, 700)
    win.show()
    sys.exit(app.exec())
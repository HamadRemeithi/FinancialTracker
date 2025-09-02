# finance_logic.py
# Contains finance calculations and data management

import json
import os
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem

DATA_FILE = "finance_data.json"

def load_data(app):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            app.data = json.load(f)
    else:
        app.data = []
    app.tableWidget.setRowCount(0)
    for entry in app.data:
        add_table_row(app, entry)

def save_data(app):
    with open(DATA_FILE, "w") as f:
        json.dump(app.data, f, indent=4)

def clear_database(app):
    reply = QMessageBox.question(app, "Clear Database", "Are you sure you want to clear all data?",
                                 QMessageBox.Yes | QMessageBox.No)
    if reply == QMessageBox.Yes:
        app.data = []
        app.tableWidget.setRowCount(0)
        save_data(app)

def add_data(app):
    entry = {
        "date": app.dateEdit.text(),
        "description": app.descriptionEdit.text(),
        "amount": float(app.amountEdit.text()),
        "category": app.categoryCombo.currentText()
    }
    app.data.append(entry)
    add_table_row(app, entry)
    save_data(app)
    update_savings_pct(app)

def add_table_row(app, d):
    row = app.tableWidget.rowCount()
    app.tableWidget.insertRow(row)
    app.tableWidget.setItem(row, 0, QTableWidgetItem(d["date"]))
    app.tableWidget.setItem(row, 1, QTableWidgetItem(d["description"]))
    app.tableWidget.setItem(row, 2, QTableWidgetItem(str(d["amount"])))
    app.tableWidget.setItem(row, 3, QTableWidgetItem(d["category"]))

def update_savings_pct(app):
    total = sum(entry["amount"] for entry in app.data)
    savings = sum(entry["amount"] for entry in app.data if entry["category"].lower() == "savings")
    pct = (savings / total * 100) if total > 0 else 0
    app.savingsLabel.setText(f"Savings: {pct:.2f}%")

def show_logs(app):
    logs = "\n".join([f"{e['date']}: {e['description']} - {e['amount']} ({e['category']})" for e in app.data])
    QMessageBox.information(app, "Logs", logs if logs else "No logs available.")

def delete_entry(app):
    row = app.tableWidget.currentRow()
    if row >= 0:
        app.tableWidget.removeRow(row)
        del app.data[row]
        save_data(app)
        update_savings_pct(app)

def show_chart(app):
    # Placeholder for chart logic
    QMessageBox.information(app, "Chart", "Chart functionality not implemented.")

def show_growth_graph(app):
    # Placeholder for growth graph logic
    QMessageBox.information(app, "Growth Graph", "Growth graph functionality not implemented.")

def export_pdf(app):
    # Placeholder for PDF export logic
    QMessageBox.information(app, "Export PDF", "PDF export functionality not implemented.")

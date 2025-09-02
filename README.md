# Personal Finance Tracker

This project is a personal finance tracking application:
- **Qt for Python version** (`main_qt.py`): Modern GUI with similar features, using PySide6 for a richer user experience.

## Features
- Add monthly finance data (salary, bills, rent, expenses, debt)
- Calculate savings and investment potential
- Visualize monthly trends and investment growth
- Export finance summary to PDF
- View detailed calculation logs
- Delete entries and clear the database

## Requirements
- Python 3.8+
- `matplotlib`
- `fpdf`
- `PySide6` (for Qt version)

Install dependencies:
```bash
pip install matplotlib fpdf PySide6
```

## Usage
- **Qt version:**
    ```bash
    python main_qt.py
    ```

## Project Structure
- `main_qt.py`: Qt for Python application
- `finance_data.json`: Saved finance data
- `finance_report.pdf`: Exported PDF report

## License
MIT

---
Feel free to fork, modify, and contribute!

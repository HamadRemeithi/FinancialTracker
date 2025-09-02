# Personal Finance Tracker

This project is a personal finance tracking application:
- **Qt for Python version** (`main_qt.py`): Modern GUI with similar features, using PySide6 for a richer user experience.

## Features

## Requirements

Install dependencies:
pip install matplotlib fpdf PySide6

## Usage
- **Stable Qt version:**
    ```bash
    python main_qt.py
    ```
- **Modular version:**
    ```bash
    python run.py
    ```
## Usage
- **Qt version:**
## Project Structure
- `main_qt.py`: Stable Qt for Python application (all-in-one)
- `run.py`: Modular entry point (uses modularized UI and logic)
- `ui.py`: Tab and widget setup logic
- `binance_dashboard.py`: Binance wallet dashboard logic
- `finance_logic.py`: Finance calculations and data management
- `finance_data.json`: Saved finance data
- `finance_report.pdf`: Exported PDF report

## Project Structure
- `main_qt.py`: Qt for Python application
- `finance_data.json`: Saved finance data
---
## Recent Changes
- Added modular entry point `run.py` for maintainable codebase
- Modularized UI and logic into `ui.py`, `binance_dashboard.py`, and `finance_logic.py`
- `run.py` now launches the full-featured app with the same UI theme and functionality as the stable release

Feel free to fork, modify, and contribute!
## License
MIT

---
Feel free to fork, modify, and contribute!

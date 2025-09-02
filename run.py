import sys

from PySide6.QtWidgets import QApplication
from main_qt import FinanceApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = FinanceApp()
    win.resize(700, 900)
    win.show()
    sys.exit(app.exec())

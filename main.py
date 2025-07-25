# main.py

import sys
import os

# این چند خط کد مشکل را حل می‌کند
# Add the project's root directory to the Python path
# This ensures that modules in subdirectories (like ui, database) can be found
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from PySide6.QtWidgets import QApplication
from ui.main_window import EpubReader

if __name__ == "__main__":
    app = QApplication(sys.argv)
    reader = EpubReader()
    reader.show()
    sys.exit(app.exec())

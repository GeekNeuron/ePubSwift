# main.py
import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import EpubReader

if __name__ == "__main__":
    app = QApplication(sys.argv)
    reader = EpubReader()
    reader.show()
    sys.exit(app.exec())

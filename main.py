import sys
import os
from PyQt6.QtWidgets import QApplication
from core.database_manager import DatabaseManager
from core.translator import Translator
from ui.main_window import MainWindow

def load_stylesheet():
    """Loads the QSS stylesheet from the assets folder."""
    style_path = os.path.join(os.path.dirname(__file__), 'assets', 'styles', 'dark_theme.qss')
    try:
        with open(style_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print("Stylesheet not found: dark_theme.qss")
        return ""

def main():
    """
    The main function to initialize and run the PyQt application.
    """
    app = QApplication(sys.argv)
    
    stylesheet = load_stylesheet()
    if stylesheet:
        app.setStyleSheet(stylesheet)
    
    db_manager = DatabaseManager()
    
    lang = db_manager.get_setting("language", "en")
    translator = Translator(lang)
    
    window = MainWindow(db_manager, translator)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

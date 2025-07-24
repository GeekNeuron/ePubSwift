import os
from PyQt6.QtWidgets import (
    QMainWindow, QListWidget, QTextBrowser, QSplitter,
    QFileDialog, QApplication, QMessageBox
)
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtCore import Qt
from core.epub_handler import EpubHandler
from ui.settings_dialog import SettingsDialog

class MainWindow(QMainWindow):
    def __init__(self, db_manager, translator):
        super().__init__()
        self.db_manager = db_manager
        self.translator = translator
        self.epub_handler = None
        self.current_book_path = None
        
        self._setup_ui()
        self._create_actions()
        self._create_menu_bar()
        self._apply_translations()

        self.load_initial_settings()

    def _setup_ui(self):
        self.setGeometry(100, 100, 1200, 800)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)

        self.chapter_list_widget = QListWidget()
        self.chapter_list_widget.currentItemChanged.connect(self.display_chapter)
        splitter.addWidget(self.chapter_list_widget)

        self.content_browser = QTextBrowser()
        self.content_browser.setOpenExternalLinks(True)
        splitter.addWidget(self.content_browser)
        splitter.setSizes([300, 900])

    def _create_actions(self):
        self.open_action = QAction(self)
        self.open_action.triggered.connect(self.open_epub_file)
        
        self.settings_action = QAction(self)
        self.settings_action.triggered.connect(self.open_settings)

        self.exit_action = QAction(self)
        self.exit_action.triggered.connect(self.close)

    def _create_menu_bar(self):
        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu("")
        self.file_menu.addAction(self.open_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)
        
        self.settings_menu = self.menu_bar.addMenu("")
        self.settings_menu.addAction(self.settings_action)

    def _apply_translations(self):
        """Applies the current language to all UI elements."""
        self.setWindowTitle(self.translator.get_text("app_title"))
        self.file_menu.setTitle(self.translator.get_text("file_menu"))
        self.settings_menu.setTitle(self.translator.get_text("settings_menu"))
        self.open_action.setText(self.translator.get_text("open_epub"))
        self.exit_action.setText(self.translator.get_text("exit"))
        self.settings_action.setText(self.translator.get_text("settings_title"))
    
    def load_initial_settings(self):
        """Loads last-used book, font, and other settings on startup."""
        font_family = self.db_manager.get_setting("font_family", "Vazirmatn")
        self.apply_font(font_family)

        last_book_path = self.db_manager.get_setting("last_book_path")
        if last_book_path and os.path.exists(last_book_path):
            self.load_book_by_path(last_book_path)

    def open_epub_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open ePub File", "", "ePub Files (*.epub)")
        if file_path:
            self.load_book_by_path(file_path)

    def load_book_by_path(self, file_path):
        try:
            self.epub_handler = EpubHandler(file_path)
            self.current_book_path = file_path
            self.db_manager.set_setting("last_book_path", file_path)
            self.load_book_ui()
        except Exception as e:
            QMessageBox.critical(self, 
                                 self.translator.get_text("error_title"),
                                 self.translator.get_text("error_loading_book").format(error=e))
    
    def load_book_ui(self):
        title = self.epub_handler.get_metadata('title')
        window_title = title[0] if title else self.translator.get_text("app_title")
        self.setWindowTitle(window_title)

        self.chapter_list_widget.clear()
        chapters = self.epub_handler.get_chapters_list()
        for i, chap in enumerate(chapters):
            self.chapter_list_widget.addItem(f"{i + 1}. {chap.get('href', 'Untitled')}")
        
        last_chapter = self.db_manager.get_progress(self.current_book_path)
        if 0 <= last_chapter < self.chapter_list_widget.count():
            self.chapter_list_widget.setCurrentRow(last_chapter)
        elif self.chapter_list_widget.count() > 0:
            self.chapter_list_widget.setCurrentRow(0)

    def display_chapter(self):
        if not self.epub_handler: return
        current_row = self.chapter_list_widget.currentRow()
        if current_row < 0: return

        html_content = self.epub_handler.get_chapter_content(current_row)
        if html_content:
            self.content_browser.setHtml(html_content)
            self.db_manager.set_progress(self.current_book_path, current_row)

    def open_settings(self):
        dialog = SettingsDialog(self.db_manager, self.translator, self)
        dialog.settings_changed.connect(self.on_settings_changed)
        dialog.exec()

    def on_settings_changed(self):
        lang_code = self.db_manager.get_setting("language", "en")
        self.translator.load_language(lang_code)
        self._apply_translations()
        
        font_family = self.db_manager.get_setting("font_family", "Vazirmatn")
        self.apply_font(font_family)
        QMessageBox.information(self, 
            self.translator.get_text("settings_changed_title"), 
            self.translator.get_text("settings_changed_message"))

    def apply_font(self, font_family):
        """Applies the selected font to the content browser and injects theme CSS."""
        base_font = QFont(font_family)
        base_font.setPointSize(10)
        QApplication.setFont(base_font)

        content_font = QFont(font_family)
        content_font.setPointSize(14)
        self.content_browser.setFont(content_font)

        font_name = font_family.replace('"', '\\"')
        text_color = "#c9d1d9"
        link_color = "#58a6ff"
        body_bg = "#0d1117"
        font_stack = f"'{font_name}', Vazirmatn, sans-serif"

        # Set document direction based on language
        direction = "rtl" if self.translator.lang_code == "fa" else "ltr"

        css = f"""
        <style>
            body {{
                font-family: {font_stack} !important;
                line-height: 1.7;
                color: {text_color};
                background-color: {body_bg};
                padding: 25px;
                direction: {direction};
            }}
            a {{ color: {link_color}; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            img, svg {{ max-width: 100%; height: auto; border-radius: 4px; }}
        </style>
        """
        self.content_browser.document().setDefaultStyleSheet(css)
        self.display_chapter()
    
    def closeEvent(self, event):
        """Saves progress before closing the application."""
        if self.epub_handler and self.current_book_path:
            current_row = self.chapter_list_widget.currentRow()
            self.db_manager.set_progress(self.current_book_path, current_row)
        self.db_manager.close()
        event.accept()

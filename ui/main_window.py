import os
from PySide6.QtWidgets import (
    QMainWindow, QFileDialog, QTextBrowser, QListWidget, QWidget,
    QVBoxLayout, QHBoxLayout, QSplitter, QTabWidget, QListWidgetItem
)
from PySide6.QtGui import QAction, QKeySequence, QFontDatabase, QFont, QIcon
from PySide6.QtCore import Qt, QThread, QTimer

from bs4 import BeautifulSoup
from database.database_manager import DatabaseManager
from ui.widgets import ClickableProgressBar, LoadingSpinner
from ui.workers import BookLoaderWorker
from utils.helpers import is_rtl

class EpubReader(QMainWindow):
    def __init__(self):
        super().__init__()
        # Enable Drag and Drop functionality for the main window
        self.setAcceptDrops(True)
        
        self.db_manager = DatabaseManager()
        self.book = None
        self.chapters = []
        self.library = []
        self.current_book_path = None
        self.app_name = "ePub Swift"
        self.author_name = "GeekNeuron"
        self.total_book_len = 0
        self.chapter_lens = []
        self.cumulative_lens = []
        self.worker_thread = None
        
        self.load_assets()
        self.update_window_title()
        self.setWindowState(Qt.WindowMaximized)
        
        self.init_ui()
        self.apply_styles()
        self.load_library_from_db()
        self.show_welcome_message()

    # --- Drag and Drop Event Handlers ---

    def dragEnterEvent(self, event):
        """This event is called when a dragged object enters the window."""
        if event.mimeData().hasUrls():
            # Check if at least one of the files is an .epub file
            for url in event.mimeData().urls():
                if url.isLocalFile() and url.toLocalFile().lower().endswith('.epub'):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event):
        """This event is called when a dragged object is dropped on the window."""
        urls = event.mimeData().urls()
        if urls:
            for url in urls:
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if file_path.lower().endswith('.epub'):
                        # Load the first valid .epub file found
                        self.load_book(file_path)
                        event.acceptProposedAction()
                        return
        event.ignore()
        
    def load_library_from_db(self):
        self.library = self.db_manager.load_library()
        self.refresh_library_list()
        
    def closeEvent(self, event):
        """Saves progress when the application is about to close."""
        self.db_manager.save_progress(self.current_book_path, self.get_current_char_position())
        event.accept()

    def init_ui(self):
        self.loading_spinner = LoadingSpinner(self)
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        open_action = QAction("Load EPUB (Ctrl+O)", self)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)
        menu_bar.addMenu("Edit")
        menu_bar.addMenu("Settings")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        self.left_panel = QTabWidget()
        self.left_panel.setMinimumWidth(250)
        self.left_panel.setMaximumWidth(450)
        self.toc_list = QListWidget()
        self.toc_list.setAlternatingRowColors(True)
        self.toc_list.currentItemChanged.connect(self.display_chapter)
        self.library_list = QListWidget()
        self.library_list.setAlternatingRowColors(True)
        self.library_list.itemClicked.connect(self.load_book_from_library)
        self.left_panel.addTab(self.toc_list, "Contents")
        self.left_panel.addTab(self.library_list, "Library")
        right_panel_widget = QWidget()
        right_layout = QVBoxLayout(right_panel_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        self.text_display = QTextBrowser()
        self.text_display.setOpenExternalLinks(True)
        self.text_display.verticalScrollBar().valueChanged.connect(self.update_global_progress)
        self.progress_bar = ClickableProgressBar()
        self.progress_bar.jump_requested.connect(self.jump_to_position)
        right_layout.addWidget(self.text_display)
        right_layout.addWidget(self.progress_bar)
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.left_panel)
        splitter.addWidget(right_panel_widget)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setHandleWidth(2)
        main_layout.addWidget(splitter)
        
    def apply_styles(self):
        self.setStyleSheet("""
            QProgressBar {
                border: none; border-radius: 4px; background-color: #e0e0e0; max-height: 14px;
            }
            QProgressBar::chunk { background-color: #345B9A; border-radius: 4px; }
            QMenu { background-color: #ffffff; border: 1px solid #dcdde1; border-radius: 8px; padding: 5px; }
            QMenu::item { padding: 8px 25px 8px 20px; border-radius: 6px; }
            QMenu::item:selected { background-color: #345B9A; color: white; }
            QMenuBar { background-color: #f2f3f7; border-bottom: 1px solid #dcdde1; padding: 2px; }
            QMenuBar::item { background-color: transparent; padding: 6px 12px; border-radius: 6px; }
            QMenuBar::item:selected { background-color: #dcdde1; }
            QMainWindow, QWidget { background-color: #f2f3f7; }
            QTabWidget::pane { border: none; }
            QTabWidget::tab-bar { alignment: center; }
            QTabBar::tab { background: #e1e5ea; color: #555; padding: 8px 20px; border-top-left-radius: 6px; border-top-right-radius: 6px; margin: 0 2px; }
            QTabBar::tab:selected { background: #ffffff; color: #000; }
            QListWidget { background-color: #ffffff; color: #2c3e50; border: none; border-radius: 8px; padding: 5px; }
            QListWidget::item { padding: 8px; border-radius: 4px; }
            QListWidget::item:alternate { background-color: #f8f9fa; }
            QListWidget::item:selected { background-color: #345B9A; color: white; }
            QTextBrowser { background-color: #ffffff; border: none; border-radius: 8px; padding: 20px; font-size: 16px; color: #34495e; }
            QScrollBar:vertical { border: none; background: #f8f9fa; width: 10px; margin: 0; border-radius: 5px; }
            QScrollBar::handle:vertical { background: #bdc3c7; min-height: 20px; border-radius: 5px; }
            QScrollBar::handle:vertical:hover { background: #95a5a6; }
        """)

    def show_welcome_message(self):
        """Displays a styled welcome message with key-like buttons and new instructions."""
        self.text_display.setHtml("""
            <style>
                .container {
                    text-align: center;
                    color: #7f8c8d;
                    font-family: sans-serif;
                    padding-top: 15%;
                }
                .container h1 {
                    font-size: 22px;
                    font-weight: 500;
                    color: #2c3e50;
                }
                .container p {
                    font-size: 13px;
                    line-height: 1.6;
                }
                .key {
                    background-color: #e9e9ed;
                    border: 1px solid #d1d1d1;
                    border-radius: 4px;
                    padding: 2px 6px;
                    font-size: 11px;
                    font-family: "Segoe UI", "Vazirmatn", monospace;
                    color: #333;
                }
            </style>
            <div class='container'>
                <h1>Welcome to ePub Swift</h1>
                <p>Load a book from the <span class='key'>File</span> menu, press <span class='key'>Ctrl</span> + <span class='key'>O</span></p>
                <p>or simply <b>drag and drop</b> an EPUB file here.</p>
            </div>
        """)
        self.text_display.setAlignment(Qt.AlignCenter)

    def load_book(self, file_path):
        if not file_path:
            return
        
        # Save progress of the PREVIOUS book before loading a new one
        self.db_manager.save_progress(self.current_book_path, self.get_current_char_position())
        
        self.toc_list.clear()
        self.text_display.clear()
        self.progress_bar.setValue(0)
        self.current_book_path = file_path
        
        self.loading_spinner.start_animation()
        
        self.worker_thread = QThread()
        self.worker = BookLoaderWorker(file_path)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_book_data_loaded)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.start()

    def on_book_data_loaded(self, result):
        self.loading_spinner.stop_animation()
        if 'error' in result:
            self.text_display.setHtml(f"<h1>Error Opening Book</h1><p>{result['error']}</p>")
            return
        
        self.book = result['book']
        self.chapters = result['chapters']
        self.total_book_len = result['total_len']
        self.chapter_lens = result['chap_lens']
        self.cumulative_lens = result['cum_lens']

        self.update_window_title(result['title'])
        self.update_library(self.current_book_path, result['title'])
        
        toc_is_rtl = is_rtl(self.chapters[0]['title'] if self.chapters else "")
        self.toc_list.setLayoutDirection(Qt.RightToLeft if toc_is_rtl else Qt.LeftToRight)

        self.toc_list.addItems([f"{i+1}. {c['title']}" for i, c in enumerate(self.chapters)])

        if self.toc_list.count() > 0:
            self.toc_list.setCurrentRow(0)
            
            book_in_lib = next((b for b in self.library if b['path'] == self.current_book_path), None)
            if book_in_lib and book_in_lib.get('last_read_pos', 0) > 0 and self.total_book_len > 0:
                percentage = (book_in_lib['last_read_pos'] / self.total_book_len) * 100
                self.jump_to_position(percentage)
        self.worker_thread = None


    def display_chapter(self, current_item):
        if not current_item or not self.book: return
        self.update_global_progress()
        
        selected_index = self.toc_list.row(current_item)
        if not (0 <= selected_index < len(self.chapters)): return
        
        chapter_info = self.chapters[selected_index]
        item = self.book.get_item_with_href(chapter_info['href'])
        content_bytes = item.get_content()
        soup = BeautifulSoup(content_bytes, 'html.parser')
        
        body_tag = soup.find('body')
        if body_tag:
            direction = "rtl" if is_rtl(body_tag.get_text()) else "ltr"
            body_tag['dir'] = direction
        
        style_tag = soup.new_tag('style')
        style_tag.string = "body { font-family: 'Vazirmatn', sans-serif !important; }"
        head = soup.find('head') or soup.new_tag('head')
        if not head.parent: soup.insert(0, head)
        head.append(style_tag)
        
        self.text_display.setHtml(soup.prettify())
        self.text_display.verticalScrollBar().setValue(0)

    def get_current_char_position(self):
        if not self.book or self.total_book_len == 0 or self.toc_list.currentRow() < 0:
            return 0
        current_chapter_index = self.toc_list.currentRow()
        if not (0 <= current_chapter_index < len(self.cumulative_lens) - 1): return 0
        scrollbar = self.text_display.verticalScrollBar()
        max_val = scrollbar.maximum()
        scroll_progress = (scrollbar.value() / max_val) if max_val > 0 else 0
        preceding_len = self.cumulative_lens[current_chapter_index]
        current_chapter_len = self.chapter_lens[current_chapter_index]
        return int(preceding_len + (scroll_progress * current_chapter_len))

    def update_global_progress(self):
        current_char_pos = self.get_current_char_position()
        if self.total_book_len > 0:
            global_percentage = (current_char_pos / self.total_book_len) * 100
        else:
            global_percentage = 0
        self.progress_bar.setValue(int(global_percentage))

    def jump_to_position(self, percentage):
        if not self.book or self.total_book_len == 0: return
        target_char_pos = self.total_book_len * (percentage / 100)
        target_chapter_index = -1
        for i in range(len(self.cumulative_lens) - 1):
            if self.cumulative_lens[i] <= target_char_pos < self.cumulative_lens[i+1]:
                target_chapter_index = i
                break
        if target_chapter_index == -1 and target_char_pos >= self.cumulative_lens[-1]:
             target_chapter_index = len(self.cumulative_lens) - 2
        if target_chapter_index < 0: return
        if self.toc_list.currentRow() != target_chapter_index:
            self.toc_list.blockSignals(True)
            self.toc_list.setCurrentRow(target_chapter_index)
            self.toc_list.blockSignals(False)
            self.display_chapter(self.toc_list.currentItem())
        
        QTimer.singleShot(50, lambda: self.scroll_to_position_in_chapter(target_char_pos))

    def scroll_to_position_in_chapter(self, target_char_pos):
        current_chapter_index = self.toc_list.currentRow()
        if not (0 <= current_chapter_index < len(self.chapter_lens)): return

        preceding_len = self.cumulative_lens[current_chapter_index]
        current_chapter_len = self.chapter_lens[current_chapter_index]
        
        if current_chapter_len > 0:
            progress_in_chapter = (target_char_pos - preceding_len) / current_chapter_len
            scrollbar = self.text_display.verticalScrollBar()
            new_scroll_value = int(progress_in_chapter * scrollbar.maximum())
            scrollbar.setValue(new_scroll_value)

    def load_assets(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(base_path, '..', 'assets', 'fonts', 'Vazirmatn-Medium.ttf')
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                font_families = QFontDatabase.applicationFontFamilies(font_id)
                app_font = QFont(font_families[0], 10)
                QApplication.instance().setFont(app_font)
        icon_path = os.path.join(base_path, '..', 'assets', 'icons', 'app_icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def update_window_title(self, book_title=None):
        if book_title:
            self.setWindowTitle(f"{book_title} - {self.app_name} ({self.author_name})")
        else:
            self.setWindowTitle(f"{self.app_name} ({self.author_name})")

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select an EPUB File", "", "EPUB Files (*.epub)")
        self.load_book(file_path)

    def update_library(self, file_path, book_title):
        if any(b['path'] == file_path for b in self.library):
            return

        new_book_data = {'path': file_path, 'title': book_title, 'pages': len(self.chapters), 'last_read_pos': 0}
        self.library.append(new_book_data)
        self.db_manager.add_or_update_book(new_book_data)
        self.refresh_library_list()

    def refresh_library_list(self):
        self.library_list.clear()
        for book in self.library:
            item_text = f"📖 {book['title']}\n📄 Chapters: {book['pages']}"
            list_item = QListWidgetItem(item_text)
            list_item.setData(Qt.UserRole, book['path'])
            self.library_list.addItem(list_item)
    
    def load_book_from_library(self, item):
        self.db_manager.save_progress(self.current_book_path, self.get_current_char_position())
        
        file_path = item.data(Qt.UserRole)
        if file_path and file_path != self.current_book_path:
            self.load_book(file_path)

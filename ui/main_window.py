from PyQt6.QtWidgets import (
    QMainWindow, QListWidget, QTextBrowser, QSplitter,
    QFileDialog, QApplication, QMessageBox
)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
from core.epub_handler import EpubHandler

class MainWindow(QMainWindow):
    """
    The main window for the ePub Swift application.
    It contains the chapter list, content viewer, and menu bar.
    """
    def __init__(self):
        super().__init__()
        self.epub_handler = None
        self.setWindowTitle("ePub Swift")
        self.setGeometry(100, 100, 1200, 800)
        self._setup_ui()
        self._create_actions()
        self._create_menu_bar()

    def _setup_ui(self):
        """Sets up the main user interface layout."""
        # Create a splitter to allow resizing between chapter list and content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)

        # Left side: Chapter List
        self.chapter_list_widget = QListWidget()
        self.chapter_list_widget.currentItemChanged.connect(self.display_chapter)
        splitter.addWidget(self.chapter_list_widget)

        # Right side: Content Viewer
        self.content_browser = QTextBrowser()
        self.content_browser.setOpenExternalLinks(True) # Open links in system browser
        splitter.addWidget(self.content_browser)

        # Set initial sizes for the splitter panes
        splitter.setSizes([300, 900])

    def _create_actions(self):
        """Creates the actions for the menu bar."""
        self.open_action = QAction("&Open ePub...", self)
        self.open_action.triggered.connect(self.open_epub_file)
        
        self.exit_action = QAction("E&xit", self)
        self.exit_action.triggered.connect(self.close)

    def _create_menu_bar(self):
        """Creates the main menu bar."""
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(self.open_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

    def open_epub_file(self):
        """Opens a file dialog to select an ePub file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open ePub File", "", "ePub Files (*.epub)"
        )
        if file_path:
            try:
                self.epub_handler = EpubHandler(file_path)
                self.load_book()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not load the book: {e}")

    def load_book(self):
        """Loads the book's metadata and chapter list into the UI."""
        if not self.epub_handler:
            return
            
        # Set window title
        title = self.epub_handler.get_metadata('title')
        creator = self.epub_handler.get_metadata('creator')
        window_title = title[0] if title else "ePub Swift"
        if creator:
            window_title += f" by {creator[0]}"
        self.setWindowTitle(window_title)

        # Clear previous content
        self.chapter_list_widget.clear()
        self.content_browser.clear()

        # Populate chapter list
        chapters = self.epub_handler.get_chapters_list()
        for i, chap in enumerate(chapters):
            # Using href as a simple title for now. We will improve this later.
            display_title = f"{i + 1}. {chap.get('href', 'Untitled')}"
            self.chapter_list_widget.addItem(display_title)
        
        # Display the first chapter by default
        if self.chapter_list_widget.count() > 0:
            self.chapter_list_widget.setCurrentRow(0)

    def display_chapter(self):
        """Displays the content of the selected chapter."""
        if not self.epub_handler:
            return
            
        current_row = self.chapter_list_widget.currentRow()
        if current_row < 0:
            return

        html_content = self.epub_handler.get_chapter_content(current_row)
        if html_content:
            # QTextBrowser can render basic HTML
            self.content_browser.setHtml(html_content)

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import os

class EpubHandler:
    """A class to handle opening and reading ePub files."""

    def __init__(self, epub_path):
        """
        Constructor that takes the path to an ePub file.
        """
        if not os.path.exists(epub_path):
            raise FileNotFoundError(f"ePub file not found at '{epub_path}'.")
        self.epub_path = epub_path
        self.book = None
        self.chapters = []
        self.open_book()

    def open_book(self):
        """Opens the ePub file using the ebooklib library."""
        try:
            self.book = epub.read_epub(self.epub_path)
            self._parse_chapters()
        except Exception as e:
            print(f"Error opening book: {e}")
            self.book = None

    def get_metadata(self, tag_name):
        """Extracts metadata (e.g., 'title', 'creator') from the book."""
        if not self.book:
            return []
        
        metadata = self.book.get_metadata('DC', tag_name)
        return [data[0] for data in metadata] if metadata else []

    def _parse_chapters(self):
        """Parses and orders the chapters from the book's spine."""
        if not self.book:
            return

        self.chapters = []
        for item in self.book.spine:
            manifest_item = self.book.get_item_with_href(item[0])
            if manifest_item:
                self.chapters.append(manifest_item)
    
    def get_chapters_list(self):
        """Returns a list of chapter dictionaries with their ID and href."""
        return [{"id": ch.id, "href": ch.file_name} for ch in self.chapters]

    def get_chapter_content(self, chapter_index):
        """Returns the raw HTML content of a specific chapter."""
        if not self.book or not (0 <= chapter_index < len(self.chapters)):
            return None
        
        chapter_item = self.chapters[chapter_index]
        return chapter_item.get_body_content().decode('utf-8', 'ignore')

    def clean_html_content(self, html_content):
        """
        Converts HTML content into plain, readable text using BeautifulSoup.
        (Note: This method is not used by the final UI, which renders HTML directly).
        """
        if not html_content:
            return ""
        
        soup = BeautifulSoup(html_content, 'lxml')
        body = soup.find('body')
        if not body:
            return ""

        text_parts = [p.get_text() for p in body.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
        return "\n\n".join(text_parts)

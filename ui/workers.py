# ui/workers.py
import os
from PySide6.QtCore import QObject, Signal
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

class BookLoaderWorker(QObject):
    finished = Signal(dict)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        """
        Loads the EPUB and calculates progress data using a much faster method
        by reading file sizes from the zip archive instead of parsing every file.
        """
        try:
            book = epub.read_epub(self.file_path, ignore_ncx=True)
            
            # --- Metadata Extraction (fast) ---
            book_title_meta = book.get_metadata('DC', 'title')
            title = book_title_meta[0][0] if book_title_meta else os.path.basename(self.file_path)
            chapters = [{'title': item.title, 'href': item.href} for item in book.toc if isinstance(item, epub.Link)]

            # --- OPTIMIZED Progress Calculation (very fast) ---
            # Create a map of file names to their uncompressed sizes
            size_map = {info.filename: info.file_size for info in book.epub.infolist()}
            
            total_len = 0
            chap_lens = []
            cum_lens = [0]
            
            # Use the book's spine to determine the reading order and content length
            spine_items = [book.get_item_with_id(item_id) for item_id, _ in book.spine]
            
            for item in spine_items:
                # Get the file size from the map instead of reading/parsing the file
                if item and item.file_name in size_map:
                    # Use the file size as a proxy for content length
                    length = size_map[item.file_name]
                    chap_lens.append(length)
                    total_len += length
            
            cumulative = 0
            for length in chap_lens:
                cumulative += length
                cum_lens.append(cumulative)
            
            result = {
                'book': book, 'title': title, 'chapters': chapters, 'total_len': total_len, 
                'chap_lens': chap_lens, 'cum_lens': cum_lens
            }
            self.finished.emit(result)
        except Exception as e:
            self.finished.emit({'error': str(e)})

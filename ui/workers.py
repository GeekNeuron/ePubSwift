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
        Loads the EPUB using the stable method. This is slightly slower but
        compatible with all versions of the ebooklib.
        """
        try:
            # Reverted: The problematic 'ignore_ncx' argument is removed.
            book = epub.read_epub(self.file_path)
            
            # --- Metadata Extraction ---
            book_title_meta = book.get_metadata('DC', 'title')
            title = book_title_meta[0][0] if book_title_meta else os.path.basename(self.file_path)
            chapters = [{'title': item.title, 'href': item.href} for item in book.toc if isinstance(item, epub.Link)]

            # --- Stable Progress Calculation ---
            total_len = 0
            chap_lens = []
            cum_lens = [0]
            
            spine_items = [book.get_item_with_id(item_id) for item_id, _ in book.spine]
            
            for item in spine_items:
                if item and item.get_type() == ebooklib.ITEM_DOCUMENT:
                    # This is the stable method: read content and get text length.
                    content = item.get_content()
                    text_len = len(BeautifulSoup(content, 'html.parser').get_text(strip=True))
                    chap_lens.append(text_len)
                    total_len += text_len
            
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

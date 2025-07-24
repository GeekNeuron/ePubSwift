import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import os

class EpubHandler:
    """
    کلاسی برای مدیریت باز کردن و خواندن فایل‌های ePub.
    """
    def __init__(self, epub_path):
        """
        سازنده کلاس که مسیر فایل ePub را دریافت می‌کند.
        """
        if not os.path.exists(epub_path):
            raise FileNotFoundError(f"فایل ePub در مسیر '{epub_path}' یافت نشد.")
        self.epub_path = epub_path
        self.book = None
        self.chapters = []
        self.open_book()

    def open_book(self):
        """
        کتاب ePub را با استفاده از کتابخانه ebooklib باز می‌کند.
        """
        try:
            self.book = epub.read_epub(self.epub_path)
            self._parse_chapters()
        except Exception as e:
            print(f"خطا در باز کردن کتاب: {e}")
            self.book = None

    def get_metadata(self, tag_name):
        """
        متادیتا (اطلاعات شناسنامه‌ای) کتاب را بر اساس نام تگ استخراج می‌کند.
        مثال: 'title', 'creator', 'publisher'
        """
        if not self.book:
            return []
        
        metadata = self.book.get_metadata('DC', tag_name)
        return [data[0] for data in metadata] if metadata else []

    def _parse_chapters(self):
        """
        فصل‌های کتاب را از قسمت spine استخراج کرده و مرتب می‌کند.
        """
        if not self.book:
            return

        self.chapters = []
        # spine شامل ترتیب محتوای اصلی کتاب است
        for item in self.book.spine:
            # item.href لینک به فایل فصل است
            manifest_item = self.book.get_item_with_href(item[0])
            if manifest_item:
                self.chapters.append(manifest_item)
    
    def get_chapters_list(self):
        """
        یک لیست از عنوان و لینک فصل‌ها را برمی‌گرداند.
        (توجه: استخراج عنوان واقعی نیازمند خواندن فایل navigation است که در مراحل بعد اضافه می‌شود)
        """
        return [{"id": ch.id, "href": ch.file_name} for ch in self.chapters]

    def get_chapter_content(self, chapter_index):
        """
        محتوای یک فصل خاص را به صورت HTML خام برمی‌گرداند.
        """
        if not self.book or chapter_index < 0 or chapter_index >= len(self.chapters):
            return None
        
        chapter_item = self.chapters[chapter_index]
        return chapter_item.get_body_content().decode('utf-8')

    def clean_html_content(self, html_content):
        """
        محتوای HTML را به متن ساده و خوانا تبدیل می‌کند.
        تگ‌های HTML را حذف کرده و فقط متن را نگه می‌دارد.
        """
        if not html_content:
            return ""
        
        soup = BeautifulSoup(html_content, 'lxml')
        # استخراج تمام متن از تگ body
        body = soup.find('body')
        if not body:
            return ""

        # پاراگراف‌ها را با یک خط جدید از هم جدا می‌کنیم
        text_parts = [p.get_text() for p in body.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
        return "\n\n".join(text_parts)

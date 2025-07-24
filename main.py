from core.epub_handler import EpubHandler

def test_epub_reader():
    # --- مهم: مسیر فایل کتاب خود را اینجا قرار دهید ---
    # مثال: "C:/Users/YourUser/Documents/mybook.epub"
    epub_path = "path/to/your/book.epub" 
    
    try:
        # یک نمونه از کلاس پردازشگر کتاب ایجاد می‌کنیم
        handler = EpubHandler(epub_path)
        
        # استخراج و نمایش اطلاعات کتاب
        print("--- اطلاعات کتاب ---")
        title = handler.get_metadata('title')
        creator = handler.get_metadata('creator')
        print(f"عنوان: {title[0] if title else 'نامشخص'}")
        print(f"نویسنده: {creator[0] if creator else 'نامشخص'}")
        print("-" * 20)

        # دریافت و نمایش لیست فصل‌ها
        chapters = handler.get_chapters_list()
        print(f"تعداد فصل‌ها: {len(chapters)}")
        
        if chapters:
            # نمایش محتوای فصل اول به عنوان نمونه
            print("\n--- محتوای فصل اول (متن پاک‌سازی شده) ---")
            first_chapter_html = handler.get_chapter_content(0)
            cleaned_text = handler.clean_html_content(first_chapter_html)
            
            # نمایش 500 کاراکتر اول
            print(cleaned_text[:500] + "...")
        
    except FileNotFoundError as e:
        print(e)
        print("لطفاً مسیر فایل ePub خود را در متغیر 'epub_path' در فایل main.py وارد کنید.")
    except Exception as e:
        print(f"یک خطای غیرمنتظره رخ داد: {e}")

if __name__ == "__main__":
    test_epub_reader()

import fitz
import io


def book2page(book: str, page_num: int) -> io.BytesIO:
    file = io.BytesIO()
    doc = fitz.open(book)
    page = doc.loadPage(page_num)
    page.insertText((3, 10), "github.com/semwai")
    zoom = 1.5
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    file.write(pix.pillowData('jpeg', quality=80))
    file.seek(0)
    return file



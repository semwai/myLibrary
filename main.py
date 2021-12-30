from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uvicorn

import os
from dotenv import load_dotenv
import io 

from typing import Optional
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

import fitz

from book2page import book2page
from books import books
from models import Page, Book


load_dotenv()

engine = create_engine(os.getenv('DB_CONNECTION'), echo=False)
session = sessionmaker(bind=engine)()
from models import metadata
metadata.create_all(engine)
 

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://project.test",
    "http://api.project.test"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, allow_methods=["*"],
    allow_headers=["*"], )


@app.get("/")
def read_root():
    return {"Hello": "World!"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}




@app.get("/book/{book_id}/", responses={ 200: {"content": {"image/jpeg": {}}}} )
@app.get("/book/{book_id}/{page}", responses={ 200: {"content": {"image/jpeg": {}}}} )
def get_page(book_id: int, page: int = 0):
    res = session.query(Page).filter_by(book_id=book_id, number=page).first()
    file = io.BytesIO()
    file.write(res.data)
    file.seek(0)
    return StreamingResponse(file, media_type="image/jpeg")


@app.post("/book")
async def post_book(name: str, author: str, file: UploadFile = File(...)):
    data = await file.read()
    book = fitz.open(stream=data, filetype="pdf")
    print(dir(file))
    for i, page in enumerate(book):
        raw_data = page.get_pixmap().pil_tobytes('jpeg', quality=80)
        elem = Page(number=i, book_id=1, data=raw_data)
        session.add(elem)
    session.commit()
    return {'ok':'ok'}


@app.get("/books/")
def get_books():
    return {'books': [{'id': book_id, 'name': name} for book_id, (file, name) in books.items()]}



if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True, debug=True, workers=3, use_colors=True)

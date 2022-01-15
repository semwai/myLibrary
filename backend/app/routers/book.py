import io
from typing import Optional

import fitz
from fastapi import File, UploadFile, BackgroundTasks, HTTPException, Depends, APIRouter, status
from fastapi.responses import StreamingResponse
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import load_only, Session

from ..models import Page, Book, User as UserModel, UserProgress
from ..schemas import BookInfo
from ..session import get_db

book_router = APIRouter()


@book_router.get("/page/{book_id}", tags=['Book'],
                 description="get page as jpg file and save current `page: int` to database.\
                             if `page` is `None` - get last opened or first page", response_class=StreamingResponse)
def get_page(book_id: int,
             page: Optional[int] = None,
             authorize: AuthJWT = Depends(),
             session: Session = Depends(get_db)):
    authorize.jwt_required()
    current_user = authorize.get_jwt_subject()
    db_user = session.query(UserModel).filter_by(name=current_user).one()
    progress = session.query(UserProgress).filter_by(user_id=db_user.id, book_id=book_id).first()
    # Update user page offset or create new for first query
    if progress is None:
        if page is not None:
            progress = UserProgress(user_id=db_user.id, book_id=book_id, page=page)
        else:
            progress = UserProgress(user_id=db_user.id, book_id=book_id, page=0)
    elif page is not None:
        progress.page = page
    res = session.query(Page).filter_by(book_id=book_id, number=progress.page).first()
    if res is None:
        raise HTTPException(status_code=404, detail="Page not found")
    try:
        session.add(progress)
        session.commit()
    except IntegrityError:
        raise HTTPException(status_code=404, detail="Book not found")
    file = io.BytesIO()
    file.write(res.data)
    file.seek(0)
    headers = {'page': str(progress.page), 'access-control-expose-headers': '*'}
    return StreamingResponse(file, headers=headers, media_type="image/jpeg")


async def upload_book(name: str, file, session: Session, author: Optional[str] = None):
    data = await file.read()
    db_book = Book(name=name, author=author)  # , raw=data)
    session.add(db_book)
    session.commit()
    book = fitz.open(stream=data, filetype="pdf")
    for i, page in enumerate(book):
        raw_data = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).pil_tobytes('jpeg', quality=70)
        elem = Page(number=i, book_id=db_book.id, data=raw_data)
        session.add(elem)
        session.commit()


@book_router.post("/book", tags=['Book'], status_code=status.HTTP_201_CREATED)
async def post_book(background_tasks: BackgroundTasks,
                    name: str, author: Optional[str] = None,
                    file: UploadFile = File(...),
                    authorize: AuthJWT = Depends(),
                    session: Session = Depends(get_db)):
    authorize.jwt_required()
    background_tasks.add_task(upload_book, name=name, author=author, file=file, session=session)
    return {'name': name, 'author': author}


@book_router.get("/books", tags=['Book'], description="get id of books")
async def post_book(authorize: AuthJWT = Depends(), session: Session = Depends(get_db)):
    authorize.jwt_required()
    fields = ['id', 'name', 'author']
    books = session.query(Book).options(load_only(*fields)).all()
    return {'books': [book.__dict__ for book in books]}


@book_router.get("/book/{id}", tags=['Book'])
async def get_book(id: int, authorize: AuthJWT = Depends(), session: Session = Depends(get_db)):
    res = session.query(Book).filter_by(id=id).first()
    if res is None:
        return HTTPException(status_code=404, detail="Book not found")
    file = io.BytesIO()
    file.write(res.raw)
    file.seek(0)
    return StreamingResponse(file, media_type="application/pdf")


@book_router.get("/book_info/{id}", tags=['Book'], response_model=BookInfo)
async def get_book(id: int, authorize: AuthJWT = Depends(), session: Session = Depends(get_db)):
    authorize.jwt_required()
    book = session.query(Book).filter_by(id=id).first()
    if book is None:
        return HTTPException(status_code=404, detail="Book not found")
    page_count = session.query(Page).filter_by(book_id=book.id).count()
    return BookInfo(name=book.name, author=book.author, pages=page_count)

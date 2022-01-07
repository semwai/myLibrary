import io
from typing import Optional

import fitz
from fastapi import APIRouter
from fastapi import File, UploadFile, BackgroundTasks, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi_jwt_auth import AuthJWT

from ..models import Page, Book, User as UserModel, UserProgress
from ..session import session

book_router = APIRouter()


@book_router.get("/page/{book_id}", tags=['Book'],
                 description="get page and save current `page: int` to database.\
                             if `page` is `None` - get last opened or first page", response_class=StreamingResponse)
def get_page(book_id: int, page: Optional[int] = None, authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    current_user = authorize.get_jwt_subject()
    db_user = session.query(UserModel).filter_by(name=current_user).one()
    progress = session.query(UserProgress).filter_by(user_id=db_user.id, book_id=book_id).first()
    # Update user page offset or create new for first query
    if progress is None:
        progress = UserProgress(user_id=db_user.id, book_id=book_id, page=page)
    else:
        if page is not None:
            progress.page = page
    session.add(progress)
    session.commit()
    res = session.query(Page).filter_by(book_id=book_id, number=progress.page).first()
    if res is None:
        return HTTPException(status_code=404, detail="Page not found")
    file = io.BytesIO()
    file.write(res.data)
    file.seek(0)
    return StreamingResponse(file, media_type="image/jpeg")


async def upload_book(name: str, file, author: Optional[str] = None):
    data = await file.read()
    db_book = Book(name=name, author=author)
    session.add(db_book)
    session.flush()
    book = fitz.open(stream=data, filetype="pdf")
    for i, page in enumerate(book):
        raw_data = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).pil_tobytes('jpeg', quality=80)
        elem = Page(number=i, book_id=db_book.id, data=raw_data)
        session.add(elem)
    session.commit()


@book_router.post("/book", tags=['Book'])
async def post_book(background_tasks: BackgroundTasks,
                    name: str, author: Optional[str] = None,
                    file: UploadFile = File(...),
                    authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    background_tasks.add_task(upload_book, name=name, author=author, file=file)
    return {'name': name, 'author': author}

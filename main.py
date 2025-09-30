from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from model import BookStore
from schemas import BookCreate, BookOut, Book, book_db
from db import SessionLocal, base, engine
from fastapi.middleware.cors import CORSMiddleware
from typing import List


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

base.metadata.create_all(bind = engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

@app.get('/')
async def read_data():
    return {'message': 'hello world'}


@app.post('/create')
async def create_book(book: BookCreate, db: Session = Depends(get_db)):
    new_book = BookStore(
        title = book.title,
        auth_fname = book.auth_fname,
        auth_lname = book.auth_lname,
        rating = book.rating
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

@app.get('/books', response_model=List[BookOut])
async def books(db: Session = Depends(get_db)):
    books = db.query(BookStore).all()
    return books

@app.put('/books/{book_id}', response_model=BookOut)
async def update_book(book_id : int, book: BookCreate, db: Session = Depends(get_db)):
    db_book = db.query(BookStore).filter(BookStore.book_id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not Found...")
    
    for key, value in book.dict().items():
        setattr(db_book, key, value)
    
    db.commit()
    db.refresh(db_book)
    return db_book

@app.delete('/books/{book_id}')
async def delete_book(book_id : int, db: Session = Depends(get_db)):
    db_book = db.query(BookStore).filter(BookStore.book_id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not Found...")
    
    db.delete(db_book)
    db.commit()
    return {'Message': f'Book with ID {book_id} deleted successfully'}
    


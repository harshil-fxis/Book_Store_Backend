from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from model import BookStore
from schemas import BookCreate, BookOut, Book
from db import SessionLocal, base, engine
from fastapi.middleware.cors import CORSMiddleware
from typing import List

#User
from datetime import datetime,timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from model import User
from schemas import UserCreate, UserLogin, UserOut

#Admin
from schemas import AdminCreate, AdminLogin, AdminOut
from model import Admin
from functools import partial

#Review
from schemas import ReviewCreate, ReviewOut
from model import Review

SECRETE_KEY = 'your_secrete_key_12345'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
    
#Users


# Signup endpoint
@app.post("/signup", response_model=UserOut, tags=["Users"])
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password directly here (truncate to 72 chars to avoid bcrypt error)
    hashed_password = pwd_context.hash(user.password[:72])

    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        phone=user.phone
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# Login endpoint
@app.post("/login", tags=["Users"])
def login(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.username).first()

    if not db_user or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": db_user.email, "role": "user"} , expires_delta=access_token_expires)

    # Verify password directly
    if not pwd_context.verify(user.password[:72], db_user.password):
        raise HTTPException(status_code=401, detail="Invalid Password")

    return {"message": f"Welcome {db_user.name}!", "access_token": access_token, "token_type": "bearer"}

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, SECRETE_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str, credentials_exception):
    try:
        playload = jwt.decode(token, SECRETE_KEY, algorithms=[ALGORITHM])
        email: str = playload.get("sub")
        if email is None:
            raise credentials_exception
        return email
    except JWTError:
        raise credentials_exception
    
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail= 'could not valid credential',
        headers={"WWW-Authenticate": "Bearer"},
    )
    email = verify_access_token(token , credentials_exception)
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@app.get('/profile', tags=["Users"])
def read_profile(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "name" : current_user.name, "email": current_user.email}



#Admin

# Signup endpoint
@app.post("/admin/signup", response_model=AdminOut, tags=["Admins"])
def signup(admin: AdminCreate, db: Session = Depends(get_db)):
    existing_admin = db.query(Admin).filter(Admin.email == admin.email).first()
    if existing_admin:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password directly here (truncate to 72 chars to avoid bcrypt error)
    hashed_password = pwd_context.hash(admin.password[:72])

    new_admin = Admin(
        name=admin.name,
        email=admin.email,
        password=hashed_password,
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin


# Login endpoint
@app.post("/admin/login", tags=["Admins"])
def login(admin: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_admin = db.query(Admin).filter(Admin.email == admin.username).first()

    if not db_admin or not pwd_context.verify(admin.password, db_admin.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": db_admin.email, "role": "admin"} , expires_delta=access_token_expires)
    

    # Verify password directly
    if not pwd_context.verify(admin.password[:72], db_admin.password):
        raise HTTPException(status_code=401, detail="Invalid Password")

    return {"message": f"Welcome {db_admin.name}!", "access_token": access_token, "token_type": "bearer"}


def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail= 'could not valid credential',
        headers={"WWW-Authenticate": "Bearer"},
    )
    email = verify_access_token(token , credentials_exception)
    admin = db.query(Admin).filter(Admin.email == email).first()
    if admin is None:
        raise credentials_exception
    return admin


@app.get('/admin/profile', tags=["Admins"])
def read_profile(current_admin: Admin = Depends(get_current_admin)):
    return {"id": current_admin.admin_id, "name" : current_admin.name, "email": current_admin.email}






#Authorization


def get_admin_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = jwt.decode(token, SECRETE_KEY, algorithms=[ALGORITHM])
    email: str = payload.get("sub")
    role: str = payload.get("role")
    
    if email is None or role != "admin":
        raise credentials_exception

    admin = db.query(Admin).filter(Admin.email == email).first()
    if admin is None:
        raise credentials_exception
    return admin


@app.post("/books/admin/create", tags=["Authorization"])
def create_book(
    book: BookCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_admin_user)  # <--- wrapper ensures admin role
):
    new_book = BookStore(
        title=book.title,
        auth_fname=book.auth_fname,
        auth_lname=book.auth_lname,
        rating=book.rating,
        price=book.price
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book



@app.put("/books/admin/update/{book_id}", tags=["Authorization"])
def update_book(
    book_id : int,
    book: BookCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_admin_user)  # <--- wrapper ensures admin role
):
    db_book = db.query(BookStore).filter(BookStore.book_id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not Found...")
    
    for key, value in book.dict().items():
        setattr(db_book, key, value)
    
    db.commit()
    db.refresh(db_book)
    return db_book
    
       
@app.delete("/books/admin/delete/{book_id}", tags=["Authorization"])
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_admin_user)  # wrapper ensures admin role
):
    db_book = db.query(BookStore).filter(BookStore.book_id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not Found...")
    
    db.delete(db_book)
    db.commit()
    return {"message": f"Book with ID {book_id} deleted successfully"}

      
      
def get_user_access(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = jwt.decode(token, SECRETE_KEY, algorithms=[ALGORITHM])
    email: str = payload.get("sub")
    role: str = payload.get("role")
    
    if email is None or role != "user":
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user



@app.get("/user/books", response_model=List[BookOut], tags=["Authorization"])  # user can view
def get_books(current_user: User = Depends(get_user_access), db: Session = Depends(get_db)):
    books = db.query(BookStore).all()
    return books



# Review

@app.post("/review/", response_model=ReviewOut, tags=["Review"])
def create_review(review: ReviewCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check if book exists
    db_book = db.query(BookStore).filter(BookStore.book_id == review.book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    new_review = Review(
        book_id=review.book_id,
        user_id=current_user.user_id,
        rating=review.rating,
        detail=review.detail
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

@app.get("/books/{book_id}/reviews", response_model=List[ReviewOut], tags=["Review"])
def get_book_reviews(book_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_book = db.query(BookStore).filter(BookStore.book_id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return db.query(Review).filter(Review.book_id == book_id).all()



#Books 

# @app.post('/create', tags=["Books"])
# async def create_book(book: BookCreate, db: Session = Depends(get_db)):
#     new_book = BookStore(
#         title = book.title,
#         auth_fname = book.auth_fname,
#         auth_lname = book.auth_lname,
#         rating = book.rating,
#         price = book.price
#     )
#     db.add(new_book)
#     db.commit()
#     db.refresh(new_book)
#     return new_book

# @app.get('/books', response_model=List[BookOut], tags=["Books"])
# async def books(db: Session = Depends(get_db)):
#     books = db.query(BookStore).all()
#     return books

# @app.put('/books/{book_id}', response_model=BookOut, tags=["Books"])
# async def update_book(book_id : int, book: BookCreate, db: Session = Depends(get_db)):
#     db_book = db.query(BookStore).filter(BookStore.book_id == book_id).first()
#     if not db_book:
#         raise HTTPException(status_code=404, detail="Book not Found...")
    
#     for key, value in book.dict().items():
#         setattr(db_book, key, value)
    
#     db.commit()
#     db.refresh(db_book)
#     return db_book

# @app.delete('/books/{book_id}', tags=["Books"])
# async def delete_book(book_id : int, db: Session = Depends(get_db)):
#     db_book = db.query(BookStore).filter(BookStore.book_id == book_id).first()
#     if not db_book:
#         raise HTTPException(status_code=404, detail="Book not Found...")
    
#     db.delete(db_book)
#     db.commit()
#     return {'Message': f'Book with ID {book_id} deleted successfully'}
    
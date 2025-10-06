from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from model import BookStore
from schemas import BookCreate, BookOut, Book
from db import SessionLocal, base, engine
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from sqlalchemy import func
import os
import shutil
from jose import jwt, JWTError

#User
from datetime import datetime,timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from model import User
from schemas import UserCreate, UserLogin, UserOut, ForgotPasswordRequest, ResetPasswordRequest

#Admin
# from schemas import AdminCreate, AdminLogin, AdminOut
# from model import Admin
from functools import partial

#Review
from schemas import ReviewCreate, ReviewOut
from model import Review

#Update Profile
from schemas import UserUpdate, UpdatePassword

#WiseList
from schemas import FolderCreate, FolderOut, ItemCreate, ItemOut
from model import WishListFolder, WishListItem

#Cart
from schemas import CartCreate, CartOut
from model import Cart

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
    access_token = create_access_token(data={"sub": str(db_user.user_id), "role": "user"} , expires_delta=access_token_expires)

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
    try:
        payload = jwt.decode(token, SECRETE_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
    except JWTError:
        raise credentials_exception

    if user_id is None or role != "user":
        raise credentials_exception

    user = db.query(User).filter(User.user_id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user

@app.get('/profile', tags=["Users"])
def read_profile(current_user: User = Depends(get_current_user)):
    return {"id": current_user.user_id, "name" : current_user.name, "email": current_user.email}


@app.post('/user/forgot-password', tags=['user'])
def forgot_password(request : ForgotPasswordRequest, db : Session = Depends(get_db)):
    user = db.query(User).filter(func.lower(User.email) == request.email.lower()).first()
    if not user:
        raise HTTPException(status_code=404, detail= "User not found...")
    reset_token = create_access_token (
        data={'sub': str(user.user_id), "role" : "user"},
        expires_delta=timedelta(minutes = 15)
    )
    return{"Message": "Password reset token generated" , "reset_token": reset_token}


@app.post('/user/reset-password', tags=['user'])
def reset_password(request : ResetPasswordRequest, db : Session = Depends(get_db)):
    try:
        payload = jwt.decode(request.token, SECRETE_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    if role != "user":
        raise HTTPException(status_code=401, detail="Invalid token role")

    user = db.query(User).filter(User.user_id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found...")
    
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Hash new password and update
    hashed_password = pwd_context.hash(request.new_password[:72])
    user.password = hashed_password

    db.commit()
    db.refresh(user)

    return {"message": "Password reset successfully"}





#Admin

# Signup endpoint
@app.post("/admin/signup", response_model=UserOut, tags=["Admins"])
def signup(admin: UserCreate, db: Session = Depends(get_db)):
    existing_admin = db.query(User).filter(User.email == admin.email).first()
    if existing_admin:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password directly here (truncate to 72 chars to avoid bcrypt error)
    hashed_password = pwd_context.hash(admin.password[:72])

    new_admin = User(
        name=admin.name,
        email=admin.email,
        password=hashed_password,
        phone=admin.phone,
        role='admin'
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin


# Login endpoint
@app.post("/admin/login", tags=["Admins"])
def login(admin: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_admin = db.query(User).filter(User.email == admin.username).first()

    if not db_admin or not pwd_context.verify(admin.password, db_admin.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": str(db_admin.user_id), "role": db_admin.role} , expires_delta=access_token_expires)
    
    # Verify password directly
    if not pwd_context.verify(admin.password[:72], db_admin.password):
        raise HTTPException(status_code=401, detail="Invalid Password")

    return {"message": f"Welcome {db_admin.name}!", "access_token": access_token, "token_type": "bearer"}


def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRETE_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")

        if user_id is None or role != "admin":
            raise credentials_exception

        admin = db.query(User).filter(User.user_id == int(user_id), User.role == "admin").first()
        if admin is None:
            raise credentials_exception

        return admin

    except JWTError:  # Correct exception for python-jose
        raise credentials_exception
    except jwt.ExpiredSignatureError:  # Optional: more descriptive
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.get('/admin/profile', tags=["Admins"])
def read_profile(current_admin: User = Depends(get_current_admin)):
    return {
        "id": current_admin.user_id,
        "name": current_admin.name,
        "email": current_admin.email,
        "role": current_admin.role
    }
    

@app.get('/admin/view-user', tags=["Admins"])
def get_all_users(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    users = db.query(User).filter(User.role == "User").all()
    return users
    




#Authorization


def get_admin_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authorized to perform this action",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRETE_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
    except JWTError:
        raise credentials_exception

    if user_id is None or role != "admin":
        raise credentials_exception

    admin = db.query(User).filter(User.user_id == int(user_id), User.role == "admin").first()
    if admin is None:
        raise credentials_exception

    return admin


@app.post("/books/admin/create", tags=["Authorization"])
def create_book(
    title: str = Form(...),
    author_name: str = Form(...),
    rating: float = Form(...),
    price: int = Form(...),
    categories: str = Form(...),
    stock: int = Form(...),
    publish_year: int = Form(...),
    description: str = Form(...),
    cover_photo: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_admin_user)  # <--- wrapper ensures admin role
):
    
    image_path = None
    if cover_photo:
        os.makedirs("uploads", exist_ok=True)
        image_path = f"uploads/{cover_photo.filename}"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(cover_photo.file, buffer)
        
    new_book = BookStore(
        title=title,
        author_name=author_name,
        rating=rating,
        price=price,
        categories=categories,
        stock=stock,
        publish_year=publish_year,
        description=description,
        cover_photo=image_path
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


@app.put("/books/admin/update/{book_id}", tags=["Authorization"])
def update_book(
    book_id: int,
    title: str = Form(...),
    auth_fname: str = Form(...),
    auth_lname: str = Form(...),
    rating: float = Form(...),
    price: int = Form(...),
    categories: str = Form(...),
    stock: int = Form(...),
    year: int = Form(...),
    detail: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_admin_user)
):
    db_book = db.query(BookStore).filter(BookStore.book_id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found.")

    # Update all fields
    db_book.title = title
    db_book.auth_fname = auth_fname
    db_book.auth_lname = auth_lname
    db_book.rating = rating
    db_book.price = price
    db_book.categories = categories
    db_book.stock = stock
    db_book.year = year
    db_book.detail = detail

    # Handle optional image upload
    if image:
        os.makedirs("uploads", exist_ok=True)
        image_path = f"uploads/{image.filename}"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        db_book.image = image_path

    db.commit()
    db.refresh(db_book)
    return db_book


    
       
@app.delete("/books/admin/delete/{book_id}", tags=["Authorization"])
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_admin_user)  # wrapper ensures admin role
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
    user_id: str = payload.get("sub")
    role: str = payload.get("role")
    
    if user_id is None or role != "user":
        raise credentials_exception

    user = db.query(User).filter(User.user_id == int(user_id)).first()
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




# Update Profile

@app.put("/user/update/{user_id}", tags=["User"])
def update_user(
    user_id : int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not Found...")
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")

    
    update_data = user.dict(exclude_unset=True)
    
    if "email" in update_data:
        existing_user = db.query(User).filter(User.email == update_data["email"]).first()
        if existing_user and existing_user.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists. Please choose a different email."
            )
            
    for key, value in update_data.items():
        if value is not None:
            setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

@app.put("/user/change-password", tags=["User"])
def change_password(
    passwords: UpdatePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if not pwd_context.verify(passwords.last_password, current_user.password):
        raise HTTPException(status_code=400, detail="Incorrect current password")

    if passwords.new_password != passwords.confirm_password:
        raise HTTPException(status_code=400, detail="New password and confirm password do not match")

    hashed_new_password = pwd_context.hash(passwords.new_password[:72])
    current_user.password = hashed_new_password

    db.commit()
    db.refresh(current_user)

    return {"message": "Password updated successfully"}





# WiseList

# @app.post("/user/{user_id}/wiselist", response_model=WiseListOut, tags=["WiseList"])
# def create_wiselist(wiselist: WiseListCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     # Check if the book exists
#     db_book = db.query(BookStore).filter(BookStore.book_id == wiselist.book_id).first()
#     if not db_book:
#         raise HTTPException(status_code=404, detail="Book not found")

#     # Check if the item is already in the wishlist (optional)
#     existing_item = db.query(WiseList).filter(
#         WiseList.user_id == current_user.user_id,
#         WiseList.book_id == wiselist.book_id
#     ).first()
#     if existing_item:
#         raise HTTPException(status_code=400, detail="Book already in wishlist")

#     # Create new wishlist item
#     new_wiselist = WiseList(
#         book_id=wiselist.book_id,
#         user_id=current_user.user_id
#     )
#     db.add(new_wiselist)
#     db.commit()
#     db.refresh(new_wiselist)
#     return new_wiselist


# @app.get("/user/{user_id}/wiselist", response_model=List[WiseListOut], tags=["WiseList"])
# def get_user_wiselist(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     # Make sure the user exists
#     db_user = db.query(User).filter(User.user_id == user_id).first()
#     if not db_user:
#         raise HTTPException(status_code=404, detail="User not found")

#     # Fetch all wishlist items for this user
#     wiselist_items = db.query(WiseList).filter(WiseList.user_id == user_id).all()

#     if not wiselist_items:
#         raise HTTPException(status_code=404, detail="No wishlist found for this user")

#     return wiselist_items

# @app.delete("/user/wiselist/delete/{wiselist_id}", tags=["WiseList"])
# def delete_wiselist(
#     wiselist_id: int,
#     db: Session = Depends(get_db),
#     current_admin: User = Depends(get_current_user)  # wrapper ensures admin role
# ):
#     db_wiselist = db.query(WiseList).filter(WiseList.wiselist_id == wiselist_id).first()
#     if not db_wiselist:
#         raise HTTPException(status_code=404, detail="WiseList not Found...")
    
#     db.delete(db_wiselist)
#     db.commit()
#     return {"message": f"WiseList with ID {wiselist_id} deleted successfully"}

def ensure_default_folder(db: Session, user: User):
    default = db.query(WishListFolder).filter_by(user_id=user.user_id, is_default=True).first()
    if default:
        return default
    
    folder = db.query(WishListFolder).filter_by(user_id=user.user_id).first()
    if not folder:
        folder = WishListFolder(user_id= user.user_id, name='Default', is_default=True)
        db.add(folder)
        db.commit()
        db.refresh(folder)
        return folder
    else:
        folder.is_default = True
        db.commit()
        db.refresh(folder)
        return folder
    
# @app.post("/users/{user_id}/folders", response_model=FolderOut, status_code=status.HTTP_201_CREATED)
# def create_folder(user_id: int, payload: FolderCreate, db: Session = Depends(get_db)):
#     user = db.query(User).get(user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     folder = WishListFolder(user_id=user_id, name= payload.name, is_default=False)
#     db.add(folder)
#     db.commit()
#     db.refresh(folder)
#     return folder

@app.post("/users/{user_id}/folders", response_model=FolderOut)
def create_folder(user_id: int, payload: FolderCreate, db: Session = Depends(get_db),current_admin: User = Depends(get_current_user) ):
    folder = WishListFolder(user_id=user_id, name=payload.name, is_default=False)
    db.add(folder)
    db.commit()
    db.refresh(folder)
    return folder


@app.get("/user/{user_id}/folders", response_model=List[FolderOut])
def list_folder(user_id: int , db: Session = Depends(get_db), current_admin: User = Depends(get_current_user)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    folders = db.query(WishListFolder).filter_by(user_id=user_id).order_by(WishListFolder.create_at).all()
    return folders


@app.post("/users/{user_id}/wishlist", response_model=ItemOut, status_code=(status.HTTP_201_CREATED))
def add_wishlist_item(user_id : int, payload: ItemCreate, db: Session = Depends(get_db),current_admin: User = Depends(get_current_user) ):
    user = db.query(User).get(user_id)
    folder = db.query(WishListFolder).get(payload.folder_id)
    book = db.query(BookStore).get(payload.book_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    item = WishListItem(user_id = user_id, folder_id = payload.folder_id, book_id = payload.book_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@app.get("/user/{user_id}/wishlist", response_model=List[ItemOut])
def get_wishlist_items(user_id : int, db: Session = Depends(get_db),current_admin: User = Depends(get_current_user) ):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    item= db.query(WishListItem).filter_by(user_id=user_id).all()
    return item


@app.delete("/user/wiselist/delete/{wiselist_id}")
def delete_wiselist(
    wiselist_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_user)  # wrapper ensures admin role
):
    db_wiselist = db.query(WishListItem).filter(WishListItem.id == wiselist_id).first()
    if not db_wiselist:
        raise HTTPException(status_code=404, detail="WiseList not Found...")
    
    db.delete(db_wiselist)
    db.commit()
    return {"message": f"WiseList with ID {wiselist_id} deleted successfully"}


# Cart

# @app.post("/user/{user_id}/cart", response_model=CartOut, tags=["Cart"])
# def create_cart(cart: CartCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     # Check if the book exists
#     db_book = db.query(BookStore).filter(BookStore.book_id == cart.book_id).first()
#     if not db_book:
#         raise HTTPException(status_code=404, detail="Book not found")

#     # Check if the item is already in the Cart (optional)
#     existing_item = db.query(Cart).filter(
#         Cart.user_id == current_user.user_id,
#         Cart.book_id == cart.book_id
#     ).first()
#     if existing_item:
#         raise HTTPException(status_code=400, detail="Book already in Cart")

#     # Create new Cart item
#     new_cart = Cart(
#         book_id=cart.book_id,
#         user_id=current_user.user_id
#     )
#     db.add(new_cart)
#     db.commit()
#     db.refresh(new_cart)
#     return new_cart

@app.post("/users/{user_id}/cart", response_model=CartOut, status_code=status.HTTP_201_CREATED,  tags=["Cart"])
def add_to_cart(user_id: int, payload: CartCreate, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    book = db.query(BookStore).get(payload.book_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    existing_cart_item = db.query(Cart).filter_by(user_id=user_id, book_id=payload.book_id).first()
    
    if existing_cart_item:
        existing_cart_item.quantity += payload.quantity
        db.commit()
        db.refresh(existing_cart_item)
        return existing_cart_item
    

    new_cart_item = Cart(
        user_id=user_id,
        book_id=payload.book_id,
        quantity=payload.quantity or 1
    )
    db.add(new_cart_item)
    db.commit()
    db.refresh(new_cart_item)
    return new_cart_item



@app.get("/user/{user_id}/cart", response_model=List[CartOut], tags=["Cart"])
def get_user_cart(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Make sure the user exists
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch all Cart items for this user
    cart_items = db.query(Cart).filter(Cart.user_id == user_id).all()

    if not cart_items:
        raise HTTPException(status_code=404, detail="No wishlist found for this user")

    return cart_items


@app.delete("/user/cart/delete/{cart_id}", tags=["Cart"])
def delete_cart(
    cart_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_user)  # wrapper ensures admin role
):
    db_cart = db.query(Cart).filter(Cart.cart_id == cart_id).first()
    if not db_cart:
        raise HTTPException(status_code=404, detail="Cart not Found...")
    
    db.delete(db_cart)
    db.commit()
    return {"message": f"Cart with ID {cart_id} deleted successfully"}





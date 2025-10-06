from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


#Books
class BookCreate(BaseModel):
    title: str
    author_name: str
    rating: float
    price: int
    
    cover_photo: str
    categories: str
    stock: int
    description: str
    publish_year: int
    
class Book(BaseModel):
    title: str
    author_name: str
    rating: float
    price: int
    
    cover_photo: str
    categories: str
    stock: int
    description: str
    publish_year: int
    

class BookOut(BaseModel):
    title: str
    author_name: str
    rating: float
    price: int
    
    cover_photo: str
    categories: str
    stock: int
    description: str
    publish_year: int
    
    model_config = {"from_attributes" : True}
  
    
#Users

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    user_id: int
    name: str
    email: EmailStr

    model_config = {
        "from_attributes": True
    }
    
    
#Admin

# class AdminCreate(BaseModel):
#     name: str
#     email: EmailStr
#     password: str
#     phone: str
    
# class AdminLogin(BaseModel):
#     email: EmailStr
#     password: str
    
# class AdminOut(BaseModel):
#     admin_id: int
#     name: str
#     email: EmailStr

#     model_config = {
#         "from_attributes": True
#     }
    
    
#review

class ReviewCreate(BaseModel):
    book_id: int
    user_id: int
    detail: str
    rating: float
    
class ReviewOut(BaseModel):
    review_id: int
    detail: str
    rating: float

    model_config = {
        "from_attributes": True
    }
    
    
    
# Update profile and Update Password

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    
    
class UpdatePassword(BaseModel):
    last_password: str
    new_password: str
    confirm_password: str 
    
class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str
    
    
    
#WiseList  

# class WiseListCreate(BaseModel):
#     name: str
#     is_default : Optional[str] = False
    
# class WiseListOut(BaseModel):
#     id: int
#     name: str
#     is_default: bool
#     created_at: datetime
    
#     class Config:
#         orm_mode = True


class FolderCreate(BaseModel):
    name: str
    
class FolderOut(BaseModel):
    id: int
    name: str
    is_default: bool
    create_at: datetime

    model_config = {
        "from_attributes": True
    }



        
class ItemCreate(BaseModel):
    book_id: Optional[int] = None
    folder_id: Optional[int] = None
    
class ItemOut(BaseModel):
    id: int
    book_id: Optional[int]
    folder_id: int
    added_at: datetime
    
    
#Cart  
class CartCreate(BaseModel):
    book_id: int
    user_id: int
    quantity: Optional[int] = 1
    
class CartOut(BaseModel):
    cart_id: int
    book_id: int
    user_id: int
    quantity: int

    model_config = {
        "from_attributes": True
    }
    
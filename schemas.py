from pydantic import BaseModel, EmailStr
from typing import Optional

#Books
class BookCreate(BaseModel):
    title: str
    auth_fname: str
    auth_lname: str
    rating: float
    price: int
    
    image: str
    categories: str
    stock: int
    detail: str
    year: int
    
class Book(BaseModel):
    title: str
    auth_fname: str
    auth_lname: str
    rating: float
    price: int
    
    image: str
    categories: str
    stock: int
    detail: str
    year: int
    

class BookOut(BaseModel):
    title: str
    auth_fname: str
    auth_lname: str
    rating: float
    price: int
    
    image: str
    categories: str
    stock: int
    detail: str
    year: int
    
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
class WiseListCreate(BaseModel):
    book_id: int
    user_id: int
    
class WiseListOut(BaseModel):
    wiselist_id: int
    book_id: int
    user_id: int

    model_config = {
        "from_attributes": True
    }
    
    
#Cart  
class CartCreate(BaseModel):
    book_id: int
    user_id: int
    
class CartOut(BaseModel):
    cart_id: int
    book_id: int
    user_id: int

    model_config = {
        "from_attributes": True
    }
    
from pydantic import BaseModel, EmailStr

#Books
class BookCreate(BaseModel):
    title: str
    auth_fname: str
    auth_lname: str
    rating: float
    price: int
    
class Book(BaseModel):
    title: str
    auth_fname: str
    auth_lname: str
    rating: float
    price: int
    

class BookOut(BaseModel):
    title: str
    auth_fname: str
    auth_lname: str
    rating: float
    price: int
    
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

class AdminCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    
class AdminLogin(BaseModel):
    email: EmailStr
    password: str
    
class AdminOut(BaseModel):
    admin_id: int
    name: str
    email: EmailStr

    model_config = {
        "from_attributes": True
    }
    
    
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
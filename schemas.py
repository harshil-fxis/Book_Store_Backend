from pydantic import BaseModel
from typing import Dict

class BookCreate(BaseModel):
    title: str
    auth_fname: str
    auth_lname: str
    rating: float
    
class Book(BaseModel):
    title: str
    auth_fname: str
    auth_lname: str
    rating: float
    

class BookOut(BaseModel):
    title: str
    auth_fname: str
    auth_lname: str
    rating: float
    
    model_config = {"from_attributes" : True}
  
    

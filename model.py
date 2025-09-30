from pydantic import BaseModel
from sqlalchemy import  Integer, Column, String, Float
from db import base

class BookStore(base):
    __tablename__ = 'bookstore'
    
    book_id = Column(Integer, primary_key = True, index = True)
    title = Column(String, nullable = False)
    auth_fname = Column(String, nullable = False)
    auth_lname = Column(String, nullable = False)
    rating = Column(Float, nullable = False)
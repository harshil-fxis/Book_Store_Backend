from pydantic import BaseModel
from sqlalchemy import  Integer, Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from db import base

class BookStore(base):
    __tablename__ = 'bookstore'
    
    book_id = Column(Integer, primary_key = True, index = True)
    title = Column(String, nullable = False)
    auth_fname = Column(String, nullable = False)
    auth_lname = Column(String, nullable = False)
    rating = Column(Float, nullable = False)
    price = Column(Integer, nullable=False)
    
    reviews = relationship("Review", back_populates="book", cascade="all, delete-orphan")
    
class User(base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    role = Column(String, default='User')
    
    reviews = relationship("Review", back_populates="user")
    
class Admin(base):
    __tablename__ = 'admins'
    
    admin_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default='Admin')
    
    
class Review(base):
    __tablename__ = "reviews"
    
    review_id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("bookstore.book_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    detail = Column(String, nullable=False)
    rating = Column(Float, nullable=False)
    
    book = relationship("BookStore", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

    
    
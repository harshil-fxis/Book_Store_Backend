from pydantic import BaseModel
from sqlalchemy import  Integer, Column, String, Float, ForeignKey, Date, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from db import base
from datetime import datetime
import enum



class CategoryEnum(str, enum.Enum):
    horror = "Horror"
    sci_Fi = "Sci-Fi"
    romance = "Romance"
    history = "History"
    adventure = "Adventure"
    fantasy = "fantasy"

class BookStore(base):
    __tablename__ = 'bookstore'

    book_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable = False)
    author_name = Column(String, nullable = False)
    rating = Column(Float, nullable = False)
    price = Column(Integer, nullable=False)
    
    cover_photo = Column(String, nullable=False)
    categories = Column(Enum(CategoryEnum), nullable=False)
    stock = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    publish_year = Column(Integer, nullable=False)
    
    reviews = relationship("Review", back_populates="book", cascade="all, delete-orphan")
    wishlist_items = relationship("WishListItem", back_populates="book")
    cart = relationship("Cart", back_populates="book")
    
class User(base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    role = Column(String, default='User')
    
    reviews = relationship("Review", back_populates="user")
    wishlist_items = relationship("WishListItem", back_populates="user")
    folders = relationship("WishListFolder", back_populates="user")
    cart = relationship("Cart", back_populates="user")
    
    
# class Admin(base):
#     __tablename__ = 'admins'
    
#     admin_id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=False)
#     email = Column(String, unique=True, index=True, nullable=False)
#     password = Column(String, nullable=False)
#     phone = Column(String, nullable= True)
#     role = Column(String, default='Admin')
    
    
class Review(base):
    __tablename__ = "reviews"
    
    review_id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("bookstore.book_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    detail = Column(String, nullable=False)
    rating = Column(Float, nullable=False)
    
    book = relationship("BookStore", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
    
    
# class WishList(base):
#     __tablename__ = "wishlist"
    
#     wishlist_id = Column(Integer, primary_key=True, index=True)
#     book_id = Column(Integer, ForeignKey("bookstore.book_id"), nullable=False)
#     user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    
#     book = relationship("BookStore", back_populates="wishlist")
#     user = relationship("User", back_populates="wishlist")
    
    
class WishListFolder(base):
    __tablename__ = "wishlist_folder"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    name = Column(String, nullable=True) 
    is_default = Column(Boolean, default=False)
    create_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="folders")
    items = relationship("WishListItem", back_populates="folder", cascade="all, delete-orphan")
    
class WishListItem(base):
    __tablename__ = "wishlist_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    folder_id = Column(Integer, ForeignKey("wishlist_folder.id"), nullable=False)
    book_id = Column(Integer, ForeignKey(BookStore.book_id), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="wishlist_items")
    folder = relationship("WishListFolder", back_populates="items")
    book = relationship("BookStore", back_populates="wishlist_items")
    

class Cart(base):
    __tablename__ = "cart"
    
    cart_id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("bookstore.book_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    
    book = relationship("BookStore", back_populates="cart")
    user = relationship("User", back_populates="cart")

 
# class Booking(base):
#     __tablename__ = "booking"
    
#     booking_id = Column(Integer, primary_key=True, index=True)
#     book_id = Column(Integer, ForeignKey("bookstore.book_id"), nullable=False)
#     user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
#     quantity = Column(Integer, nullable=False)
#     booking_date = Column(Date, nullable=False, default=datetime.utcnow().date)
#     return_date = Column(Date, nullable=True)
#     price_per_book = Column(Float, nullable=False)
#     total_amount = Column(Float, nullable=False)
#     deliver_address = Column(String, nullable=False)
    
#     book = relationship("BookStore", back_populates="booking")
#     user = relationship("User", back_populates="booking")   
    
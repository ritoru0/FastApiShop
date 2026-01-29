from decimal import Decimal
import uuid
from datetime import datetime

from sqlalchemy import (
    ARRAY, Column, Integer, String, Boolean,
    ForeignKey, Float, DateTime, Numeric
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    role = Column(ARRAY(String), nullable=False)

    carts = relationship("Cart", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user")
    addresses = relationship("Address", back_populates="user")


class Product(Base):
    __tablename__ = "products"

    product_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.category_id"), nullable=False)
    name = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    discount_percentage = Column(Float, nullable=False, default=0.0)
    description = Column(String, nullable=True)
    stock = Column(Integer, nullable=False, default=0)
    images = Column(ARRAY(String), nullable=False, default=list)

    cart_items = relationship("CartItem", back_populates="product")
    category = relationship("Category", back_populates="products")


class Cart(Base):
    __tablename__ = "carts"

    cart_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"),
                     nullable=False, unique=True)

    user = relationship("User", back_populates="carts")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items)


class CartItem(Base):
    __tablename__ = "cart_items"

    cart_id = Column(UUID(as_uuid=True), ForeignKey("carts.cart_id", ondelete="CASCADE"), primary_key=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.product_id", ondelete="CASCADE"), primary_key=True)
    quantity = Column(Integer, nullable=False, default=1)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")

    @property
    def subtotal(self):
        price = self.product.price          
        discount = Decimal(str(self.product.discount_percentage)) / Decimal('100') 
        return self.quantity * price * (Decimal('1') - discount)


class Address(Base):
    __tablename__ = "addresses"

    address_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    city = Column(String(100), nullable=False)
    street = Column(String(200), nullable=False)
    house = Column(String(20), nullable=False)
    apartment = Column(String(20), nullable=True)
    postal_code = Column(String(20), nullable=True)
    is_default = Column(Boolean, nullable=False, default=False)

    user = relationship("User", back_populates="addresses")


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    total = Column(Numeric(12, 2), nullable=False)
    status = Column(Float, nullable=False, default=1.0)          
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.order_id", ondelete="CASCADE"), primary_key=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.product_id", ondelete="SET NULL"), primary_key=True)

    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)        

    order = relationship("Order", back_populates="items")
   
class Category(Base):
    __tablename__ = "categories"

    category_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)

    products = relationship("Product", back_populates="category")
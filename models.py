from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func

from database import Base


# =========================================================
# USER / CUSTOMER TABLE
# =========================================================

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    address = Column(String, nullable=False)
    pin_code = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)


# =========================================================
# PRODUCT TABLE
# =========================================================

class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    rating = Column(Float, nullable=False)


# =========================================================
# AVAILABILITY TABLE
# =========================================================

class Availability(Base):
    __tablename__ = "availability"

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(
        Integer,
        ForeignKey("products.product_id"),
        nullable=False
    )

    pin_code = Column(String, nullable=False)


# =========================================================
# CART TABLE
# =========================================================

class Cart(Base):
    __tablename__ = "cart"

    cart_id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.product_id"),
        nullable=False
    )

    quantity = Column(
        Integer,
        nullable=False,
        default=1
    )


# =========================================================
# ORDER TABLE
# =========================================================

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.product_id"),
        nullable=False
    )

    order_date = Column(
        DateTime,
        server_default=func.now()
    )

    status = Column(
        String,
        default="PLACED"
    )


# =========================================================
# PAYMENT TABLE
# =========================================================

class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, index=True)

    order_id = Column(
        Integer,
        ForeignKey("orders.order_id"),
        nullable=False
    )

    amount = Column(
        Float,
        nullable=False
    )

    payment_method = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        default="PENDING"
    )

    payment_date = Column(
        DateTime,
        server_default=func.now()
    )


# =========================================================
# WAREHOUSE TABLE
# =========================================================

class Warehouse(Base):
    __tablename__ = "warehouses"

    warehouse_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    address = Column(
        String,
        nullable=False
    )

    pin_code = Column(
        String,
        nullable=False
    )

    stock = Column(
        Integer,
        nullable=False,
        default=0
    )
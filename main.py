from datetime import timedelta

from fastapi import FastAPI, Depends, HTTPException, Form
from sqlalchemy.orm import Session

from database import Base, engine, get_db

from models import (
    User,
    Product,
    Availability,
    Cart,
    Order,
    Payment,
    Warehouse
)

from schemas import (
    UserCreate,
    UserResponse,
    ProductCreate,
    ProductResponse,
    AvailabilityCreate,
    CartCreate,
    CartResponse,
    OrderCreate,
    OrderResponse,
    PaymentCreate,
    PaymentResponse,
    WarehouseCreate,
    WarehouseResponse
)

from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="Amazon Backend API",
    description="Amazon-like Backend Application",
    version="2.0"
)


# =========================================================
# HOME
# =========================================================

@app.get("/", tags=["Home"])
def home():
    return {
        "message": "Amazon Backend API is running"
    }


# =========================================================
# CUSTOMERS
# =========================================================

@app.post(
    "/customers/register",
    response_model=UserResponse,
    tags=["Customers"]
)
def register_customer(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.username == user.username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    hashed_password = hash_password(user.password)

    new_user = User(
        username=user.username,
        password=hashed_password,
        address=user.address,
        pin_code=user.pin_code,
        phone_number=user.phone_number
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post(
    "/customers/login",
    tags=["Customers"]
)
def customer_login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == username
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    access_token = create_access_token(
        data={"user_id": user.user_id},
        expires_delta=timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.get(
    "/customers/profile",
    response_model=UserResponse,
    tags=["Customers"]
)
def get_customer_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user


# =========================================================
# PRODUCTS
# =========================================================

@app.post(
    "/products",
    response_model=ProductResponse,
    tags=["Products"]
)
def add_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if product.price < 0:
        raise HTTPException(
            status_code=400,
            detail="Price cannot be negative"
        )

    if product.rating < 0 or product.rating > 5:
        raise HTTPException(
            status_code=400,
            detail="Rating must be between 0 and 5"
        )

    new_product = Product(
        name=product.name,
        price=product.price,
        rating=product.rating
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


@app.get(
    "/products",
    response_model=list[ProductResponse],
    tags=["Products"]
)
def get_products(
    db: Session = Depends(get_db)
):
    return db.query(Product).all()


@app.get(
    "/products/{product_id}",
    response_model=ProductResponse,
    tags=["Products"]
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.product_id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product


@app.put(
    "/products/{product_id}",
    response_model=ProductResponse,
    tags=["Products"]
)
def update_product(
    product_id: int,
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(
        Product.product_id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if product_data.price < 0:
        raise HTTPException(
            status_code=400,
            detail="Price cannot be negative"
        )

    if product_data.rating < 0 or product_data.rating > 5:
        raise HTTPException(
            status_code=400,
            detail="Rating must be between 0 and 5"
        )

    product.name = product_data.name
    product.price = product_data.price
    product.rating = product_data.rating

    db.commit()
    db.refresh(product)

    return product


# =========================================================
# CART
# =========================================================

@app.post(
    "/cart",
    response_model=CartResponse,
    tags=["Cart"]
)
def add_to_cart(
    cart_data: CartCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(
        Product.product_id == cart_data.product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if cart_data.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0"
        )

    new_cart = Cart(
        user_id=current_user.user_id,
        product_id=cart_data.product_id,
        quantity=cart_data.quantity
    )

    db.add(new_cart)
    db.commit()
    db.refresh(new_cart)

    return new_cart


@app.get(
    "/cart",
    response_model=list[CartResponse],
    tags=["Cart"]
)
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Cart).filter(
        Cart.user_id == current_user.user_id
    ).all()


# =========================================================
# PRODUCT AVAILABILITY
# =========================================================

@app.post(
    "/availability",
    tags=["Products"]
)
def add_availability(
    data: AvailabilityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(
        Product.product_id == data.product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    existing = db.query(Availability).filter(
        Availability.product_id == data.product_id,
        Availability.pin_code == data.pin_code
    ).first()

    if existing:
        return {
            "message": "Product availability already exists",
            "product_id": data.product_id,
            "pin_code": data.pin_code
        }

    availability = Availability(
        product_id=data.product_id,
        pin_code=data.pin_code
    )

    db.add(availability)
    db.commit()
    db.refresh(availability)

    return {
        "message": "Product availability added",
        "product_id": data.product_id,
        "pin_code": data.pin_code
    }


@app.get(
    "/availability/{product_id}/{pin_code}",
    tags=["Products"]
)
def check_availability(
    product_id: int,
    pin_code: str,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.product_id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    available = db.query(Availability).filter(
        Availability.product_id == product_id,
        Availability.pin_code == pin_code
    ).first()

    if available:
        return {
            "product_id": product_id,
            "pin_code": pin_code,
            "available": True,
            "message": "Product is available for delivery"
        }

    return {
        "product_id": product_id,
        "pin_code": pin_code,
        "available": False,
        "message": "Product is not available for this PIN code"
    }


# =========================================================
# ORDERS
# =========================================================

@app.post(
    "/orders",
    tags=["Orders"]
)
def place_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(
        Product.product_id == order_data.product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    available = db.query(Availability).filter(
        Availability.product_id == product.product_id,
        Availability.pin_code == current_user.pin_code
    ).first()

    if not available:
        raise HTTPException(
            status_code=400,
            detail="Product is not available in your PIN code"
        )

    new_order = Order(
        user_id=current_user.user_id,
        product_id=product.product_id,
        status="PLACED"
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return {
        "message": "Order placed successfully",
        "order_id": new_order.order_id,
        "user_id": new_order.user_id,
        "product_id": new_order.product_id,
        "status": new_order.status,
        "order_date": new_order.order_date
    }


@app.get(
    "/orders",
    response_model=list[OrderResponse],
    tags=["Orders"]
)
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Order).filter(
        Order.user_id == current_user.user_id
    ).all()


@app.get(
    "/orders/{order_id}",
    response_model=OrderResponse,
    tags=["Orders"]
)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(
        Order.order_id == order_id,
        Order.user_id == current_user.user_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return order


@app.put(
    "/orders/{order_id}/status",
    tags=["Orders"]
)
def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(
        Order.order_id == order_id,
        Order.user_id == current_user.user_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    allowed_status = [
        "PLACED",
        "SHIPPED",
        "OUT_FOR_DELIVERY",
        "DELIVERED",
        "CANCELLED"
    ]

    if status not in allowed_status:
        raise HTTPException(
            status_code=400,
            detail="Invalid order status"
        )

    order.status = status

    db.commit()
    db.refresh(order)

    return {
        "message": "Order status updated",
        "order_id": order.order_id,
        "status": order.status
    }


# =========================================================
# PAYMENTS
# =========================================================

@app.post(
    "/payments",
    response_model=PaymentResponse,
    tags=["Payments"]
)
def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(
        Order.order_id == payment_data.order_id,
        Order.user_id == current_user.user_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if payment_data.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Payment amount must be greater than 0"
        )

    payment = Payment(
        order_id=payment_data.order_id,
        amount=payment_data.amount,
        payment_method=payment_data.payment_method,
        status="SUCCESS"
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment


@app.get(
    "/payments",
    response_model=list[PaymentResponse],
    tags=["Payments"]
)
def get_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    payments = (
        db.query(Payment)
        .join(Order, Payment.order_id == Order.order_id)
        .filter(Order.user_id == current_user.user_id)
        .all()
    )

    return payments


# =========================================================
# WAREHOUSE
# =========================================================

@app.post(
    "/warehouse",
    response_model=WarehouseResponse,
    tags=["Warehouse"]
)
def create_warehouse(
    warehouse_data: WarehouseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if warehouse_data.stock < 0:
        raise HTTPException(
            status_code=400,
            detail="Stock cannot be negative"
        )

    warehouse = Warehouse(
        name=warehouse_data.name,
        address=warehouse_data.address,
        pin_code=warehouse_data.pin_code,
        stock=warehouse_data.stock
    )

    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)

    return warehouse


@app.get(
    "/warehouse",
    response_model=list[WarehouseResponse],
    tags=["Warehouse"]
)
def get_warehouses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Warehouse).all()


@app.get(
    "/warehouse/{warehouse_id}",
    response_model=WarehouseResponse,
    tags=["Warehouse"]
)
def get_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    warehouse = db.query(Warehouse).filter(
        Warehouse.warehouse_id == warehouse_id
    ).first()

    if not warehouse:
        raise HTTPException(
            status_code=404,
            detail="Warehouse not found"
        )

    return warehouse


@app.put(
    "/warehouse/{warehouse_id}",
    response_model=WarehouseResponse,
    tags=["Warehouse"]
)
def update_warehouse(
    warehouse_id: int,
    warehouse_data: WarehouseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    warehouse = db.query(Warehouse).filter(
        Warehouse.warehouse_id == warehouse_id
    ).first()

    if not warehouse:
        raise HTTPException(
            status_code=404,
            detail="Warehouse not found"
        )

    if warehouse_data.stock < 0:
        raise HTTPException(
            status_code=400,
            detail="Stock cannot be negative"
        )

    warehouse.name = warehouse_data.name
    warehouse.address = warehouse_data.address
    warehouse.pin_code = warehouse_data.pin_code
    warehouse.stock = warehouse_data.stock

    db.commit()
    db.refresh(warehouse)

    return warehouse
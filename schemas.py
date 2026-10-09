from pydantic import BaseModel, ConfigDict


# =========================================================
# USER / CUSTOMER SCHEMAS
# =========================================================

class UserCreate(BaseModel):
    username: str
    password: str
    address: str
    pin_code: str
    phone_number: str


class UserResponse(BaseModel):
    user_id: int
    username: str
    address: str
    pin_code: str
    phone_number: str

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# PRODUCT SCHEMAS
# =========================================================

class ProductCreate(BaseModel):
    name: str
    price: float
    rating: float


class ProductResponse(BaseModel):
    product_id: int
    name: str
    price: float
    rating: float

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# AVAILABILITY SCHEMAS
# =========================================================

class AvailabilityCreate(BaseModel):
    product_id: int
    pin_code: str


# =========================================================
# CART SCHEMAS
# =========================================================

class CartCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int = 1


class CartResponse(BaseModel):
    cart_id: int
    user_id: int
    product_id: int
    quantity: int

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# ORDER SCHEMAS
# =========================================================

class OrderCreate(BaseModel):
    user_id: int
    product_id: int


class OrderResponse(BaseModel):
    order_id: int
    user_id: int
    product_id: int
    status: str

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# PAYMENT SCHEMAS
# =========================================================

class PaymentCreate(BaseModel):
    order_id: int
    amount: float
    payment_method: str


class PaymentResponse(BaseModel):
    payment_id: int
    order_id: int
    amount: float
    payment_method: str
    status: str

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# WAREHOUSE SCHEMAS
# =========================================================

class WarehouseCreate(BaseModel):
    name: str
    address: str
    pin_code: str
    stock: int = 0


class WarehouseResponse(BaseModel):
    warehouse_id: int
    name: str
    address: str
    pin_code: str
    stock: int

    model_config = ConfigDict(from_attributes=True)
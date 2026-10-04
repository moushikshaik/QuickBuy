from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    price: float
    quantity: int
    
class UserCreate(BaseModel):
    name: str
    email: str

class CartCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int
    
class OrderCreate(BaseModel):
    user_id: int
    total_amount: float
    
class OrderItemCreate(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    price: float
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from .database import engine, Base, SessionLocal
from .models import Product, User, Cart, Order, OrderItem
from .schemas import (
    ProductCreate,
    UserCreate,
    CartCreate,
    OrderCreate,
    OrderItemCreate
)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="QuickBuy API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {
        "message": "Welcome to QuickBuy API"
    }


@app.post("/products")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_product = Product(
        name=product.name,
        price=product.price,
        quantity=product.quantity
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products


@app.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(
        name=user.name,
        email=user.email
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


@app.post("/cart")
def add_to_cart(cart: CartCreate, db: Session = Depends(get_db)):
    new_cart = Cart(
        user_id=cart.user_id,
        product_id=cart.product_id,
        quantity=cart.quantity
    )

    db.add(new_cart)
    db.commit()
    db.refresh(new_cart)

    return new_cart


@app.get("/cart/{user_id}")
def get_cart(user_id: int, db: Session = Depends(get_db)):
    cart = db.query(Cart).filter(Cart.user_id == user_id).all()
    return cart


@app.post("/orders")
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    new_order = Order(
        user_id=order.user_id,
        total_amount=order.total_amount
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return new_order


@app.get("/orders/{user_id}")
def get_orders(user_id: int, db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.user_id == user_id).all()
    return orders


@app.post("/order-items")
def create_order_item(
    item: OrderItemCreate,
    db: Session = Depends(get_db)
):
    new_item = OrderItem(
        order_id=item.order_id,
        product_id=item.product_id,
        quantity=item.quantity,
        price=item.price
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item


@app.get("/order-items/{order_id}")
def get_order_items(order_id: int, db: Session = Depends(get_db)):
    items = db.query(OrderItem).filter(
        OrderItem.order_id == order_id
    ).all()

    return items


@app.post("/checkout/{user_id}")
def checkout(user_id: int, db: Session = Depends(get_db)):
    cart_items = db.query(Cart).filter(
        Cart.user_id == user_id
    ).all()

    if not cart_items:
        return {
            "message": "Cart is empty"
        }

    total_amount = 0

    for item in cart_items:
        product = db.query(Product).filter(
            Product.id == item.product_id
        ).first()

        if not product:
            return {
                "message": f"Product {item.product_id} not found"
            }

        if product.quantity < item.quantity:
            return {
                "message": f"Not enough stock for {product.name}",
                "available": product.quantity,
                "requested": item.quantity
            }

        total_amount += product.price * item.quantity

    new_order = Order(
        user_id=user_id,
        total_amount=total_amount,
        status="PENDING"
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    for item in cart_items:
        product = db.query(Product).filter(
            Product.id == item.product_id
        ).first()

        new_item = OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=product.price
        )

        db.add(new_item)

        product.quantity -= item.quantity

    db.commit()

    db.query(Cart).filter(
        Cart.user_id == user_id
    ).delete()

    db.commit()

    return {
        "message": "Order created successfully",
        "order_id": new_order.id,
        "user_id": new_order.user_id,
        "total_amount": new_order.total_amount,
        "status": new_order.status
    }
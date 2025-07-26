from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Product Model
class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    price: float
    category: str
    image_url: str
    in_stock: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category: str
    image_url: str
    in_stock: bool = True

# Order Models
class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price: float
    image_url: str

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    items: List[OrderItem]
    total_amount: float
    customer_name: str
    customer_phone: str
    customer_address: str
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class OrderCreate(BaseModel):
    items: List[OrderItem]
    total_amount: float
    customer_name: str
    customer_phone: str
    customer_address: str

# Product Routes
@api_router.get("/products", response_model=List[Product])
async def get_products():
    products = await db.products.find().to_list(1000)
    return [Product(**product) for product in products]

@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    product = await db.products.find_one({"id": product_id})
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(**product)

@api_router.get("/products/category/{category}")
async def get_products_by_category(category: str):
    products = await db.products.find({"category": category}).to_list(1000)
    return [Product(**product) for product in products]

@api_router.post("/products", response_model=Product)
async def create_product(product: ProductCreate):
    product_dict = product.dict()
    product_obj = Product(**product_dict)
    await db.products.insert_one(product_obj.dict())
    return product_obj

# Order Routes
@api_router.post("/orders", response_model=Order)
async def create_order(order: OrderCreate):
    order_dict = order.dict()
    order_obj = Order(**order_dict)
    await db.orders.insert_one(order_obj.dict())
    return order_obj

@api_router.get("/orders", response_model=List[Order])
async def get_orders():
    orders = await db.orders.find().to_list(1000)
    return [Order(**order) for order in orders]

@api_router.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: str):
    order = await db.orders.find_one({"id": order_id})
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return Order(**order)

# Initialize sample data
@api_router.post("/init-data")
async def initialize_sample_data():
    # Check if products already exist
    existing_products = await db.products.find().to_list(10)
    if existing_products:
        return {"message": "Sample data already exists"}
    
    sample_products = [
        {
            "id": str(uuid.uuid4()),
            "name": "Chicken Biryani",
            "description": "Aromatic basmati rice cooked with tender chicken pieces and traditional spices",
            "price": 12.99,
            "category": "biryani",
            "image_url": "https://images.unsplash.com/photo-1701579231305-d84d8af9a3fd?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHwxfHxiaXJ5YW5pfGVufDB8fHx8MTc1MzUyNDQ1Mnww&ixlib=rb-4.1.0&q=85",
            "in_stock": True,
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Mutton Biryani",
            "description": "Premium mutton biryani with fragrant spices and long grain basmati rice",
            "price": 15.99,
            "category": "biryani",
            "image_url": "https://images.unsplash.com/photo-1589302168068-964664d93dc0?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHwzfHxiaXJ5YW5pfGVufDB8fHx8MTc1MzUyNDQ1Mnww&ixlib=rb-4.1.0&q=85",
            "in_stock": True,
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Margherita Pizza",
            "description": "Classic pizza with fresh tomatoes, mozzarella cheese, and basil",
            "price": 8.99,
            "category": "pizza",
            "image_url": "https://images.unsplash.com/photo-1700513971573-4f941ab7d282?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwxfHxwaXp6YSUyMGJ1cmdlcnxlbnwwfHx8b3JhbmdlfDE3NTM1MjQwNjZ8MA&ixlib=rb-4.1.0&q=85",
            "in_stock": True,
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Pepperoni Pizza",
            "description": "Delicious pizza topped with pepperoni and melted cheese",
            "price": 10.99,
            "category": "pizza",
            "image_url": "https://images.unsplash.com/photo-1700513971573-4f941ab7d282?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwxfHxwaXp6YSUyMGJ1cmdlcnxlbnwwfHx8b3JhbmdlfDE3NTM1MjQwNjZ8MA&ixlib=rb-4.1.0&q=85",
            "in_stock": True,
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Classic Burger",
            "description": "Juicy beef patty with lettuce, tomato, onion, and special sauce",
            "price": 6.99,
            "category": "burger",
            "image_url": "https://images.unsplash.com/photo-1648580852350-3098af89f110?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwyfHxwaXp6YSUyMGJ1cmdlcnxlbnwwfHx8b3JhbmdlfDE3NTM1MjQwNjZ8MA&ixlib=rb-4.1.0&q=85",
            "in_stock": True,
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Cheese Burger",
            "description": "Classic burger with extra melted cheese and crispy vegetables",
            "price": 7.99,
            "category": "burger",
            "image_url": "https://images.unsplash.com/photo-1648580852350-3098af89f110?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwyfHxwaXp6YSUyMGJ1cmdlcnxlbnwwfHx8b3JhbmdlfDE3NTM1MjQwNjZ8MA&ixlib=rb-4.1.0&q=85",
            "in_stock": True,
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Potato Chips",
            "description": "Crispy golden potato chips with sea salt",
            "price": 2.99,
            "category": "snacks",
            "image_url": "https://images.pexels.com/photos/8858693/pexels-photo-8858693.jpeg",
            "in_stock": True,
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Fresh Bananas",
            "description": "Ripe yellow bananas, perfect for a healthy snack",
            "price": 1.99,
            "category": "groceries",
            "image_url": "https://images.pexels.com/photos/1343537/pexels-photo-1343537.jpeg",
            "in_stock": True,
            "created_at": datetime.utcnow()
        }
    ]
    
    await db.products.insert_many(sample_products)
    return {"message": "Sample data initialized successfully"}

# Search endpoint
@api_router.get("/search")
async def search_products(query: str):
    products = await db.products.find({
        "$or": [
            {"name": {"$regex": query, "$options": "i"}},
            {"description": {"$regex": query, "$options": "i"}},
            {"category": {"$regex": query, "$options": "i"}}
        ]
    }).to_list(1000)
    return [Product(**product) for product in products]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
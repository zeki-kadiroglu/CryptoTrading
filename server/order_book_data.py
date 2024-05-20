import asyncio
from typing import Dict

from server.db.db_initializer import db


async def fetch_initial_order_book_data():
    order_book = db.get("order_book")
    return order_book        

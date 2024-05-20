import os
from typing import Dict

import aiohttp
from broadcast import Broadcast
from server.db.schemas.orderDto import OrderDto

import sys
os.path.join(os.path.dirname(__file__), '../')
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

class Order:
    def __init__(self) -> None:
        self.broadcast = Broadcast()
        
    async def handle_order(self, order: OrderDto, order_book: Dict) -> None:
        pair = order.pair
        if order.action == "buy":
            order_book[pair]["bids"].append({"price": order.price, "quantity": order.quantity})
        elif order.action == "sell":
            order_book[pair]["asks"].append({"price": order.price, "quantity": order.quantity})
        await self.broadcast.broadcast_order_book(pair, order_book)
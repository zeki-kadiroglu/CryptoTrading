from datetime import datetime
from server.db.db_initializer import db

from server.broadcast import Broadcast


class Trade:
    def __init__(self):
        self.broadcast = Broadcast()

    async def execute_trade(
        self,
        user_name,
        connected_users,
        client_id,
        pair,
        quantity,
        price,
        action,
        ):

        trade = {
            "price": price,
            "quantity": quantity,
            "timestamp": str(datetime.utcnow()),
            "action": action
        }

        db.set_key("orders", "username", user_name)
        db.set_key("orders", "price", price)
        db.set_key("orders", "pair", pair)
        db.set_key("orders", "quantity", quantity)
        db.set_key("orders", "action", action)
        db.set_key("orders", "time", str(datetime.now()))
        
        await self.broadcast.broadcast_trade(
            connected_users,
            client_id,
            pair,
            trade
            )

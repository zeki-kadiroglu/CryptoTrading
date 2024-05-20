import json
from fastapi import WebSocket as websocket

class Broadcast:
    def __init__(self):
        self.subscriptions = {}

    async def broadcast_order_book(self, pair, order_book):
        if pair in self.subscriptions:
            for ws in self.subscriptions[pair]:
                #await ws.send_json({
                #    "type": "orderBook",
                #    "pair": pair,
                #    "orderBook": order_book[pair]})
                await ws.send_json(json.dumps(order_book))
                
    async def broadcast_trade(self, connected_users, client_id, pair, trade):
        print("prepare broadcast trade data delivery")
        for user in connected_users:
            print("socker user", type(user), user)
            print("correct websocekt")
            await connected_users[client_id].send_json(
                json.dumps({
                    "type": "trade",
                    "pair": pair,
                    "trade": trade
                    })
                )
            print("sent message..")
        #if pair in self.subscriptions:
        #    for ws in self.subscriptions[pair]:
        #        await ws.send_json()
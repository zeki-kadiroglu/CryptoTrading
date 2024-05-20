import os
import sys
os.path.join(os.path.dirname(__file__), '../')
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from fastapi import FastAPI

from server.broadcast import Broadcast
from server.message_broker import MessageBroker
from server.order import Order
from server.socket_manager import ConnectionManager
from server.trade import Trade


class CryptoAPI(FastAPI):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = FastAPI()
        self.trade = Trade()
        self.broadcast = Broadcast()
        self.msg_broker = MessageBroker()
        self.manager = ConnectionManager()
        self.order = Order()
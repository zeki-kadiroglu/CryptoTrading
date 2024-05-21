import json
import os
import sys
os.path.join(os.path.dirname(__file__), '../')
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from server.dependencies.redis_pool import get_redis_pool
from server.crypto_api import CryptoAPI
from fastapi import HTTPException, Request, status
from server.security.authenticate_user import *
from fastapi import  WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uuid
from server.order_book_data import fetch_initial_order_book_data
import uvicorn
from server.db.db_initializer import db
from server.db.schemas.orderDto import *
from server.db.schemas.token import *
from server.db.schemas.user import *

import logging

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger("myapp")



crpyto_api = CryptoAPI(title="Crypto.API", version="1.0.0")

connected_users = {}
order_book = {}
subscriptions = {}


# GET REDIS CACHE POOL
pool = get_redis_pool()

@crpyto_api.on_event("startup")
async def startup_event():
    
    order_book = await fetch_initial_order_book_data()
    order_book.update(order_book)
    
    # START MESSAGE QUEUE CONSUMER
    crpyto_api.msg_broker.consume_socket_message()
    
    # redis ping
    await pool.ping()
    

@crpyto_api.on_event("shutdown")
async def shutdown():
    #redis close
    await pool.close()
    

crpyto_api.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@crpyto_api.post("/register")
def register_user(user: User):
    existing_user = None
    if user.username in db.get("users"):
        db.set_key("users", "username", user.username)
        existing_user = db.get_key("users", "username")
         
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    encrypted_password = get_password_hash(user.password)
    
    db.set_key("users", "id", str(uuid.uuid4()))
    db.set_key("users", "username", user.username)
    db.set_key("users", "password", encrypted_password)


    return {"message":"user created successfully"}



@crpyto_api.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Request
    ):
    form_data = await form_data.json()
    user = authenticate_user(db, form_data["username"], form_data["password"])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

        
@crpyto_api.websocket("/ws/subscribe/{pair}")
async def websocket_endpoint(
    pair: str,
    websocket: WebSocket,
    ):
    await crpyto_api.manager.connect(websocket)
    
    # Store the WebSocket connection in the dictionary
    client_id = db.get_key("users", "id")
    connected_users[client_id] = websocket
    
    # data from db
    user_name = db.get_key("users", "username")
    client_id = db.get_key("users", "id")
    order_book = db.get("order_book")
    
    
    
    # cache data with redis
    cache_key = str(uuid.uuid4())
    cached_data = await pool.get(cache_key)
    if cached_data:
        pair_order_book = order_book[pair]
    
    pair_order_book = order_book[pair]
    await pool.set(cache_key, json.dumps(order_book), ex=60)
    
    ################
    try:

        while True:
            # order book broadcasting
            data = await websocket.receive_json()
            crpyto_api.msg_broker.publish_socket_message(data)
            await crpyto_api.broadcast.broadcast_order_book(pair=data["pair"], order_book=pair_order_book)
            
            #execute order
            await crpyto_api.trade.execute_trade(
                user_name=user_name,
                connected_users=connected_users,
                client_id=client_id,
                pair=data["pair"],
                quantity=data["quantity"],
                price=data["price"],
                action=data["action"],
                )
    
                
    except WebSocketDisconnect:
        # If a user disconnects, remove them from the dictionary
        del connected_users[client_id]
        crpyto_api.manager.disconnect(websocket)
        
        

# @app.post("/execute_order")
# async def update_order(order: Request):
#     #for user in connected_users:
#     #    await user[client_id].send_json()
#     order = await order.json()
#     print("len connected users", len(connected_users), connected_users)
#     print("order", order)
#     user_name = db.get_key("users", "username")
#     client_id = db.get_key("users", "id")
#     order_book = db.get("order_book")
#     #message = json.dumps(order)
#     await trade.execute_trade(
#         user_name=user_name,
#         connected_users=connected_users,
#         client_id=client_id,
#         pair=order["pair"],
#         quantity=order["quantity"],
#         price=order["price"],
#         action=order["action"],
#         order_book=order_book
#         )
#     return {"message": "Order executed"}

if __name__ == "__main__":

    uvicorn.run(crpyto_api, host="0.0.0.0", port=8000)
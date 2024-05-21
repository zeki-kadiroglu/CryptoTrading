

from pydantic import BaseConfig

class GlobalConfig(BaseConfig):
    RABBITMQ_PORT = 5672
    RABBITMQ_HOST = '127.0.0.1'
    RABBITMQ_USER_NAME = 'guest'
    RABBITMQ_PASSWORD = 'guest'
    RABBITMQ_EXCHANGE = 'socket'
    
    # Secret key to encode/decode JWT tokens
    SECRET_KEY = "your_secret_key"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
settings = GlobalConfig()
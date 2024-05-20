from pydantic import BaseModel


class OrderDto(BaseModel):
    direction: str
    price: str
    quantity: str
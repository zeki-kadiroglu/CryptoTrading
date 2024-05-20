from pydantic import BaseModel

class User(BaseModel):
    username: str
    #full_name: str
    #email: str
    password: str
    
class UserInDB(User):
    hashed_password: str
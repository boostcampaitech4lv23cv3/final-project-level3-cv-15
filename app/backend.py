from fastapi import FastAPI, UploadFile, File
from fastapi.param_functions import Depends
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import List, Union, Optional, Dict, Any
from datetime import datetime
from database import engineconn, User, Exercise

app = FastAPI()

engine = engineconn()
session = engine.sessionmaker()

class UserItem(BaseModel):
    nickname : str
    user_id : str
    user_password : str
    user_hash : str
    
class ExerciseItem(BaseModel):
    user_hash : str
    type : str
    date : datetime
    count : int
    perfect : int
    good : int
    miss : int

@app.get("/users")
def get_user():
    example = session.query(User).all()
    return example

@app.post("/users")
async def register_user(item: UserItem):
    new_user = User(nickname=item.nickname, 
                   user_id=item.user_id,
                   user_password=item.user_password, 
                   user_hash=item.user_hash)
    session.add(new_user)
    session.commit()
    return new_user
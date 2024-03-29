from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date
from database import engineconn, User, Exercise
import uvicorn
import pandas as pd
from sqlalchemy.dialects.mysql import insert

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
    date : date
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

@app.get("/exercises")
def get_exercise():
    example = session.query(Exercise).all()
    return example

@app.post("/exercises")
async def add_exercise(item: ExerciseItem):
    insert_stmt = insert(Exercise).values(
                user_hash=item.user_hash, 
                type=item.type,
                date=item.date, 
                perfect=item.perfect, 
                good=item.good,
                miss=item.miss)

    on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(
                user_hash=insert_stmt.inserted.user_hash, 
                type=insert_stmt.inserted.type,
                date=insert_stmt.inserted.date, 
                perfect=insert_stmt.inserted.perfect, 
                good=insert_stmt.inserted.good,
                miss=insert_stmt.inserted.miss,
                status='U'
            )

    engine.engine.execute(on_duplicate_key_stmt)

def user_info(user_id):
    sql = f"select * from user where user_id='{user_id}'"
    data = pd.read_sql(sql=sql, con=engine.engine)
    return data

def user_exercise_info(user_hash, date):
    sql = f"select type, perfect, good, miss from exercise where user_hash='{user_hash}' and date='{date}'"
    data = pd.read_sql(sql=sql, con=engine.engine)
    return data

def user_exercise_day(user_hash):
    sql = f"select count(distinct date) from exercise where user_hash='{user_hash}'"
    data = pd.read_sql(sql=sql, con=engine.engine)
    return data

def user_calendar_data(user_hash):
    sql = f"select date, count(date) from exercise where user_hash='{user_hash}' group by date"
    data = pd.read_sql(sql=sql, con=engine.engine)
    return [[date.strftime('%Y-%m-%d'), count] for date, count in zip(data['date'],data['count(date)'])]


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

class engineconn():
    def __init__(self, DB_NAME):
        self.engine = create_engine('mysql://root:boostcamp4cv15@localhost:3306/'+DB_NAME, encoding="utf-8", echo=True)

    def sessionmaker(self):
        Session = sessionmaker(autocommig=False, autoflush=False, bind=self.engine)
        session = Session()
        return session

    def connection(self):
        conn = self.engine.connect()
        return conn
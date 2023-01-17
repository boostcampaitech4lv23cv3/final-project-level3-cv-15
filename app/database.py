from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, declarative_base

class engineconn():
    def __init__(self):
        self.engine = create_engine(
            'mysql+pymysql://root:boostcamp4cv15@0.0.0.0:3306/boostcamp_db',
            encoding="utf-8",
            echo=True,
        )

    def sessionmaker(self):
        Session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        return Session()

    def connection(self):
        return self.engine.connect()
    
Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    nickname = Column(VARCHAR, nullable=False)
    user_id = Column(VARCHAR, nullable=False)
    user_password = Column(VARCHAR, nullable=False)
    user_hash = Column(VARCHAR, nullable=False, primary_key=True)
    
class Exercise(Base):
    __tablename__ = 'exercise'
    user_hash = Column(VARCHAR, nullable=False, primary_key=True)
    type = Column(VARCHAR, nullable=False, primary_key=True)
    date = Column(DATETIME, nullable=False, primary_key=True)
    perfect = Column(INT, nullable=False)
    good = Column(INT, nullable=False)
    miss = Column(INT, nullable=False)
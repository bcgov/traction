import os
from config import Config
from sqlmodel import create_engine, SQLModel, Session

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=True)
admin_engine = create_engine(Config.SQLALCHEMY_DATABASE_ADMIN_URI, echo=True)

def init_db():
    SQLModel.metadata.create_all(admin_engine)


def get_session():
    with Session(engine) as session:
        yield session
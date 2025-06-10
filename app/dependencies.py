from typing import Annotated
from fastapi import Depends
from sqlalchemy import Engine
from sqlmodel import Session, SQLModel, create_engine


username = 'root'
password = '123456'
server_ip = '127.0.0.1'
port = '3306'
db_name = 'economics'
sql_url = f"mysql+pymysql://{username}:{password}@{server_ip}:{port}/{db_name}"

# engine = create_engine(sql_url, echo=True)
engine = create_engine(
    sql_url,
    echo=True,
    pool_pre_ping=True,  # 可选：连接断开后自动重连
    future=True          # 启用 SQLAlchemy 2.0 风格语法（可选）
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
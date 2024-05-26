from sqlalchemy import Column, Integer, String, Float, LargeBinary
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import event, text
import sqlalchemy

# create the engine and event listeners as before
engine = create_async_engine("sqlite+aiosqlite:///./db/users_data.sqlite?check_same_thread=False")

@event.listens_for(engine.sync_engine, "connect")
def do_connect(dbapi_connection, connection_record):
    print("do connect")
    dbapi_connection.isolation_level = None

@event.listens_for(engine.sync_engine, "begin")
def do_begin(conn):
    print("do begin")
    conn.exec_driver_sql("BEGIN")

# create a base class for our models
Base = sqlalchemy.orm.declarative_base()

# define our model
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(String, unique=True, index=True)
    chat_id = Column(String, unique=True)
    username = Column(String, unique=True)
    language = Column(String)
    name = Column(String)
    age = Column(Integer)
    height = Column(Integer)
    coord_x = Column(Float)
    coord_y = Column(Float)
    photos = Column(String, default='')
    mainText = Column(String, nullable=True)
    gender = Column(String)
    find_gender = Column(String)
    minAge = Column(Integer)
    maxAge = Column(Integer)
    minHeight = Column(Integer)
    maxHeight = Column(Integer)
    arr_of_ids = Column(LargeBinary)
    city = Column(String)
    last_user_id = Column(String)

# create the database tables
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# create the async session maker
__factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


# create a session
async def create_session() -> AsyncSession:
    global __factory
    return __factory()

# main function
async def main():
    # await create_tables()
    session = await create_session()
    res = await session.execute(text("SELECT * FROM users"))
    res = res.scalars().first()
    await session.close()
    print(f'{res=}')

import asyncio

asyncio.run(main())
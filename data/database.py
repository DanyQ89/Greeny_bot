from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SqlAlchemyBase = declarative_base()

__factory = None


async def init_models():
    global __factory

    if __factory:
        return

    conn_str = 'sqlite+aiosqlite:///./db/users_data.sqlite?check_same_thread=False'

    engine = create_async_engine(conn_str, echo=False)
    __factory = async_sessionmaker(bind=engine, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(SqlAlchemyBase.metadata.create_all, checkfirst=True)


async def create_session() -> AsyncSession:
    global __factory
    return __factory()

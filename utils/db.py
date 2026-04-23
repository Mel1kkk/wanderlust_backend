from fastapi import FastAPI
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
from os import getenv


load_dotenv()

engine = create_async_engine(
    getenv('DB_URL', 'sqlite+aiosqlite:///./educators.db'),
    # todo Заменить sqlite на postgresql, aiosqlite на asyncpg, линк дб
    echo = True
)
BaseEntity = declarative_base()


asyncSession = sessionmaker(
        bind = engine,
        class_ = AsyncSession,
        expire_on_commit = False,
        autoflush = False
    )


async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(BaseEntity.metadata.create_all)
    yield

    
async def connect_db():
    async with asyncSession() as session:
        yield session
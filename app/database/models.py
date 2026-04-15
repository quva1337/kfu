import os

from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import BigInteger, JSON, TIMESTAMP, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession
from dotenv import load_dotenv

load_dotenv(override=True)
engine = create_async_engine(url=os.getenv('SQLALCHEMY_URL'), echo=False)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    telephone_number: Mapped[str]
    name_and_surname: Mapped[str]


class CountOrders(Base):
    __tablename__ = 'count_orders'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    num_orders: Mapped[int] = mapped_column(nullable=True)


class Promocode(Base):
    __tablename__ = 'promocodes'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    left_in_use: Mapped[int] = mapped_column(nullable=True)
    percent: Mapped[int]


class Banned_User(Base):
    __tablename__ = 'banned_users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    # telephone_number: Mapped[str]
    # name_and_surname: Mapped[str]
    # time = mapped_column(Time)


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    name_and_surname: Mapped[str]
    telephone_number: Mapped[str]
    number_of_zone: Mapped[str]
    time: Mapped[str]
    create_time = mapped_column(TIMESTAMP(timezone=True))
    order = mapped_column(JSON)
    payment: Mapped[float]
    status: Mapped[bool] = mapped_column(nullable=True)


class User_Used_Promo(Base):
    __tablename__ = 'user_used_promocodes'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    used_promocodes = mapped_column(MutableList.as_mutable(ARRAY(String)), nullable=False)


async def async_main():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

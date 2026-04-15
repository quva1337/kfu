from app.database.models import async_session
from app.database.models import User, Order, Banned_User, CountOrders, Promocode, User_Used_Promo
from sqlalchemy import select, update
import app.config as config


async def check_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

    if not user:
        return False


async def get_user_tgid(fio, telephone_number):
    async with async_session() as session:
        user = await session.scalar(
            select(User).where(User.name_and_surname == fio, User.telephone_number == telephone_number))
        if user:
            return user.tg_id
        else:
            return


async def get_user_tgid_for_razban(telephone_number):
    async with async_session() as session:
        user = await session.scalar(
            select(User).where(User.telephone_number == telephone_number))
        if user:
            return user.tg_id
        else:
            return


async def check_banned_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(Banned_User).where(Banned_User.tg_id == tg_id))
    if user:
        return True
    else:
        return False


async def get_num_user_orders(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(CountOrders).where(CountOrders.tg_id == tg_id))
        if user:
            return user.num_orders
        else:
            return 0


async def count_user_orders(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(CountOrders).where(CountOrders.tg_id == tg_id))
        if user:
            user.num_orders += 1
        else:
            session.add(CountOrders(tg_id=tg_id, num_orders=1))
        await session.commit()


async def check_promo(name):
    async with async_session() as session:
        promo = await session.scalar(select(Promocode).where(Promocode.name == name))

        if promo:
            return [promo.name, promo.percent, promo.left_in_use]
        else:
            return False


async def have_promo_in_history(tg_id, name):
    async with async_session() as session:
        user = await session.scalar(select(User_Used_Promo).where(User_Used_Promo.tg_id == tg_id))
        if user:
            return name in user.used_promocodes
        else:
            return False


async def add_to_promo_history(tg_id, name):
    async with async_session() as session:
        user = await session.scalar(select(User_Used_Promo).where(User_Used_Promo.tg_id == tg_id))
        if not user:
            session.add(User_Used_Promo(tg_id=tg_id, used_promocodes=[name]))
            await session.commit()
        else:
            user.used_promocodes.append(name)
            await session.commit()


async def create_promo(name, percent, left_in_use):
    async with async_session() as session:
        session.add(Promocode(name=name, left_in_use=left_in_use, percent=percent))
        await session.commit()
        return


async def used_promo(name):
    async with async_session() as session:
        promo = await session.scalar(select(Promocode).where(Promocode.name == name))
        if promo.left_in_use == 1:
            await session.delete(promo)
            await session.commit()
        else:
            promo.left_in_use -= 1
            await session.commit()


async def load_blocked_users():
    async with async_session() as session:
        result = await session.execute(select(Banned_User.tg_id))
        blocked_ids = result.scalars().all()
        config.blocked_users_cache = set(blocked_ids)
        print(config.blocked_users_cache)


async def add_user(tg_id, fio, telephone_number):
    async with async_session() as session:
        session.add(User(tg_id=tg_id, name_and_surname=fio, telephone_number=telephone_number))
        await session.commit()


async def edit_user_fio(tg_id, fio):
    async with async_session() as session:
        stmt = (
            update(User)
            .where(User.tg_id == tg_id)
            .values(name_and_surname=fio)
            .execution_options(synchronize_session="fetch")
        )
        await session.execute(stmt)
        await session.commit()


async def edit_user_telephone(tg_id, telephone_number):
    async with async_session() as session:
        stmt = (
            update(User)
            .where(User.tg_id == tg_id)
            .values(telephone_number=telephone_number)
            .execution_options(synchronize_session="fetch")
        )
        await session.execute(stmt)
        await session.commit()


async def add_order(tg_id, number_of_zone, time, order, payment, create_time):
    async with async_session() as session:
        async with session.begin():
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            session.add(
                Order(tg_id=tg_id, name_and_surname=user.name_and_surname, telephone_number=user.telephone_number,
                      number_of_zone=number_of_zone,
                      time=time, order=order, payment=payment, create_time=create_time))
            await session.commit()


async def check_order(tg_id):
    async with async_session() as session:
        order = await session.scalar(select(Order).where(User.tg_id == tg_id))

        return order.order


async def get_user_info(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        return [user.name_and_surname, user.telephone_number]


async def add_banned_user(tg_id):
    async with async_session() as session:
        # Проверяем, существует ли пользователь
        existing_user = await session.scalar(select(Banned_User).where(Banned_User.tg_id == tg_id))
        if existing_user:
            return
            # Добавляем нового пользователя
        new_user = Banned_User(tg_id=tg_id)
        session.add(new_user)
        await session.commit()
        await load_blocked_users()


async def delete_banned_user(tg_id):
    async with async_session() as session:
        # Проверяем, существует ли пользователь
        user_to_delete = await session.scalar(
            select(Banned_User).where(Banned_User.tg_id == tg_id)
        )
        if user_to_delete:
            await session.delete(user_to_delete)
            await session.commit()
            await load_blocked_users()
        return


async def set_order_status_true(surname_name, telephone_number, time, create_time, zone):
    async with async_session() as session:
        order = await session.scalar(
            select(Order).where(Order.name_and_surname == surname_name, Order.telephone_number == telephone_number,
                                Order.number_of_zone == zone, Order.time == time,
                                Order.create_time == create_time))
        order.status = True
        await session.commit()


async def set_order_status_false(surname_name, telephone_number, time, create_time, zone, payment):
    async with async_session() as session:
        order = await session.scalar(
            select(Order).where(Order.name_and_surname == surname_name, Order.telephone_number == telephone_number,
                                Order.number_of_zone == zone, Order.time == time, Order.payment == payment,
                                Order.create_time == create_time))
        order.status = False
        await session.commit()


async def get_order_to_back(surname_name, telephone_number, time, create_time, zone, payment):
    async with async_session() as session:
        order = await session.scalar(
            select(Order).where(Order.name_and_surname == surname_name, Order.telephone_number == telephone_number,
                                Order.number_of_zone == zone, Order.time == time, Order.payment == payment,
                                Order.create_time == create_time))
        return order.order

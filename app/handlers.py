from datetime import datetime
import re
import os
from aiogram import F, Router
from aiogram.filters import Filter
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, callback_query
from aiogram.types.callback_query import CallbackQuery
from aiogram import Bot
import app.keyboards as kb
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from app.database.requests import check_user, add_user, add_order, check_order, get_user_info, edit_user_fio, \
    edit_user_telephone, add_banned_user, set_order_status_true, get_order_to_back, set_order_status_false, \
    check_banned_user, get_user_tgid, delete_banned_user, get_user_tgid_for_razban, count_user_orders, check_promo, \
    create_promo, get_num_user_orders, used_promo, have_promo_in_history, add_to_promo_history
import app.config as config

PHONE_REGEX = r'^(?:\+7|8)\d{10}$'
NAME_SURNAME_REGEX = r'^[А-ЯЁа-яёA-Za-z]{1,20}(-[А-ЯЁа-яёA-Za-z]{1,20})? [А-ЯЁа-яёA-Za-z]{1,20}(-[А-ЯЁа-яёA-Za-z]{1,20})?$'
ORDERS_OPEN = True

router = Router()


class Is_Digit(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.text.isdigit()


class Is_Digit_and_Bolshe_0(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.text.isdigit() and int(message.text) > 0


class Isnt_Digit(Filter):
    async def __call__(self, message: Message) -> bool:
        return not (message.text.isdigit()) or int(message.text) <= 0


class More_10(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.text.isdigit() and int(message.text) > 0


class Less_10(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.text.isdigit() and int(message.text) <= 10


class BlockUserFilter(Filter):
    async def __call__(self, obj: Message | CallbackQuery) -> bool:
        return obj.from_user.id not in config.blocked_users_cache


# router.message.filter(BlockUserFilter())
# router.callback_query.filter(BlockUserFilter())


class Order(StatesGroup):
    name_and_surname = State()
    change_fio = State()
    change_telephone_number = State()
    telephone_number = State()
    choose_category = State()
    choose_dish = State()
    number_of_dishes = State()
    number_of_zone = State()
    time_of_delivery = State()
    waiting_for_unban = State()
    waiting_for_promo_name = State()
    waiting_for_promo_percent = State()
    waiting_for_promo_num_of_usage = State()
    have_no_have_promo = State()
    waiting_promo_from_user = State()
    after_new_promocode = State()
    after_ban = State()


async def processing_categories(callback_data: kb.Category, query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if callback_data.name == 'Основное':
        await query.message.edit_text('Наши основные блюда:', reply_markup=kb.main_kb)
        await state.update_data(current_group='Основное')
        await state.set_state(Order.choose_dish)
    elif callback_data.name == 'Сэндвичи':
        await query.message.edit_text('Сэндвичи:', reply_markup=kb.sandwiches_kb)
        await state.update_data(current_group='Сэндвичи')
        await state.set_state(Order.choose_dish)
    elif callback_data.name == 'Суп':
        await query.message.edit_text('Наши супы:', reply_markup=kb.soup_kb)
        await state.update_data(current_group='Суп')
        await state.set_state(Order.choose_dish)
    elif callback_data.name == 'Паста':
        await query.message.edit_text('Паста:', reply_markup=kb.pasta_and_wok_kb)
        await state.update_data(current_group='Паста')
        await state.set_state(Order.choose_dish)
    elif callback_data.name == 'Пицца Наполетана':
        await query.message.edit_text('Пицца:', reply_markup=kb.pizza_kb)
        await state.update_data(current_group='Пицца Наполетана')
        await state.set_state(Order.choose_dish)
    elif callback_data.name == 'Морсы':
        await query.message.edit_text('Морсы:', reply_markup=kb.morses_kb)
        await state.update_data(current_group='Морсы')
        await state.set_state(Order.choose_dish)
    elif callback_data.name == 'Салаты':
        await query.message.edit_text('Салаты:', reply_markup=kb.salads_kb)
        await state.update_data(current_group='Салаты')
        await state.set_state(Order.choose_dish)
    elif callback_data.name == 'Фри':
        await query.message.edit_text('Фри:', reply_markup=kb.free_kb)
        await state.update_data(current_group='Фри')
        await state.set_state(Order.choose_dish)
    elif callback_data.name == 'Напитки':
        if not data['need_end']:
            await query.message.edit_text('Напитки:', reply_markup=kb.drinks_kb)
            await state.update_data(current_group='Напитки')
            await state.set_state(Order.choose_category)
        else:
            await query.message.edit_text('Напитки:', reply_markup=kb.drinks_withend_kb)
            await state.update_data(current_group='Напитки')
            await state.set_state(Order.choose_category)
    elif callback_data.name == 'Прохладительные':
        await query.message.edit_text('Прохладительные напитки:', reply_markup=kb.cold_drinks_kb)
        await state.update_data(current_group='Прохладительные')
        await state.set_state(Order.choose_dish)
    elif callback_data.name == 'Горячие':
        await query.message.edit_text('Горячие напитки:', reply_markup=kb.pasta_and_wok_kb)
        await state.update_data(current_group='Горячие')
        await state.set_state(Order.choose_dish)
    elif callback_data.name == 'Милкшейки':
        await query.message.edit_text('Милкшейки:', reply_markup=kb.pizza_kb)
        await state.update_data(current_group='Милкшейки')
        await state.set_state(Order.choose_dish)
    elif callback_data.name == 'Смузи и Фреши':
        await query.message.edit_text('Смузи и Фреши:', reply_markup=kb.drinks_kb)
        await state.update_data(current_group='Смузи и Фреши')
        await state.set_state(Order.choose_dish)


@router.message(F.text == 'ban')
async def test(message: Message, state: FSMContext):
    await add_banned_user(message.from_user.id)


@router.callback_query(kb.TimeButton.filter(), Order.time_of_delivery)
async def check_prom(query: CallbackQuery, callback_data: kb.TimeButton, state: FSMContext):
    await query.message.edit_text('У вас есть промокод?', reply_markup=kb.promo_checking)
    await state.update_data(time=callback_data.time)
    await state.set_state(Order.have_no_have_promo)


@router.callback_query(kb.Promo.filter(), Order.have_no_have_promo)
async def check_prom(query: CallbackQuery, callback_data: kb.Promo, state: FSMContext):
    if not callback_data.have:
        res = await check_banned_user(query.from_user.id)
        if res == False:
            data = await state.get_data()
            if 'order' in data:
                number_of_zone = data['number_of_zone']
                time = data['time']
                text = 'Ваш заказ:\n'
                for i in data['order']:
                    text += f'{i}: '
                    text += str(data['order'][i])
                    text += '\n'
                for j in range(30):
                    text += '_'
                text += '\n'
                text += f'Итого - {data["payment"]}₽\n'
                text += f'время: {time}\n'
                text += f'зона доставки: {number_of_zone}\n'
                text += f'Все верно?'
                await query.message.edit_text(text=text, reply_markup=kb.itog_ord)
                await state.update_data(used_promo='no')
        else:
            await query.answer()
    else:
        await query.message.edit_text("Введите промокод")
        await state.set_state(Order.waiting_promo_from_user)


@router.message(Order.waiting_promo_from_user)
async def typed_promo(message: Message, state: FSMContext):
    # проверить существует ли этот промокод
    # проверить первый ли это заказ пользователя и если да, и промокод определенный, например первый10, то засчитать ему промик
    # если не первый и существует промик то обновить количество, удалить
    # проверить не использовал ли ранее этот промокод
    tg_id = message.from_user.id
    number_of_orders = await get_num_user_orders(tg_id)
    promo_text = message.text.strip()
    check_existing_promo = await check_promo(promo_text)
    data = await state.get_data()
    if number_of_orders == 0:
        if promo_text == 'первый10' or check_existing_promo:
            res = await check_banned_user(tg_id)
            if res == False:
                if check_existing_promo:
                    has_promo = await have_promo_in_history(tg_id, promo_text)
                    if has_promo:
                        await message.answer('Вы уже использовали этот промокод!')
                        number_of_zone = data['number_of_zone']
                        time = data['time']
                        text = 'Ваш заказ:\n'
                        for i in data['order']:
                            text += f'{i}: '
                            text += str(data['order'][i])
                            text += '\n'
                        for j in range(30):
                            text += '_'
                        text += '\n'
                        text += f'Итого - {data["payment"]}₽\n'
                        text += f'время: {time}\n'
                        text += f'зона доставки: {number_of_zone}\n'
                        text += f'Все верно?'
                        await message.answer(text=text, reply_markup=kb.itog_ord)
                        await state.update_data(used_promo='no')
                        await state.set_state(Order.have_no_have_promo)
                    else:
                        # await add_to_promo_history(tg_id, promo_text)
                        if 'order' in data:
                            number_of_zone = data['number_of_zone']
                            time = data['time']
                            text = 'Ваш промокод активирован\n'
                            text += 'Ваш заказ:\n'
                            for i in data['order']:
                                text += f'{i}: '
                                text += str(data['order'][i])
                                text += '\n'
                            for j in range(30):
                                text += '_'
                            text += '\n'
                            text += f'Итого - {data["payment"] * (100 - check_existing_promo[1]) / 100}₽\n'
                            await state.update_data(last_percent=check_existing_promo[1])
                            text += f'время: {time}\n'
                            text += f'зона доставки: {number_of_zone}\n'
                            text += f'Все верно?'
                            await state.update_data(used_promo=promo_text)
                            await message.answer(text=text, reply_markup=kb.itog_ord)
                            await state.set_state(Order.have_no_have_promo)
                elif promo_text == 'первый10':
                    if 'order' in data:
                        number_of_zone = data['number_of_zone']
                        time = data['time']
                        text = 'Ваш промокод активирован\n'
                        text += 'Ваш заказ:\n'
                        for i in data['order']:
                            text += f'{i}: '
                            text += str(data['order'][i])
                            text += '\n'
                        for j in range(30):
                            text += '_'
                        text += '\n'
                        text += f'Итого - {data["payment"] * 90 / 100}₽\n'
                        await state.update_data(last_percent=10)
                        text += f'время: {time}\n'
                        text += f'зона доставки: {number_of_zone}\n'
                        text += f'Все верно?'
                        await state.update_data(used_promo=promo_text)
                        await message.answer(text=text, reply_markup=kb.itog_ord)
                        await state.set_state(Order.have_no_have_promo)
            else:
                await message.answer('Ваш аккаунт заморожен')
        else:
            await message.answer('Такого промокода не существует')
            res = await check_banned_user(tg_id)
            if res == False:
                if 'order' in data:
                    number_of_zone = data['number_of_zone']
                    time = data['time']
                    text = 'Ваш заказ:\n'
                    for i in data['order']:
                        text += f'{i}: '
                        text += str(data['order'][i])
                        text += '\n'
                    for j in range(30):
                        text += '_'
                    text += '\n'
                    text += f'Итого - {data["payment"]}₽\n'
                    text += f'время: {time}\n'
                    text += f'зона доставки: {number_of_zone}\n'
                    text += f'Все верно?'
                    await message.answer(text=text, reply_markup=kb.itog_ord)
                    await state.update_data(used_promo='no')
                    await state.set_state(Order.have_no_have_promo)
            else:
                await message.answer('Ваш аккаунт заморожен')
    else:
        if promo_text == 'первый10':
            text = 'Этот промокод действителен только на первый заказ.\n'
            res = await check_banned_user(tg_id)
            if res == False:
                if 'order' in data:
                    number_of_zone = data['number_of_zone']
                    time = data['time']
                    text += 'Ваш заказ:\n'
                    for i in data['order']:
                        text += f'{i}: '
                        text += str(data['order'][i])
                        text += '\n'
                    for j in range(30):
                        text += '_'
                    text += '\n'
                    text += f'Итого - {data["payment"]}₽\n'
                    text += f'время: {time}\n'
                    text += f'зона доставки: {number_of_zone}\n'
                    text += f'Все верно?'
                    await message.answer(text=text, reply_markup=kb.itog_ord)
                    await state.update_data(used_promo='no')
                    await state.set_state(Order.have_no_have_promo)
            else:
                await message.answer('Ваш аккаунт заморожен')
        else:
            if check_existing_promo:
                res = await check_banned_user(tg_id)
                if res == False:
                    has_promo = await have_promo_in_history(tg_id, promo_text)
                    if not has_promo:
                        # await add_to_promo_history(tg_id, promo_text)
                        if 'order' in data:
                            number_of_zone = data['number_of_zone']
                            time = data['time']
                            text = 'Ваш промокод активирован\n'
                            text += 'Ваш заказ:\n'
                            for i in data['order']:
                                text += f'{i}: '
                                text += str(data['order'][i])
                                text += '\n'
                            for j in range(30):
                                text += '_'
                            text += '\n'
                            text += f'Итого - {data["payment"] * (100 - check_existing_promo[1]) / 100}₽\n'
                            text += f'время: {time}\n'
                            text += f'зона доставки: {number_of_zone}\n'
                            text += f'Все верно?'
                            await state.update_data(used_promo=promo_text)
                            await state.update_data(last_percent=check_existing_promo[1])
                            await message.answer(text=text, reply_markup=kb.itog_ord)
                            await state.set_state(Order.have_no_have_promo)
                    else:
                        await message.answer('Вы уже использовали этот промокод!')
                        number_of_zone = data['number_of_zone']
                        time = data['time']
                        text = 'Ваш заказ:\n'
                        for i in data['order']:
                            text += f'{i}: '
                            text += str(data['order'][i])
                            text += '\n'
                        for j in range(30):
                            text += '_'
                        text += '\n'
                        text += f'Итого - {data["payment"]}₽\n'
                        text += f'время: {time}\n'
                        text += f'зона доставки: {number_of_zone}\n'
                        text += f'Все верно?'
                        await message.answer(text=text, reply_markup=kb.itog_ord)
                        await state.update_data(used_promo='no')
                        await state.set_state(Order.have_no_have_promo)
                else:
                    await message.answer('Ваш аккаунт заморожен')
            else:
                await message.answer('Такого промокода не существует')
                res = await check_banned_user(tg_id)
                if res == False:
                    if 'order' in data:
                        number_of_zone = data['number_of_zone']
                        time = data['time']
                        text = 'Ваш заказ:\n'
                        for i in data['order']:
                            text += f'{i}: '
                            text += str(data['order'][i])
                            text += '\n'
                        for j in range(30):
                            text += '_'
                        text += '\n'
                        text += f'Итого - {data["payment"]}₽\n'
                        text += f'время: {time}\n'
                        text += f'зона доставки: {number_of_zone}\n'
                        text += f'Все верно?'
                        await message.answer(text=text, reply_markup=kb.itog_ord)
                        await state.update_data(used_promo='no')
                        await state.set_state(Order.have_no_have_promo)
                else:
                    await message.answer('Ваш аккаунт заморожен')


# @router.callback_query(kb.TimeButton.filter(), Order.time_of_delivery)
# async def itog_order(query: CallbackQuery, callback_data: kb.TimeButton, state: FSMContext):
#     res = await check_banned_user(query.from_user.id)
#     if res == False:
#         data = await state.get_data()
#         if 'order' in data:
#             number_of_zone = data['number_of_zone']
#             time = callback_data.time
#             text = 'Ваш заказ:\n'
#             for i in data['order']:
#                 text += f'{i}: '
#                 text += str(data['order'][i])
#                 text += '\n'
#             for j in range(30):
#                 text += '_'
#             text += '\n'
#             text += f'Итого - {data["payment"]}₽\n'
#             text += f'время: {time}\n'
#             text += f'зона доставки: {number_of_zone}\n'
#             text += f'Все верно?'
#             await query.message.edit_text(text=text, reply_markup=kb.itog_ord)
#             await state.update_data(time=time)
#     else:
#         await query.answer()
#     # await query.message.edit_text('Вот наше меню!', reply_markup=kb.category_withend_kb)
#     # await state.set_state(Order.choose_category)


@router.callback_query(F.data == 'ne_sostoyalsa', Order.have_no_have_promo)
async def ne_sostoyalsa(query: CallbackQuery, state: FSMContext):
    res = await check_banned_user(query.from_user.id)
    if res == False:
        await query.message.edit_text('Вот наше меню!', reply_markup=kb.category_withend_kb)
        await state.set_state(Order.choose_category)
    else:
        await query.answer()


@router.callback_query(F.data == 'end_itog', Order.have_no_have_promo)
async def zaver_order(query: CallbackQuery, state: FSMContext):
    res = await check_banned_user(query.from_user.id)
    if res == False:
        if ORDERS_OPEN:
            data = await state.get_data()
            used_promocode = data['used_promo']
            tg_id = query.from_user.id
            create_time = query.message.date
            local_time = create_time.astimezone()
            if 'order' in data:
                if used_promocode == 'no':
                    payment = data['payment']
                elif used_promocode == 'первый10':
                    payment = data['payment'] * 90 / 100
                else:
                    payment = data["payment"] * (100 - data['last_percent']) / 100
                    await add_to_promo_history(tg_id, used_promocode)
                order = data['order']
                number_of_zone = data['number_of_zone']
                time = data['time']
                await add_order(tg_id, number_of_zone, time, order, payment, local_time)
                await query.message.delete()
                await query.answer('Заказ оформлен!', show_alert=True)
                await query.message.answer(
                    'Спасибо за заказ! Пожалуйста, заберите заказ в течение следующей перемены, иначе ваш аккаунт будет заморожен. Дополнительно вам придет сообщение, когда курьер приедет в зону выдачи заказа. Чтобы заказать еще раз, так же воспользуйтесь кнопками',
                    reply_markup=kb.first)
                await count_user_orders(tg_id)
                await state.update_data(payment=0)
                await state.update_data(order={})
                await state.update_data(need_end=False)
                await state.update_data(history=[])
                await state.update_data(used_promo='no')
                text = 'заказ:\n'
                for i in order:
                    text += f'{i}: '
                    text += str(order[i])
                    text += '\n'
                for j in range(30):
                    text += '_'
                text += '\n'
                user_info = await get_user_info(tg_id)
                text += f'имя и фамилия: {user_info[0]}\n'
                text += f'номер телефона: {user_info[1]}\n'
                text += f'время: {time}\n'
                text += f'дата создания: {local_time}\n'
                text += f'сумма заказа: {payment}\n'
                text += f'зона доставки: {number_of_zone}'
                if used_promocode != 'no' and used_promocode != 'первый10':
                    text += f'\nиспользованный промокод: "{used_promocode}"'
                    await used_promo(used_promocode)
                elif used_promocode == 'первый10':
                    text += f'\nиспользованный промокод: "{used_promocode}"'
                bot = Bot(token=os.getenv('TOKEN'))
                await bot.send_message(os.getenv('WORKING_AKK'), text=text, reply_markup=kb.order_status2)
                # await state.update_data(for_delivers=[user_info[0], user_info[1], tg_id, tele])
            else:
                await query.message.answer('Пожалуйста, добавьте товары в корзину заново!', reply_markup=kb.first)
        else:
            await query.answer()
            await query.message.answer(
                'Сейчас кухня загружена, ваш заказ не смогут обработать, пожалуйста, возвращайтесь позднее.')

    else:
        await query.answer()


@router.message(CommandStart())
async def com_start(message: Message, state: FSMContext):
    res = await check_user(message.from_user.id)
    if res == False:
        await message.answer(
            'Привет! Чтобы воспользоваться доставкой, нужно пройти регистрацию. Пожалуйста, введите вашу фамилию и имя. Например, Петров Иван')
        await state.set_state(Order.name_and_surname)
    else:
        await message.answer('Привет! Здесь ты можешь заказать еду с доставкой.', reply_markup=kb.first)
    await state.update_data(payment=0)
    await state.update_data(order={})
    await state.update_data(need_end=False)
    await state.update_data(history=[])
    await state.update_data(used_promo='no')


@router.message(Command('close'))
async def com_close(message: Message, state: FSMContext):
    if message.from_user.id == int(os.getenv('WORKING_AKK')):
        bot = Bot(token=os.getenv('TOKEN'))
        await message.answer('Заказы остановлены!')
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        global ORDERS_OPEN
        ORDERS_OPEN = False


@router.message(Command('open'))
async def com_close(message: Message, state: FSMContext):
    if message.from_user.id == int(os.getenv('WORKING_AKK')):
        bot = Bot(token=os.getenv('TOKEN'))
        await message.answer('Заказы возобновлены!')
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        global ORDERS_OPEN
        ORDERS_OPEN = True


@router.message(F.text == 'Мой профиль')
async def my_profile(message: Message, state: FSMContext):
    user_info = await get_user_info(message.from_user.id)
    await message.answer(
        f"""Ваши данные:
______________
{user_info[0]}
{user_info[1]}
______________
Если хотите изменить что-либо,
нажмите на соответствующую кнопку
""", reply_markup=kb.change_info)


@router.callback_query(F.data == 'change_fio')
async def change_fio_profile(query: CallbackQuery, state: FSMContext):
    await query.message.edit_text('Введите новые имя и фамилию')
    await state.set_state(Order.change_fio)


@router.callback_query(F.data == 'change_telephone_number')
async def change_telephone_number_profile(query: CallbackQuery, state: FSMContext):
    await query.message.edit_text('Введите новый номер телефона')
    await state.set_state(Order.change_telephone_number)


@router.message(F.text == 'Сделать заказ')
async def do_order(message: Message, state: FSMContext):
    res = await check_banned_user(message.from_user.id)
    if res == False:
        if ORDERS_OPEN:
            data = await state.get_data()
            if 'need_end' not in data:
                data['need_end'] = False
            await state.update_data(need_end=False)
            data = await state.get_data()
            if not data['need_end']:
                await message.answer('Вот наше меню!', reply_markup=kb.category_kb)
                await state.set_state(Order.choose_category)
            else:
                await message.answer('Вот наше меню!', reply_markup=kb.category_withend_kb)
                await state.set_state(Order.choose_category)
        else:
            await message.answer(
                'Сейчас кухня загружена, ваш заказ не смогут обработать, пожалуйста, возвращайтесь позднее.')
    else:
        await message.answer(
            "Ваш аккаунт заморожен.")


@router.message(F.text == 'Разморозить аккаунт')
async def category_handler(message: Message, state: FSMContext):
    res = await check_banned_user(message.from_user.id)
    if res == False:
        await message.answer('Ваш аккаунт и так разморожен, вы можете пользоваться всеми функциями бота.',
                             reply_markup=kb.first)
    else:
        await message.answer(
            "Для того чтобы разморозить аккаунт нужно написать @dostavkakfu и отправить скриншот ваших неоплаченных заказов. В случае попытки обмана, вы лишитесь возможности оспорить заморозку аккаунта.",
            reply_markup=kb.first_with_ban)


@router.message(Command('unban'))
async def razban(message: Message, state: FSMContext):
    if message.from_user.id == 7038317548:
        await message.answer(
            'Введите номер телефона пользователя. Например, +79123456789')
        await state.set_state(Order.waiting_for_unban)
    else:
        await message.answer('Вы не можете разбанивать людей.')


@router.message(Command('promo'))
async def wait_name_promocode(message: Message, state: FSMContext):
    if message.from_user.id == 7038317548:
        await message.answer('Введите промокод')
        await state.set_state(Order.waiting_for_promo_name)
    else:
        await message.answer('Вы не можете создавать промокоды.')


@router.message(Order.waiting_for_promo_name)
async def wait_percent_promocode(message: Message, state: FSMContext):
    if message.from_user.id == 7038317548:
        name = message.text.strip()
        promo = await check_promo(name)
        if not promo:
            await message.answer('Введите, какую скидку в процентах дает промокод, например, 15')
            await state.set_state(Order.waiting_for_promo_percent)
            await state.update_data(new_promo=message.text.strip())
        else:
            await message.answer('Такой промокод уже создан, введите другой')
    else:
        await message.answer('Вы не можете создавать промокоды.')


@router.message(Order.waiting_for_promo_percent)
async def wait_num_of_usage_promocode(message: Message, state: FSMContext):
    if message.from_user.id == 7038317548:
        await message.answer('Введите количество использований для промокода.')
        await state.set_state(Order.waiting_for_promo_num_of_usage)
        await state.update_data(percent=int(message.text.strip()))
    else:
        await message.answer('Вы не можете создавать промокоды.')


@router.message(Order.waiting_for_promo_num_of_usage)
async def end_new_promocode(message: Message, state: FSMContext):
    if message.from_user.id == 7038317548:
        await message.answer('Промокод создан')
        data = await state.get_data()
        await create_promo(data['new_promo'], data['percent'], int(message.text.strip()))
    else:
        await message.answer('Вы не можете создавать промокоды.')
    await state.set_state(Order.after_new_promocode)


@router.message(Order.change_fio)
async def typed_new_fio(message: Message, state: FSMContext):
    if re.match(NAME_SURNAME_REGEX, message.text):
        await edit_user_fio(message.from_user.id, message.text)
        await message.answer("Данные обновлены!", reply_markup=kb.first)
    else:
        await message.answer('Пожалуйста, введите имя и фамилию правильно, через пробел, например, Абрамов Даниил')


@router.message(Order.change_telephone_number)
async def typed_new_telephone_number(message: Message, state: FSMContext):
    if re.match(PHONE_REGEX, message.text):
        await edit_user_telephone(message.from_user.id, message.text)
        await message.answer(f"Данные обновлены!", reply_markup=kb.first)
    else:
        await message.answer('Вы ввели некорректный номер телефона, пожалуйста, введите правильный!')


@router.message(Order.name_and_surname)
async def typed_name(message: Message, state: FSMContext):
    if re.match(NAME_SURNAME_REGEX, message.text):
        await state.update_data(fio=message.text)
        await message.answer('Далее, введите ваш номер телефона в формате +7. Например, +79123456789')
        await state.set_state(Order.telephone_number)
    else:
        await message.answer('Пожалуйста, введите имя и фамилию правильно, через пробел, например, Абрамов Даниил')


@router.message(Order.telephone_number)
async def typed_number(message: Message, state: FSMContext):
    if re.match(PHONE_REGEX, message.text):
        await state.update_data(telephone_number=message.text)
        await message.answer('Спасибо за регистрацию! Воспользуйтесь кнопками внизу', reply_markup=kb.first)
        data = await state.get_data()
        await add_user(message.from_user.id, data['fio'], data['telephone_number'])
    else:
        await message.answer('Вы ввели некорректный номер телефона, пожалуйста, введите правильный!')


@router.callback_query(kb.Category.filter())
async def category_handler(query: CallbackQuery, callback_data: kb.Category, state: FSMContext):
    res = await check_banned_user(query.from_user.id)
    if res == False:
        await processing_categories(callback_data=callback_data, query=query, state=state)
    else:
        await query.answer()


# @router.callback_query(kb.Drink.filter())
# async def category_handler(query: CallbackQuery, callback_data: kb.Category, state: FSMContext):
#     await processing_categories(callback_data=callback_data, query=query, state=state)
#     await state.set_state(Order.choose_category)


@router.callback_query(kb.Back.filter())
async def back_to_menu(query: CallbackQuery, callback_data: kb.Back, state: FSMContext):
    res = await check_banned_user(query.from_user.id)
    if res == False:
        data = await state.get_data()
        if callback_data.to_main:
            if not data['need_end']:
                await query.message.edit_text('Вот наше меню!', reply_markup=kb.category_kb)
                await state.set_state(Order.choose_category)
            else:
                await query.message.edit_text('Вот наше меню!', reply_markup=kb.category_withend_kb)
                await state.set_state(Order.choose_category)
        elif callback_data.to_drinks:
            if not data['need_end']:
                await query.message.edit_text('Напитки:', reply_markup=kb.drinks_kb)
                await state.set_state(Order.choose_category)
            else:
                await query.message.edit_text('Напитки:', reply_markup=kb.drinks_withend_kb)
                await state.set_state(Order.choose_category)
        elif callback_data.to_last_category:
            await processing_categories(kb.Category(name=data['current_group']), query, state)
            await state.update_data(current_dish=None)
            await state.set_state(Order.choose_dish)
    else:
        await query.answer()


@router.callback_query(kb.Delivery_Zone_Button.filter(), Order.number_of_zone)
async def typed_zone(query: CallbackQuery, callback_data: kb.Delivery_Zone_Button, state: FSMContext):
    res = await check_banned_user(query.from_user.id)
    if res == False:
        await state.update_data(number_of_zone=f'{callback_data.number} | {callback_data.name}')
        res = await kb.time_buttons()
        if res == False:
            await query.message.delete()
            await query.message.answer("Мы сожалеем, но доставка не работает. Ваша корзина сохранена",
                                       reply_markup=kb.first)
        else:
            await query.message.edit_text("Выберите время доставки", reply_markup=res)
        await state.set_state(Order.time_of_delivery)
    else:
        await query.answer()


@router.callback_query(kb.Bludo.filter())
async def category_handler(query: CallbackQuery, callback_data: kb.Category, state: FSMContext):
    res = await check_banned_user(query.from_user.id)
    if res == False:
        await query.message.edit_text(f'Введите какое количество {callback_data.name} вы хотите заказать',
                                      reply_markup=kb.back_in_message)
        await state.set_state(Order.number_of_dishes)
        await state.update_data(current_dish=callback_data.name)
    else:
        await query.answer()


@router.message(Order.number_of_dishes, Is_Digit(), Is_Digit_and_Bolshe_0(), Less_10())
async def category_handler(message: Message, state: FSMContext):
    res = await check_banned_user(message.from_user.id)
    if res == False:
        await state.update_data(need_end=True)
        data = await state.get_data()
        if 'order' not in data:
            data['order'] = {}
        order = data['order']
        if 'history' not in data:
            data['history'] = []
        history = data['history']
        if 'payment' not in data:
            data['payment'] = 0
        if data['current_dish'] in order:
            order[data['current_dish']] += int(message.text)
        else:
            order[data['current_dish']] = int(message.text)
        x = data['payment'] + int(message.text) * kb.price_list[data['current_dish']]
        history += [(int(message.text), data['current_dish'])]
        await state.update_data(order=order)
        await state.update_data(payment=x)
        await state.update_data(history=history)
        await message.answer('Отлично, добавили в заказ!')
        await message.answer('Вот наше меню!', reply_markup=kb.category_withend_kb)
        await state.set_state(Order.choose_category)
    else:
        await message.answer("Ваш аккаунт заморожен", reply_markup=kb.first_with_ban)


@router.message(Order.number_of_dishes, More_10())
async def category_handler(message: Message, state: FSMContext):
    await message.answer('В один заказ нельзя добавить больше 10, введите меньшее число.')


@router.message(Order.number_of_dishes, Isnt_Digit())
async def category_handler(message: Message, state: FSMContext):
    await message.answer('Пожалуйста, введите целое число, например, 2')


@router.callback_query(F.data == 'end_zakaz')
async def end_zakaz(callback_data: callback_query, state: FSMContext):
    res = await check_banned_user(callback_data.from_user.id)
    if res == False:
        data = await state.get_data()
        if 'order' in data:
            text = 'Ваш заказ:\n'
            for i in data['order']:
                text += f'{i}: '
                text += str(data['order'][i])
                text += '\n'
            for j in range(30):
                text += '_'
            text += '\n'
            text += f'Итого - {data["payment"]}₽'
            await callback_data.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Удалить последнее', callback_data='clear_last'),
                 InlineKeyboardButton(text='Очистить все', callback_data='clear_all')],
                [InlineKeyboardButton(text='⬅️ Назад', callback_data=(kb.Back(to_main=True)).pack())],
                [InlineKeyboardButton(text='Заказать с доставкой', callback_data='delivery')]
            ]))
        else:
            await callback_data.answer('Пожалуйста, добавьте товары в корзину заново', show_alert=True)
            await callback_data.message.edit_text('Вот наше меню!', reply_markup=kb.category_kb)
            await state.set_state(Order.choose_category)
            await state.update_data(history=[])
            await state.update_data(need_end=False)
            await state.update_data(order={})
            await state.update_data(payment=0)
    else:
        await callback_data.answer()


@router.message(Order.waiting_for_unban)
async def do_razban(message: Message, state: FSMContext):
    # print(message.text.split('|'))
    data = message.text.strip()
    tg_id = await get_user_tgid_for_razban(data)
    if tg_id:
        res = await check_banned_user(tg_id)
        if res:
            await delete_banned_user(tg_id)
            await message.answer('Пользователь успешно разбанен!')
            await state.set_state(Order.after_ban)
        else:
            await message.answer('Пользователь с таким номером телефона не забанен!')
            await state.set_state(Order.after_ban)
    else:
        await message.answer('Перепроверьте данные пользователя, тот, кого вы ввели не заморожен')


@router.callback_query(F.data == 'clear_all')
async def clear_all(query: CallbackQuery, state: FSMContext):
    res = await check_banned_user(query.from_user.id)
    if res == False:
        await state.update_data(payment=0)
        await state.update_data(order={})
        await state.update_data(need_end=False)
        await state.update_data(history=[])

        await query.answer('Корзина очищена!')
        await query.message.edit_text('Вот наше меню!', reply_markup=kb.category_kb)
        await state.set_state(Order.choose_category)
    else:
        await query.answer()


@router.callback_query(F.data == 'clear_last')
async def clear_last(callback_data: callback_query, state: FSMContext):
    res = await check_banned_user(callback_data.from_user.id)
    if res == False:
        data = await state.get_data()
        if 'order' in data:
            order = data['order']
            history = data['history']
            # print(history)
            order[history[-1][1]] -= history[-1][0]
            if order[history[-1][1]] == 0:
                del order[history[-1][1]]
            x = data['payment'] - history[-1][0] * kb.price_list[history[-1][1]]
            history.pop()
            # print(history)

            await callback_data.answer('Удалили последнее добавленное блюдо')

            if order:
                text = 'Ваш заказ:\n'
                for i in order:
                    text += f'{i}: '
                    text += str(order[i])
                    text += '\n'
                for j in range(30):
                    text += '_'
                text += '\n'
                text += f'Итого - {x}₽'
                await callback_data.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Удалить последнее', callback_data='clear_last'),
                     InlineKeyboardButton(text='Очистить все', callback_data='clear_all')],
                    [InlineKeyboardButton(text='⬅️ Назад', callback_data=(kb.Back(to_main=True)).pack())],
                    [InlineKeyboardButton(text='Заказать с доставкой', callback_data='delivery')]
                ]))
                await state.update_data(need_end=True)
            else:
                await callback_data.message.edit_text('Вот наше меню!', reply_markup=kb.category_kb)
                await state.set_state(Order.choose_category)
                await state.update_data(need_end=False)
            await state.update_data(history=history)
            await state.update_data(order=order)
            await state.update_data(payment=x)
        else:
            await callback_data.answer('Корзина пустая', show_alert=True)
            await callback_data.message.edit_text('Вот наше меню!', reply_markup=kb.category_kb)
            await state.set_state(Order.choose_category)
            await state.update_data(need_end=False)
            await state.update_data(history=[])
            await state.update_data(order={})
            await state.update_data(payment=0)
    else:
        await callback_data.answer()


@router.callback_query(F.data == 'delivery')
async def waiting_zone(callback_data: callback_query, state: FSMContext):
    res = await check_banned_user(callback_data.from_user.id)
    if res == False:
        res = await kb.zones_buttons()
        await state.set_state(Order.number_of_zone)
        await callback_data.message.edit_text('Выберите зону доставки', reply_markup=res)
    else:
        await callback_data.answer()


@router.callback_query(F.data == 'uspeh')
async def first_check(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if 'for_delivery_payment' not in data or data['for_delivery_payment'] == 'payment':
        # print(query.message.text.split())
        text = query.message.text.split()
        if text[-2] != 'промокод:':
            surname_name = ''
            telephone_number = ''
            time = ''
            create_time = ''
            zone = ''
            payment = 0
            for i in range(len(text)):
                if text[i] == 'фамилия:':
                    surname_name = text[i + 1] + ' ' + text[i + 2]
                    telephone_number = text[i + 5]
                    time = text[i + 7]
                    create_time = text[i + 10] + ' ' + text[i + 11]
                    for j in range(len(text)):
                        if text[j] == 'заказа:':
                            payment = float(text[j + 1])
                    if text[i + 17] == '1':
                        zone = text[-3] + ' ' + text[-2] + ' ' + text[-1]
                    else:
                        zone = text[-4] + ' ' + text[-3] + ' ' + text[-2] + ' ' + text[-1]
            create_time = datetime.fromisoformat(create_time)
        else:
            surname_name = ''
            telephone_number = ''
            time = ''
            create_time = ''
            zone = ''
            payment = 0
            for i in range(len(text)):
                if text[i] == 'фамилия:':
                    surname_name = text[i + 1] + ' ' + text[i + 2]
                    telephone_number = text[i + 5]
                    time = text[i + 7]
                    create_time = text[i + 10] + ' ' + text[i + 11]
                    for j in range(len(text)):
                        if text[j] == 'заказа:':
                            payment = float(text[j + 1])
                    if text[i + 17] == '1':
                        zone = text[-6] + ' ' + text[-5] + ' ' + text[-4]
                    else:
                        zone = text[-7] + ' ' + text[-6] + ' ' + text[-5] + ' ' + text[-4]
            create_time = datetime.fromisoformat(create_time)
        await state.update_data(for_delivery_surname_name=surname_name, for_delivery_telephone_number=telephone_number,
                                for_delivery_time=time, for_delivery_create_time=create_time, for_delivery_zone=zone,
                                for_delivery_payment=payment)
        await query.message.edit_text("Вы подтвердили заказ. Вы уверены?", reply_markup=kb.status_yes_checking)
    else:
        await query.answer(
            text='Пожалуйста, завершите оформление прошлого заказа, либо нажмите ⬅️, чтобы снова показывалась информация о заказе.',
            show_alert=True)


@router.callback_query(F.data == 'neuspeh')
async def first_check(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if 'for_delivery_payment' not in data or data['for_delivery_payment'] == 'payment':
        # print(query.message.text.split())
        text = query.message.text.split()
        surname_name = ''
        telephone_number = ''
        time = ''
        create_time = ''
        zone = ''
        payment = 0
        if text[-2] != 'промокод:':
            for i in range(len(text)):
                if text[i] == 'фамилия:':
                    surname_name = text[i + 1] + ' ' + text[i + 2]
                    telephone_number = text[i + 5]
                    time = text[i + 7]
                    create_time = text[i + 10] + ' ' + text[i + 11]
                    for j in range(len(text)):
                        if text[j] == 'заказа:':
                            payment = float(text[j + 1])
                    if text[i + 17] == '1':
                        zone = text[-3] + ' ' + text[-2] + ' ' + text[-1]
                    else:
                        zone = text[-4] + ' ' + text[-3] + ' ' + text[-2] + ' ' + text[-1]
        else:
            for i in range(len(text)):
                if text[i] == 'фамилия:':
                    surname_name = text[i + 1] + ' ' + text[i + 2]
                    telephone_number = text[i + 5]
                    time = text[i + 7]
                    create_time = text[i + 10] + ' ' + text[i + 11]
                    for j in range(len(text)):
                        if text[j] == 'заказа:':
                            payment = float(text[j + 1])
                    if text[i + 17] == '1':
                        zone = text[-6] + ' ' + text[-5] + ' ' + text[-4]
                    else:
                        zone = text[-7] + ' ' + text[-6] + ' ' + text[-5] + ' ' + text[-4]
        create_time = datetime.fromisoformat(create_time)
        await state.update_data(for_delivery_surname_name=surname_name, for_delivery_telephone_number=telephone_number,
                                for_delivery_time=time, for_delivery_create_time=create_time, for_delivery_zone=zone,
                                for_delivery_payment=payment)
        await query.message.edit_text("Вы отклонили заказ. Вы уверены?", reply_markup=kb.status_no_checking)
    else:
        await query.answer(
            text='Пожалуйста, завершите оформление прошлого заказа, либо нажмите ⬅️, чтобы снова показывалась информация о заказе.',
            show_alert=True)


@router.callback_query(F.data == 'kurer_na_meste')
async def second_check(query: CallbackQuery, state: FSMContext):
    # отправить сообщение пользователю
    data = await state.get_data()
    # print(query.message.text.split())
    text = query.message.text.split()
    surname_name = ''
    telephone_number = ''
    time = ''
    create_time = ''
    zone = ''
    payment = 0
    for i in range(len(text)):
        if text[i] == 'фамилия:':
            surname_name = text[i + 1] + ' ' + text[i + 2]
            telephone_number = text[i + 5]
            time = text[i + 7]
            create_time = text[i + 10] + ' ' + text[i + 11]
            for j in range(len(text)):
                if text[j] == 'заказа:':
                    payment = float(text[j + 1])
                if text[i + 17] == '1':
                    zone = text[-3] + ' ' + text[-2] + ' ' + text[-1]
                else:
                    zone = text[-4] + ' ' + text[-3] + ' ' + text[-2] + ' ' + text[-1]
    create_time = datetime.fromisoformat(create_time)
    tg_id = await get_user_tgid(surname_name, telephone_number)
    bot = Bot(token=os.getenv('TOKEN'))
    await bot.send_message(tg_id, text='Курьер с вашим заказом приехал! Пожалуйста, заберите заказ на перемене!')
    await query.answer('Сообщили заказчику', show_alert=True)
    await query.message.edit_text(query.message.text, reply_markup=kb.order_status)
    await state.update_data(kurer_na_meste=True)


@router.callback_query(F.data == 'nice')
async def second_check(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    # print(data['for_delivery_surname_name'], data['for_delivery_telephone_number'], data['for_delivery_time'],
    #       data['for_delivery_create_time'], data['for_delivery_zone'])
    await set_order_status_true(surname_name=data['for_delivery_surname_name'],
                                telephone_number=data['for_delivery_telephone_number'], time=data['for_delivery_time'],
                                create_time=data['for_delivery_create_time'], zone=data['for_delivery_zone'])
    await query.message.edit_text("Отлично")
    await state.update_data(for_delivery_surname_name='surname_name', for_delivery_telephone_number='telephone_number',
                            for_delivery_time='time', for_delivery_create_time='create_time', for_delivery_zone='zone',
                            for_delivery_payment='payment')


@router.callback_query(F.data == 'bad')
async def second_check(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await set_order_status_false(surname_name=data['for_delivery_surname_name'],
                                 telephone_number=data['for_delivery_telephone_number'], time=data['for_delivery_time'],
                                 create_time=data['for_delivery_create_time'], zone=data['for_delivery_zone'],
                                 payment=data['for_delivery_payment'])
    await query.message.edit_text("Свяжемся с пользователем")
    tg_id = await get_user_tgid(data['for_delivery_surname_name'], data['for_delivery_telephone_number'])
    await add_banned_user(tg_id)
    bot = Bot(token=os.getenv('TOKEN'))
    text = 'Ваш аккаунт заморожен.\nНеоплаченный заказ:\n'
    order = await get_order_to_back(surname_name=data['for_delivery_surname_name'],
                                    telephone_number=data['for_delivery_telephone_number'],
                                    time=data['for_delivery_time'],
                                    create_time=data['for_delivery_create_time'], zone=data['for_delivery_zone'],
                                    payment=data['for_delivery_payment'])
    for i in order:
        text += f'{i}: '
        text += str(order[i])
        text += '\n'
    for j in range(30):
        text += '_'
    text += '\n'
    text += f'сумма заказа: {data["for_delivery_payment"]}\n'
    text += f'время: {data["for_delivery_time"]}\n'
    text += f'дата создания: {data["for_delivery_create_time"]}\n'
    text += f'зона доставки: {data["for_delivery_zone"]}\n'
    text += f'номер телефона: {data["for_delivery_telephone_number"]}'
    text2 = 'Неоплаченный заказ:\n'
    for i in order:
        text2 += f'{i}: '
        text2 += str(order[i])
        text2 += '\n'
    for j in range(30):
        text2 += '_'
    text2 += '\n'
    text2 += f'сумма заказа: {data["for_delivery_payment"]}\n'
    text2 += f'время: {data["for_delivery_time"]}\n'
    text2 += f'дата создания: {data["for_delivery_create_time"]}\n'
    text2 += f'зона доставки: {data["for_delivery_zone"]}\n'
    text2 += f'имя и фамилия: {data["for_delivery_surname_name"]}\n'
    text2 += f'номер телефона: {data["for_delivery_telephone_number"]}'
    await bot.send_message(tg_id,
                           text, reply_markup=kb.first_with_ban)
    await bot.send_message(os.getenv('WORKING_AKK'), text2)
    await state.update_data(for_delivery_surname_name='surname_name', for_delivery_telephone_number='telephone_number',
                            for_delivery_time='time', for_delivery_create_time='create_time', for_delivery_zone='zone',
                            for_delivery_payment='payment')


@router.callback_query(F.data == 'back_to_order_status')
async def second_check(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
#     print(data['for_delivery_surname_name'], data['for_delivery_telephone_number'], data['for_delivery_time'], data['for_delivery_create_time'], data['for_delivery_zone'], data['for_delivery_payment'])
    order = await get_order_to_back(surname_name=data['for_delivery_surname_name'],
                                    telephone_number=data['for_delivery_telephone_number'],
                                    time=data['for_delivery_time'],
                                    create_time=data['for_delivery_create_time'], zone=data['for_delivery_zone'],
                                    payment=data['for_delivery_payment'])
    text = 'заказ:\n'
    for i in order:
        text += f'{i}: '
        text += str(order[i])
        text += '\n'
    for j in range(30):
        text += '_'
    text += '\n'
    text += f'имя и фамилия: {data["for_delivery_surname_name"]}\n'
    text += f'номер телефона: {data["for_delivery_telephone_number"]}\n'
    text += f'время: {data["for_delivery_time"]}\n'
    text += f'дата создания: {data["for_delivery_create_time"]}\n'
    text += f'сумма заказа: {data["for_delivery_payment"]}\n'
    text += f'зона доставки: {data["for_delivery_zone"]}'
    if 'kurer_na_meste' in data:
        if data['kurer_na_meste']:
            await query.message.edit_text(text=text, reply_markup=kb.order_status)

        else:
            await query.message.edit_text(text=text, reply_markup=kb.order_status2)
    else:
        await query.message.edit_text(text=text, reply_markup=kb.order_status2)
    await state.update_data(for_delivery_surname_name='surname_name', for_delivery_telephone_number='telephone_number',
                            for_delivery_time='time', for_delivery_create_time='create_time', for_delivery_zone='zone',
                            for_delivery_payment='payment')
    # print(order)
    # await query.message.edit_text("Отлично")

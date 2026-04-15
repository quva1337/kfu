from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from datetime import datetime

price_list = {'Лосось в сливочном соусе': 1090,
              'Тилапия по-кантонски': 590,
              'Стейк Диана': 890,
              'Томленая говядина': 650,
              'Хинкали': 350,
              'Том Ям': 490,
              'Токмач': 350,
              'суп Грибной': 350,
              'Шурпа': 450,
              'Пельмени': 390,
              'паста Креветки и баклажан': 650,
              'Курица и грибы': 450,
              'Говядина Лао Мэн': 450,
              'Курица Мэй Фун': 390,
              'пицца Пепперони': 450,
              'пицца Цезарь': 550,
              'пицца Четыре мяса': 690,
              'пицца Стейк': 650,
              'пицца Ветчина и грибы': 450,
              'пицца Четыре сыра': 490,
              'пицца Маргарита': 350,
              'пицца Мединская утка': 590,
              'пицца Том Ям': 650,
              'пицца Примавера': 450,
              'пицца Тоскана': 450,
              'пицца Бавария': 450,
              'Салат Греческий': 650,
              'Салат Цезарь': 650,
              'Морс Облепиховый': 650,
              'Морс Клюквенный': 650,
              'Сэндвич с тунцом': 650,
              'Сэндвич с ветчиной': 650,
              'Сэндвич с фри и сосисками': 650,
              'Фри с сосисками': 650,
              'Паста с сыром и курицей': 650,
              'Паста с фрикадельками': 650}


class TimeButton(CallbackData, prefix='my'):
    time: str


class Promo(CallbackData, prefix='my'):
    have: bool


async def time_buttons():
    builder = InlineKeyboardBuilder()
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")  # строка
    current_time = datetime.strptime(current_time, "%H:%M:%S").time()

    # time1 = "10:25:00"
    # time2 = "14:05:00"
    times = ["08:55:00", "10:25:00", "12:25:00", "14:05:00", "16:05:00", "17:45:00", "23:59:00"]
    times_to_pokaz = ["10-00", "11-40", "13-40", "15-20", "17-20", "19-00", "23-59"]
    # times = ["08:55:00", "10:25:00", "12:25:00", "14:05:00", "16:05:00", "17:45:00"]
    # times_to_pokaz = ["10-00", "11-40", "13-40", "15-20", "17-20", "19-00"]
    for i in range(len(times)):
        times[i] = datetime.strptime(times[i], "%H:%M:%S").time()

    buttons = [True] * len(times)

    for i in range(len(times)):
        if current_time > times[i]:
            buttons[i] = False

    if all((not x) for x in buttons) or current_time < datetime.strptime("00:00:00",
                                                                         "%H:%M:%S").time():  # проверка что не слишком рано и не слишком поздно
        return False
    else:
        for i in range(len(times)):
            if buttons[i]:
                builder.button(text=f'{times_to_pokaz[i]}',
                               callback_data=TimeButton(time=times_to_pokaz[i]).pack())
        builder.adjust(3)
        return builder.as_markup()

    # first_time = datetime.strftime("08:45:00", "%H:%M:%S")


class Delivery_Zone_Button(CallbackData, prefix='my'):
    number: str
    name: str


class Uspeh(CallbackData, prefix='my'):
    uspeh: bool


async def zones_buttons():
    builder = InlineKeyboardBuilder()
    numbers_of_zones = ['1', '2']
    names_of_zones = ['Фое', 'Главный вход']

    for i in range(len(numbers_of_zones)):
        builder.button(text=f'{numbers_of_zones[i]} | {names_of_zones[i]}',
                       callback_data=Delivery_Zone_Button(number=numbers_of_zones[i],
                                                          name=names_of_zones[i]).pack())

    return builder.as_markup()


class Category(CallbackData, prefix='my'):
    name: str


class Bludo(CallbackData, prefix='my'):
    price: int
    name: str


class Back(CallbackData, prefix='my'):
    to_main: bool = False
    to_drinks: bool = False
    to_last_category: bool = False


class Drink(CallbackData, prefix='my'):
    name: str


first = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Сделать заказ'), KeyboardButton(text='Мой профиль')]
], resize_keyboard=True)

first_with_ban = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Сделать заказ'), KeyboardButton(text='Мой профиль')],
    [KeyboardButton(text='Разморозить аккаунт')]
], resize_keyboard=True)

category_kb = InlineKeyboardMarkup(inline_keyboard=[
    # [InlineKeyboardButton(text='Основное',
    #                       callback_data=Category(name='Основное').pack())],
    # [InlineKeyboardButton(text='Суп',
    #                     callback_data=Category(name='Суп').pack())],
    [InlineKeyboardButton(text='Паста',
                          callback_data=Category(name='Паста').pack())],
    [InlineKeyboardButton(text='Пицца',
                          callback_data=Category(name='Пицца Наполетана').pack())],
    [InlineKeyboardButton(text='Салаты',
                          callback_data=Category(name='Салаты').pack())],
    [InlineKeyboardButton(text='Сэндвичи',
                          callback_data=Category(name='Сэндвичи').pack())],
    [InlineKeyboardButton(text='Фри',
                          callback_data=Category(name='Фри').pack())],
    [InlineKeyboardButton(text='Морсы',
                          callback_data=Category(name='Морсы').pack())],
])

main_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Лосось в сливочном соусе - 1090₽',
                          callback_data=Bludo(price=1090, name='Лосось в сливочном соусе').pack())],
    [InlineKeyboardButton(text='Тилапия по-кантонски - 590₽',
                          callback_data=Bludo(price=590, name='Тилапия по-кантонски').pack())],
    [InlineKeyboardButton(text='Стейк Диана - 890₽',
                          callback_data=Bludo(price=890, name='Стейк Диана').pack())],
    [InlineKeyboardButton(text='Томленая говядина - 650₽',
                          callback_data=Bludo(price=650, name='Томленая говядина').pack())],
    [InlineKeyboardButton(text='Хинкали - 350₽',
                          callback_data=Bludo(price=350, name='Хинкали').pack())],
    [InlineKeyboardButton(text='⬅️ Назад',
                          callback_data=Back(to_main=True).pack())]
])

soup_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Том Ям - 490₽',
                          callback_data=Bludo(price=490, name='Том Ям').pack())],
    [InlineKeyboardButton(text='Токмач - 350₽',
                          callback_data=Bludo(price=350, name='Токмач').pack())],
    [InlineKeyboardButton(text='Грибной - 350₽',
                          callback_data=Bludo(price=350, name='суп Грибной').pack())],
    [InlineKeyboardButton(text='Шурпа - 450₽',
                          callback_data=Bludo(price=450, name='Шурпа').pack())],
    [InlineKeyboardButton(text='Пельмени - 390₽',
                          callback_data=Bludo(price=390, name='Пельмени').pack())],
    [InlineKeyboardButton(text='⬅️ Назад',
                          callback_data=Back(to_main=True).pack())]
])

pasta_and_wok_kb = InlineKeyboardMarkup(inline_keyboard=[
    # [InlineKeyboardButton(text='Креветки и баклажан - 650₽',
    #                       callback_data=Bludo(price=650, name='паста Креветки и баклажан').pack())],
    # [InlineKeyboardButton(text='Курица и грибы - 450₽',
    #                       callback_data=Bludo(price=450, name='Курица и грибы').pack())],
    # [InlineKeyboardButton(text='Говядина Лао Мэн - 450₽',
    #                       callback_data=Bludo(price=450, name='Говядина Лао Мэн').pack())],
    # [InlineKeyboardButton(text='Курица Мэй Фун - 390₽',
    #                       callback_data=Bludo(price=390, name='Курица Мэй Фун').pack())],
    [InlineKeyboardButton(text='Паста с фрикадельками - 650₽',
                          callback_data=Bludo(price=650, name='Паста с фрикадельками').pack())],
    [InlineKeyboardButton(text='Паста с сыром и курицей - 650₽',
                          callback_data=Bludo(price=650, name='Паста с сыром и курицей').pack())],
    [InlineKeyboardButton(text='⬅️ Назад',
                          callback_data=Back(to_main=True).pack())]
])

pizza_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Пепперони - 450₽',
                          callback_data=Bludo(price=450, name='пицца Пепперони').pack())],
    # [InlineKeyboardButton(text='Цезарь - 550₽',
    #                       callback_data=Bludo(price=550, name='пицца Цезарь').pack())],
    # [InlineKeyboardButton(text='Четыре мяса - 690₽',
    #                       callback_data=Bludo(price=690, name='пицца Четыре мяса').pack())],
    # [InlineKeyboardButton(text='Стейк - 650₽',
    #                       callback_data=Bludo(price=650, name='пицца Стейк').pack())],
    [InlineKeyboardButton(text='Ветчина и грибы - 450₽',
                          callback_data=Bludo(price=450, name='пицца Ветчина и грибы').pack())],
    # [InlineKeyboardButton(text='Четыре сыра - 490₽',
    #                       callback_data=Bludo(price=490, name='пицца Четыре сыра').pack())],
    # [InlineKeyboardButton(text='Маргарита - 350₽',
    #                       callback_data=Bludo(price=350, name='пицца Маргарита').pack())],
    # [InlineKeyboardButton(text='Мединская утка - 590₽',
    #                       callback_data=Bludo(price=590, name='пицца Мединская утка').pack())],
    # [InlineKeyboardButton(text='Том Ям - 650₽',
    #                       callback_data=Bludo(price=650, name='пицца Том Ям').pack())],
    # [InlineKeyboardButton(text='Примавера - 450₽',
    #                       callback_data=Bludo(price=450, name='пицца Примавера').pack())],
    [InlineKeyboardButton(text='Тоскана - 450₽',
                          callback_data=Bludo(price=450, name='пицца Тоскана').pack())],
    # [InlineKeyboardButton(text='Бавария - 450₽',
    #                       callback_data=Bludo(price=450, name='пицца    Бавария').pack())],
    [InlineKeyboardButton(text='⬅️ Назад',
                          callback_data=Back(to_main=True).pack())]
])
morses_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Морс клюквенный - 650₽',
                          callback_data=Bludo(price=650, name='Морс Клюквенный').pack())],
    [InlineKeyboardButton(text='Морс облепиховый - 650₽',
                          callback_data=Bludo(price=650, name='Морс Облепиховый').pack())],
    [InlineKeyboardButton(text='⬅️ Назад',
                          callback_data=Back(to_main=True).pack())]
])

free_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Фри с сосисками - 650₽',
                          callback_data=Bludo(price=650, name='Фри с сосисками').pack())],
    [InlineKeyboardButton(text='⬅️ Назад',
                          callback_data=Back(to_main=True).pack())]
])

salads_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Салат Греческий - 650₽',
                          callback_data=Bludo(price=650, name='Салат Греческий').pack())],
    [InlineKeyboardButton(text='Салат Цезарь - 650₽',
                          callback_data=Bludo(price=650, name='Салат Цезарь').pack())],
    [InlineKeyboardButton(text='⬅️ Назад',
                          callback_data=Back(to_main=True).pack())]
])

sandwiches_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Сэндвич с тунцом - 650₽',
                          callback_data=Bludo(price=650, name='Сэндвич с тунцом').pack())],
    [InlineKeyboardButton(text='Сэндвич с ветчиной - 650₽',
                          callback_data=Bludo(price=650, name='Сэндвич с ветчиной').pack())],
    [InlineKeyboardButton(text='Сэндвич с фри и сосисками - 650₽',
                          callback_data=Bludo(price=650, name='Сэндвич с фри и сосисками').pack())],
    [InlineKeyboardButton(text='⬅️ Назад',
                          callback_data=Back(to_main=True).pack())]
])

drinks_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Прохладительные',
                          callback_data=Drink(name='Прохладительные').pack())],
    [InlineKeyboardButton(text='Горячие',
                          callback_data=Drink(name='Горячие').pack())],
    [InlineKeyboardButton(text='Милкшейки',
                          callback_data=Drink(name='Милкшейки').pack())],
    [InlineKeyboardButton(text='Смузи и Фреши',
                          callback_data=Drink(name='Смузи и Фреши').pack())],
    [InlineKeyboardButton(text='⬅️ Назад',
                          callback_data=Back(to_main=True).pack())]
])

cold_drinks_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Эмиз Таврический - 490₽',
                          callback_data=Bludo(price=490, name='Эмиз Таврический').pack())],
    [InlineKeyboardButton(text='Виноградный напиток - 390₽',
                          callback_data=Bludo(price=390, name='Виноградный напиток').pack())],
    [InlineKeyboardButton(text='Солодовый напиток - 250₽',
                          callback_data=Bludo(price=250, name='Солодовый напиток').pack())],
    [InlineKeyboardButton(text='Морс клюква \ Облепиха - 90₽',
                          callback_data=Bludo(price=90, name='Морс клюква \ Облепиха').pack())],
    [InlineKeyboardButton(text='Добрый кола \ Сок - 150₽',
                          callback_data=Bludo(price=150, name='Добрый кола \ Сок').pack())],
    [InlineKeyboardButton(text='Лимонад Базр - 190₽',
                          callback_data=Bludo(price=190, name='Лимонад Базр').pack())],
    [InlineKeyboardButton(text='⬅️ Назад',
                          callback_data=Back(to_drinks=True).pack())]
])

hot_drinks_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Эмиз Таврический - 490₽',
                          callback_data=Bludo(price=490, name='Эмиз Таврический').pack())],
    [InlineKeyboardButton(text='Виноградный напиток - 390₽',
                          callback_data=Bludo(price=390, name='Виноградный напиток').pack())],
    [InlineKeyboardButton(text='Солодовый напиток - 250₽',
                          callback_data=Bludo(price=250, name='Солодовый напиток').pack())],
    [InlineKeyboardButton(text='Морс клюква \ Облепиха - 90₽',
                          callback_data=Bludo(price=90, name='Морс клюква \ Облепиха').pack())],
    [InlineKeyboardButton(text='Добрый кола \ Сок - 150₽',
                          callback_data=Bludo(price=150, name='Добрый кола \ Сок').pack())],
    [InlineKeyboardButton(text='Лимонад Базр - 190₽',
                          callback_data=Bludo(price=190, name='Лимонад Базр').pack())],
    [InlineKeyboardButton(text='⬅️ Назад',
                          callback_data=Back(to_drinks=True).pack())]
])

back_in_message = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⬅️ Назад', callback_data=Back(to_last_category=True).pack())]
])

category_withend_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Паста',
                          callback_data=Category(name='Паста').pack())],
    [InlineKeyboardButton(text='Пицца',
                          callback_data=Category(name='Пицца Наполетана').pack())],
    [InlineKeyboardButton(text='Салаты',
                          callback_data=Category(name='Салаты').pack())],
    [InlineKeyboardButton(text='Сэндвичи',
                          callback_data=Category(name='Сэндвичи').pack())],
    [InlineKeyboardButton(text='Фри',
                          callback_data=Category(name='Фри').pack())],
    [InlineKeyboardButton(text='Морсы',
                          callback_data=Category(name='Морсы').pack())],
    [InlineKeyboardButton(text='Завершить заказ',
                          callback_data='end_zakaz')]
])

drinks_withend_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Прохладительные',
                          callback_data=Drink(name='Прохладительные').pack())],
    [InlineKeyboardButton(text='Горячие',
                          callback_data=Drink(name='Горячие').pack())],
    [InlineKeyboardButton(text='Милкшейки',
                          callback_data=Drink(name='Милкшейки').pack())],
    [InlineKeyboardButton(text='Смузи и Фреши',
                          callback_data=Drink(name='Смузи и Фреши').pack())],
    [InlineKeyboardButton(text='⬅️ Назад',
                          callback_data=Back(to_main=True).pack())],
    [InlineKeyboardButton(text='Завершить заказ',
                          callback_data='end_zakaz')]
])

change_info = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Имя и фамилию',
                          callback_data='change_fio')],
    [InlineKeyboardButton(text='Номер телефона',
                          callback_data='change_telephone_number')]
])

order_status = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅', callback_data='uspeh'), InlineKeyboardButton(text='❌', callback_data='neuspeh')]
])

order_status2 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅', callback_data='uspeh'), InlineKeyboardButton(text='❌', callback_data='neuspeh')],
    [InlineKeyboardButton(text='Я на месте', callback_data='kurer_na_meste')]
])

status_yes_checking = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅', callback_data='nice'),
     InlineKeyboardButton(text='⬅️', callback_data='back_to_order_status')]
])

status_no_checking = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅', callback_data='bad'),
     InlineKeyboardButton(text='⬅️', callback_data='back_to_order_status')]
])

itog_ord = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅', callback_data='end_itog'),
     InlineKeyboardButton(text='❌', callback_data='ne_sostoyalsa')]
])

promo_checking = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data=Promo(have=True).pack()),
     InlineKeyboardButton(text='Нет', callback_data=Promo(have=False).pack())]
])

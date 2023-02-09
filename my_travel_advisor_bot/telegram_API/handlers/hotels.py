from datetime import datetime

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove, ContentTypes

from settings import logger_message, logger
from site_API.hotels import nearest_hotels, search_hotels
from telegram_API import keyboards
from telegram_API.calendar import SimpleCalendar, calendar_callback


class SearchHotels(StatesGroup):
    waiting_for_hotels_search = State()
    waiting_for_user_location = State()
    waiting_for_city = State()
    waiting_for_distance = State()
    waiting_for_stars = State()
    waiting_for_prices = State()
    waiting_for_checkin = State()
    waiting_for_nights = State()
    waiting_for_rooms = State()
    waiting_for_adults = State()
    waiting_for_child_rm_ages = State()
    waiting_for_count_results = State()
    waiting_for_confirm_results = State()
    waiting_for_price_level = State()
    waiting_for_min_price = State()
    waiting_for_max_price = State()


def is_date_valid(valid_date: str) -> bool:
    """
    Проверяет корректность введенной даты
    :param valid_date: проверяемая дата
    :type valid_date: str
    :return: True, если дата корректна, иначе False
    :rtype: bool
    """
    try:
        datetime.strptime(valid_date, "%d-%m-%Y")
        return True
    except (ValueError, TypeError, IndexError):
        logger.exception('Неверный формат даты. Укажите дату в формате "dd-mm-yyyy"')
        return False


async def start_search_hotels(message: types.Message, state: FSMContext):
    """
    Запускаем поиск по отелям
    :param state: статус
    :param message: сообщение от пользователя
    """
    logger_message.info(f'{message.from_user.first_name}: {message.text}')
    await message.answer('Я могу найти отели поблизости или в конкретном городе.',
                         reply_markup=keyboards.hotels_keyboard)
    await state.set_state(
        SearchHotels.waiting_for_hotels_search.state)


async def button_nearest_specific(call: types.CallbackQuery, state: FSMContext):
    """
    Обработка результатов зоны поиска по отелям
    """
    logger_message.info(f'{call.from_user.first_name}: {call.data}')
    await state.update_data(zone=call.data)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer()
    if call.data == 'nearest_hotels':
        await call.message.answer(text='Ищем ближайшие отели.\nДля этого необходимо отправить вашу геопозицию, '
                                       'используя клавиатуру ниже.', reply_markup=keyboards.request_geo)
        await state.set_state(SearchHotels.waiting_for_user_location.state)
    elif call.data == 'specific_hotels':
        await call.message.answer(text='Ищем отели в конкретном городе. Для этого, укажите интересующий вас город.')
        await state.set_state(SearchHotels.waiting_for_city.state)


async def request_geo(message: types.Message, state: FSMContext):
    """
    Запрашиваем геопозицию пользователя
    :param message: сообщение от пользователя
    :param state: статус
    """
    logger_message.info(f'{message.from_user.first_name}: {message.text}')
    if not message.location:
        await message.answer('Пожалуйста, отправьте вашу геопозицию, используя клавиатуру ниже.')
        return
    await state.update_data(coordinates=message.location)
    await message.answer('Укажите удаленность поиска. Максимальное значение 25 км.', reply_markup=ReplyKeyboardRemove())
    await state.set_state(SearchHotels.waiting_for_distance.state)


async def request_city(message: types.Message, state: FSMContext):
    """
    Ищем отели в конкретном городе
    :param message: сообщение от пользователя
    :param state: статус
    """
    logger_message.info(f'{message.from_user.first_name}: {message.text}')
    await state.update_data(city_for_search=message.text)
    await message.answer('Укажите количество звезд отеля. Можно перечислить через запятую.')
    await state.set_state(SearchHotels.waiting_for_stars.state)


async def distance(message: types.Message, state: FSMContext):
    """
    Запрашиваем удаленность от искомого места
    :param message: сообщение от пользователя
    :param state: статус
    """
    logger_message.info(f'{message.from_user.first_name}: {message.text}')
    if not message.text.isdigit() or not 0 < int(message.text) <= 25:
        await message.answer('Пожалуйста, укажите корректные данные (от 1 до 25 включительно).')
        return
    await state.update_data(distance=int(message.text))
    await message.answer('Укажите количество звезд отеля. Можно перечислить через запятую.')
    await state.set_state(SearchHotels.waiting_for_stars.state)


async def stars_hotels(message: types.Message, state: FSMContext):
    """
    Выбор количества звезд отеля
    :param message: сообщение от пользователя
    :param state: статус
    """
    logger_message.info(f'{message.from_user.first_name}: {message.text}')
    stars = message.text.split(',')
    try:
        for index in range(len(stars)):
            stars[index] = int(stars[index])
            if not 0 < stars[index] <= 5:
                raise ValueError
    except ValueError:
        logger.exception('произошла ошибка при записи данных о количестве звезд отеля:')
        await message.answer('Пожалуйста, укажите корректные данные (от 1 до 5 включительно).')
        return
    else:
        stars = [str(i_star) for i_star in stars]
        await state.update_data(stars=stars)
        await message.answer(
            '1. Я могу найти список отелей по диапазону цен.\n2. Могу найти отели по минимальной стоимости.'
            '\n3. Могу найти отели по максимальной стоимости.\nПожалуйста, выберите.',
            reply_markup=keyboards.keyboard_hotels_price)
        await state.set_state(SearchHotels.waiting_for_price_level.state)


async def price_level_hotels(call: types.CallbackQuery, state: FSMContext):
    """
    Выбор условий поиска отелей по цене
    :param call: данные от пользователя
    :param state: статус
    """
    logger_message.info(f'{call.from_user.first_name}: {call.data}')
    await state.update_data(price_level=call.data)
    await call.answer()
    price_level = call.data
    if price_level == 'price_range':
        await call.message.answer('Укажите диапазон цен (в рублях) через пробел.')
        await state.set_state(SearchHotels.waiting_for_prices.state)
    elif price_level == 'min_price':
        await call.message.answer('Укажите минимальную стоимость за ночь (в рублях).')
        await state.set_state(SearchHotels.waiting_for_min_price.state)
    elif price_level == 'max_price':
        await call.message.answer('Укажите максимальную стоимость за ночь (в рублях).')
        await state.set_state(SearchHotels.waiting_for_max_price.state)
    else:
        logger_message.info(f'Ошибка по диапазону цен...{call.from_user.first_name}: {call.data}')


async def request_price_range(message: types.Message, state: FSMContext):
    """
    Запрос цен
    :param message: сообщение от пользователя
    :param state: статус
    """
    logger_message.info(f'{message.from_user.first_name}: {message.text}')
    prices = message.text.split()
    try:
        assert len(prices) == 2
        for index in range(len(prices)):
            prices[index] = int(prices[index])
        prices = [min(prices), max(prices)]
        prices = [str(price) for price in prices]
    except (ValueError, AssertionError):
        logger.exception('произошла ошибка при записи данных о диапазоне цен:')
        await message.answer('Пожалуйста, укажите корректные данные.')
        return
    else:
        await state.update_data(prices=prices)
        await message.answer(f'Укажите дату заезда в формате: число-месяц-год '
                             f'(пример: {datetime.now().strftime("%d-%m-%Y")}) или выберите дату в календаре.',
                             reply_markup=await SimpleCalendar().start_calendar())
        await state.set_state(SearchHotels.waiting_for_checkin.state)


async def request_price_min(message: types.Message, state: FSMContext):
    """
    Обработка запроса минимальной цены
    :param message:
    :param state:
    """
    logger_message.info(f'{message.from_user.first_name}: {message.text}')
    min_price = message.text.split()
    try:
        assert len(min_price) == 1
        min_price = int(min_price[0])
    except (ValueError, AssertionError):
        logger.exception('произошла ошибка при записи данных о диапазоне цен:')
        await message.answer('Пожалуйста, укажите корректные данные.')
        return
    else:
        await state.update_data(min_price=str(min_price))
        await message.answer(f'Укажите дату заезда в формате: число-месяц-год '
                             f'(пример: {datetime.now().strftime("%d-%m-%Y")}) или выберите дату в календаре.',
                             reply_markup=await SimpleCalendar().start_calendar())
        await state.set_state(SearchHotels.waiting_for_checkin.state)


async def request_price_max(message: types.Message, state: FSMContext):
    """
    Обработка запроса максимальной цены
    :param message:
    :param state:
    """
    logger_message.info(f'{message.from_user.first_name}: {message.text}')
    max_price = message.text.split()
    try:
        assert len(max_price) == 1
        max_price = int(max_price[0])
    except (ValueError, AssertionError):
        logger.exception('произошла ошибка при записи данных о диапазоне цен:')
        await message.answer('Пожалуйста, укажите корректные данные.')
        return
    else:
        await state.update_data(max_price=str(max_price))
        await message.answer(f'Укажите дату заезда в формате: число-месяц-год '
                             f'(пример: {datetime.now().strftime("%d-%m-%Y")}) или выберите дату в календаре.',
                             reply_markup=await SimpleCalendar().start_calendar())
        await state.set_state(SearchHotels.waiting_for_checkin.state)


async def process_input_checkin(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """
    Выбор даты заезда с помощью календаря
    :param callback_query: запрос от пользователя
    :param callback_data: данные
    :param state: статус
    """
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        logger_message.info(f'{selected}: {date.strftime("%d-%m-%Y")}')
        await callback_query.message.answer(f'Вы указали дату: {date.strftime("%d-%m-%Y")}')
        await state.update_data(checkin=str(date.strftime("%d-%m-%Y")))
        await callback_query.message.answer('Укажите количество ночей.')
        await state.set_state(SearchHotels.waiting_for_nights.state)


async def request_checkin(message: types.Message, state: FSMContext):
    """
    Запрос даты, введенной с клавиатуры
    :param message: сообщение от пользователя
    :param state: статус
    """
    logger_message.info(f'{message.from_user.first_name}: {message.text}')
    if not is_date_valid(message.text):
        await message.answer(f'Укажите дату заезда в формате: число-месяц-год '
                             f'(пример: {datetime.now().strftime("%d-%m-%Y")}) или выберите дату в календаре.',
                             reply_markup=await SimpleCalendar().start_calendar())
        return
    await message.answer(f'Вы указали дату: {message.text}.')
    await state.update_data(checkin=message.text)
    await message.answer('Укажите количество ночей.')
    await state.set_state(SearchHotels.waiting_for_nights.state)


async def request_nights(message: types.Message, state: FSMContext):
    """
    Запрос количества ночей
    :param message: сообщение от пользователя
    :param state: статус
    """
    logger_message.info(f'{message.from_user.first_name}: {message.text}')
    if not message.text.isdigit():
        await message.answer('Пожалуйста, укажите корректные данные в виде числа.')
        return
    await state.update_data(nights=int(message.text))
    await state.set_state(SearchHotels.waiting_for_rooms.state)
    await message.answer('Укажите количество номеров.')


async def request_rooms(message: types.Message, state: FSMContext):
    """
    Запрос количества номеров
    :param message: сообщение от пользователя
    :param state: статус
    """
    logger_message.info(f'{message.from_user.first_name}: {message.text}')
    if not message.text.isdigit():
        await message.answer('Пожалуйста, укажите корректные данные в виде числа.')
        return
    await state.update_data(rooms=int(message.text))
    await state.set_state(SearchHotels.waiting_for_adults.state)
    await message.answer('Укажите количество взрослых въезжающих.')


async def request_adults(message: types.Message, state: FSMContext):
    """
    Запрос количества взрослых въезжающих
    :param message: сообщение от пользователя
    :param state: статус
    """
    logger_message.info(f'{message.from_user.first_name}: {message.text}')
    if not message.text.isdigit():
        await message.answer('Пожалуйста, укажите корректные данные в виде числа.')
        return
    await state.update_data(adults=int(message.text))
    await state.set_state(SearchHotels.waiting_for_child_rm_ages.state)
    await message.answer('Укажите возраст детей, через пробел. Если детей нет, укажите ноль.')


async def request_for_child_rm_ages(message: types.Message, state: FSMContext):
    """
    Запрос возраста детей
    :param message: сообщение от пользователя
    :param state: статус
    """
    logger_message.info(f'{message.from_user.first_name}: {message.text}')
    ages = message.text
    if ages != '0':
        try:
            ages = ages.split()
            for i_age in ages:
                if not i_age.isdigit():
                    raise ValueError('Неверные данные о возрасте детей.')
        except ValueError:
            logger.exception('произошла ошибка при записи данных о возрасте детей:')
            await message.answer('Пожалуйста, укажите корректные данные.')
            return
    await state.update_data(child_rm_ages=ages)
    await state.set_state(SearchHotels.waiting_for_count_results.state)
    await message.answer('Сколько результатов необходимо показать? Максимум, доступно 30 результатов.')


async def request_count_results(message: types.Message, state: FSMContext):
    """
    Запрос количества выдаваемых результатов
    :param message: сообщение от пользователя
    :param state: статус
    """
    logger_message.info(f'{message.from_user.first_name}: {message.text}')
    if not message.text.isdigit() or not 0 < int(message.text) <= 30:
        await message.answer('Пожалуйста, укажите корректные данные (от 1 до 30 включительно).')
        return
    await state.update_data(count_results=int(message.text))
    user_data = await state.get_data()
    zone = user_data.get('zone')
    stars = user_data.get('stars')
    if user_data.get('prices'):
        price = f'Диапазон цен: {" - ".join(user_data.get("prices"))}'
    elif user_data.get('min_price'):
        price = f'Минимальная цена за ночь: {"".join(user_data.get("min_price"))}'
    elif user_data.get('max_price'):
        price = f'Максимальная цена за ночь: {"".join(user_data.get("max_price"))}'
    else:
        price = '0'
        logger_message.info(f'ошибка при получении данных о цене {message.from_user.first_name}: {message.text}')
    checkin = user_data.get('checkin')
    nights = user_data.get('nights')
    rooms = user_data.get('rooms')
    adults = user_data.get('adults')
    child_rm_ages = user_data.get('child_rm_ages')
    count_res = user_data.get('count_results')
    if zone == 'nearest_hotels':
        coordinates = [str(user_data['coordinates']['latitude']), str(user_data['coordinates']['longitude'])]
        distance_res = user_data['distance']
        await message.answer(f'Вы указали:\nКоординаты: {", ".join(coordinates)}\n'
                             f'Удаленность поиска: {distance_res} км.\n'
                             f'Количество звезд отеля: {", ".join(stars)}\n'
                             f'{price} руб.\n'
                             f'Дата заезда: {checkin}\n'
                             f'Количество ночей: {nights}\n'
                             f'Количество номеров: {rooms}\n'
                             f'Количество взрослых: {adults}\n'
                             f'Возраст детей: {"-".join(child_rm_ages)}\n'
                             f'Количество выдаваемых результатов: {count_res}\n'
                             f'Всё верно?',
                             reply_markup=keyboards.yes_no_keyboard)
        await state.set_state(SearchHotels.waiting_for_confirm_results.state)
    else:
        city = user_data['city_for_search']
        await message.answer(f'Вы указали:\nГород поиска: {city}\n'
                             f'Количество звезд отеля: {", ".join(stars)}\n'
                             f'{price} руб.\n'
                             f'Дата заезда: {checkin}\n'
                             f'Количество ночей: {nights}\n'
                             f'Количество номеров: {rooms}\n'
                             f'Количество взрослых: {adults}\n'
                             f'Возраст детей: '
                             f'{", ".join(child_rm_ages) if len(child_rm_ages) != 1 else "".join(child_rm_ages)}\n'
                             f'Количество выдаваемых результатов: {count_res}\n'
                             f'Всё верно?',
                             reply_markup=keyboards.yes_no_keyboard)
        await state.set_state(SearchHotels.waiting_for_confirm_results.state)


async def confirm_button(call: types.CallbackQuery, state: FSMContext):
    """
    Подтверждение данных для запроса
    """
    user = [call.message.chat.id, call.message.chat.username, call.message.chat.first_name]
    logger_message.info(f'{call.from_user.first_name}: {call.data}')
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer()
    user_data = await state.get_data()
    await state.finish()
    zone = user_data.get('zone')
    if call.data == 'confirm':
        if zone == 'nearest_hotels':
            await call.message.answer('Пожалуйста, подождите, обрабатываю ваш запрос.',
                                      reply_markup=ReplyKeyboardRemove())
            results = nearest_hotels(user=user, data=user_data)
            await output_data(call, results)
        else:
            await call.message.answer('Пожалуйста, подождите, обрабатываю ваш запрос.',
                                      reply_markup=ReplyKeyboardRemove())
            results = search_hotels(user=user, data=user_data)
            await output_data(call, results)
    else:
        await call.message.answer('Действие отменено.',
                                  reply_markup=ReplyKeyboardRemove())


async def output_data(call, results):
    for n, i_data in enumerate(results):
        hotel_data = i_data[0]
        hotel_coordinates = i_data[1]
        await call.message.answer(text=f'<u><b>Результат №{n + 1}</b></u>\n{hotel_data}', parse_mode='HTML')
        if hotel_coordinates is not None:
            await call.message.answer_location(hotel_coordinates[0], hotel_coordinates[1])


def register_handlers_search_hotels(dps: Dispatcher):
    """
    Регистрируем все обработчики
    :param dps: диспетчер
    """
    dps.register_message_handler(start_search_hotels, commands="hotels", state="*")
    dps.register_message_handler(request_geo, state=SearchHotels.waiting_for_user_location,
                                 content_types=ContentTypes.LOCATION)
    dps.register_message_handler(distance, state=SearchHotels.waiting_for_distance)
    dps.register_message_handler(request_city, state=SearchHotels.waiting_for_city)
    dps.register_message_handler(stars_hotels, state=SearchHotels.waiting_for_stars)
    dps.register_message_handler(request_price_range, state=SearchHotels.waiting_for_prices)
    dps.register_message_handler(request_checkin, state=SearchHotels.waiting_for_checkin)
    dps.register_message_handler(request_nights, state=SearchHotels.waiting_for_nights)
    dps.register_message_handler(request_rooms, state=SearchHotels.waiting_for_rooms)
    dps.register_message_handler(request_adults, state=SearchHotels.waiting_for_adults)
    dps.register_message_handler(request_for_child_rm_ages, state=SearchHotels.waiting_for_child_rm_ages)
    dps.register_message_handler(request_count_results, state=SearchHotels.waiting_for_count_results)
    dps.register_message_handler(request_price_min, state=SearchHotels.waiting_for_min_price)
    dps.register_message_handler(request_price_max, state=SearchHotels.waiting_for_max_price)


def register_callbacks_hotels(dps: Dispatcher):
    """
    Регистрация коллбэков
    :param dps: диспетчер
    """
    dps.register_callback_query_handler(button_nearest_specific, Text(['nearest_hotels', 'specific_hotels']),
                                        state=SearchHotels.waiting_for_hotels_search.state)
    dps.register_callback_query_handler(confirm_button, state=SearchHotels.waiting_for_confirm_results)
    dps.register_callback_query_handler(process_input_checkin, calendar_callback.filter(),
                                        state=SearchHotels.waiting_for_checkin)
    dps.register_callback_query_handler(price_level_hotels, state=SearchHotels.waiting_for_price_level)

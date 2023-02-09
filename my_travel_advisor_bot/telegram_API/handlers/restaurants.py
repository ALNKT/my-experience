from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentTypes, ReplyKeyboardRemove

from settings import logger_message
from site_API.restaurants import nearest_restaurants, search_restaurants
from aiogram.dispatcher.filters.state import StatesGroup, State

from telegram_API import keyboards


class SearchRestaurants(StatesGroup):
    waiting_for_place_search = State()
    waiting_for_user_location = State()
    waiting_for_count_results = State()
    waiting_for_distance = State()
    waiting_for_city = State()
    waiting_for_confirm_nearest = State()
    waiting_for_confirm_city = State()


async def start_search_restaurants(message: types.Message, state: FSMContext):
    """
    Запускаем поиск по ресторанам
    :param state: статус
    :param message: сообщение от пользователя
    """
    logger_message.info(f'{message.from_user.first_name}: {message.text}')
    await message.answer('Я могу найти рестораны поблизости или в конкретном городе.',
                         reply_markup=keyboards.restaurants_keyboard)
    await state.set_state(SearchRestaurants.waiting_for_place_search.state)  # ожидаем ответа на сообщение (поблизости или город)


async def search_nearest_restaurants(message: types.Message, state: FSMContext):
    """
    Ищем рестораны поблизости
    :param message: сообщение от пользователя
    :param state: статус
    """
    logger_message.info(f'{message.from_user.first_name}: {message.text}')
    if message.text in 'Хочу найти ближайшие ко мне рестораны.':
        await message.answer('Мне нужно определить вашу геопозицию.', reply_markup=keyboards.request_geo)
        await state.set_state(SearchRestaurants.waiting_for_user_location.state)
    elif message.text == 'Хочу найти рестораны в конкретном городе.':
        await message.answer('Укажите город.', reply_markup=ReplyKeyboardRemove())
        await state.set_state(SearchRestaurants.waiting_for_city.state)
    else:
        await message.answer('Некорректный запрос, пожалуйста повторите.')


async def request_city(message: types.Message, state: FSMContext):
    """
    Ищем рестораны в конкретном городе
    :param message: сообщение от пользователя
    :param state: статус
    """
    logger_message.info(f'{message.from_user.first_name}: {message.text}')
    await state.update_data(city_for_search=message.text)
    await state.set_state(SearchRestaurants.waiting_for_count_results.state)
    await message.answer('Сколько результатов необходимо показать? Максимум, доступно 30 результатов.',
                         reply_markup=ReplyKeyboardRemove())


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
    await state.set_state(SearchRestaurants.waiting_for_distance.state)
    await message.answer('Укажите удаленность поиска. Максимальное значение 10 км.', reply_markup=ReplyKeyboardRemove())


async def distance(message: types.Message, state: FSMContext):
    """
    Запрашиваем удаленность от искомого места
    :param message: сообщение от пользователя
    :param state: статус
    """
    logger_message.info(f'{message.from_user.first_name}: {message.text}')
    if not message.text.isdigit() or not 0 < int(message.text) <= 10:
        await message.answer('Пожалуйста, укажите корректные данные (от 1 до 10 включительно).')
        return
    await state.update_data(distance=int(message.text))
    await state.set_state(SearchRestaurants.waiting_for_count_results.state)
    await message.answer('Сколько результатов необходимо показать? Максимум, доступно 30 результатов.')


async def count_results(message: types.Message, state: FSMContext):
    """
    Запрашиваем количество выдаваемых результатов
    :param message: сообщение от пользователя
    :param state: статус
    """
    logger_message.info(f'{message.from_user.first_name}: {message.text}')
    if not message.text.isdigit() or not 0 < int(message.text) <= 30:
        await message.answer('Пожалуйста, укажите корректные данные (от 1 до 30 включительно).')
        return
    await state.update_data(count_results=int(message.text))
    user_data = await state.get_data()
    if 'coordinates' in user_data:
        coordinates = [str(user_data['coordinates']['latitude']), str(user_data['coordinates']['longitude'])]
        count_res = user_data['count_results']
        distance_res = user_data['distance']
        await state.set_state(SearchRestaurants.waiting_for_confirm_nearest.state)
        await message.answer(f'Вы указали:\nКоординаты: {", ".join(coordinates)}\nКоличество результатов: {count_res}\n'
                             f'Удаленность поиска: {distance_res} км.\nВсё верно?',
                             reply_markup=keyboards.confirm_keyboard)
    else:
        city = user_data['city_for_search']
        count_res = user_data['count_results']
        await state.set_state(SearchRestaurants.waiting_for_confirm_city.state)
        await message.answer(f'Вы указали:\nГород поиска: {city}\nКоличество результатов: {count_res}.\nВсё верно?',
                             reply_markup=keyboards.confirm_keyboard)


async def confirmed_data(message: types.Message, state: FSMContext):
    """
    Обрабатываем данные от пользователя или отмена действия
    :param message: сообщение от пользователя
    :param state: статус
    """
    user = [message.from_user.id, message.from_user.username, message.from_user.first_name]
    logger_message.info(f'{message.from_user.first_name}: {message.text}')
    user_data = await state.get_data()
    await state.finish()
    if 'coordinates' in user_data:
        coordinates = (user_data['coordinates']['latitude'], user_data['coordinates']['longitude'])
        count_res = user_data['count_results']
        distance_res = user_data['distance']
        await state.finish()
        await message.answer('Пожалуйста, подождите, обрабатываю ваш запрос.', reply_markup=ReplyKeyboardRemove())
        results = nearest_restaurants(user=user, coordinates=coordinates, count=count_res, distance_search=distance_res)
        for n, i_data in enumerate(results):
            restaurant_data = i_data[0]
            restaurant_coordinates = i_data[1]
            await message.answer(text=f'<u><b>Результат №{n + 1}</b></u>\n{restaurant_data}', parse_mode='HTML')
            if restaurant_coordinates is not None:
                await message.answer_location(restaurant_coordinates[0], restaurant_coordinates[1])

    else:
        city = user_data['city_for_search']
        count_res = user_data['count_results']
        await state.finish()
        await message.answer('Пожалуйста, подождите, обрабатываю ваш запрос.', reply_markup=ReplyKeyboardRemove())
        results = search_restaurants(user=user, city=city, count=count_res)
        for n, i_data in enumerate(results):
            restaurant_data = i_data[0]
            restaurant_coordinates = i_data[1]
            await message.answer(text=f'<u><b>Результат №{n + 1}</b></u>\n{restaurant_data}', parse_mode='HTML')
            if restaurant_coordinates is not None:
                await message.answer_location(restaurant_coordinates[0], restaurant_coordinates[1])


def register_handlers_search_restaurants(dps: Dispatcher):
    """
    Регистрируем все обработчики
    :param dps: диспетчер
    """
    dps.register_message_handler(start_search_restaurants, commands="restaurants", state="*")
    dps.register_message_handler(search_nearest_restaurants, state=SearchRestaurants.waiting_for_place_search)
    dps.register_message_handler(request_geo, state=SearchRestaurants.waiting_for_user_location,
                                 content_types=ContentTypes.LOCATION)
    dps.register_message_handler(count_results, state=SearchRestaurants.waiting_for_count_results)
    dps.register_message_handler(distance, state=SearchRestaurants.waiting_for_distance)
    dps.register_message_handler(request_city, state=SearchRestaurants.waiting_for_city)
    dps.register_message_handler(confirmed_data, state=[SearchRestaurants.waiting_for_confirm_nearest,
                                 SearchRestaurants.waiting_for_confirm_city])

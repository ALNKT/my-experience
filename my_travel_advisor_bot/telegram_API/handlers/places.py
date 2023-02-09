from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove, ContentTypes

from settings import logger_message
from site_API.places import nearest_places, search_places
from telegram_API import keyboards


class SearchPlaces(StatesGroup):
    waiting_for_place_search = State()
    waiting_for_user_location = State()
    waiting_for_count_results = State()
    waiting_for_distance = State()
    waiting_for_city = State()
    waiting_for_confirm_nearest = State()
    waiting_for_confirm_city = State()


async def start_search_places(message: types.Message, state: FSMContext):
    """
    Запускаем поиск по местам
    :param state: статус
    :param message: сообщение от пользователя
    """
    logger_message.info(f'{message.from_user.first_name}: {message.text}')
    await message.answer('Я могу найти достопримечательности поблизости или в конкретном городе.',
                         reply_markup=keyboards.places_keyboard)
    await state.set_state(
        SearchPlaces.waiting_for_place_search.state)  # ожидаем ответа на сообщение (поблизости или город)


async def button_nearest_specific(call: types.CallbackQuery, state: FSMContext):
    """
    Обработка результатов зоны поиска по местам
    """
    logger_message.info(f'{call.from_user.first_name}: {call.data}')
    await state.update_data(zone=call.data)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer()
    if call.data == 'nearest_places':
        await call.message.answer(text='Ищем ближайшие места.\nДля этого необходимо отправить вашу геопозицию, '
                                       'используя клавиатуру ниже.', reply_markup=keyboards.request_geo)
        await state.set_state(SearchPlaces.waiting_for_user_location.state)
    elif call.data == 'specific_places':
        await call.message.answer(text='Ищем места в конкретном городе. Для этого, укажите интересующий вас город.')
        await state.set_state(SearchPlaces.waiting_for_city.state)


async def request_city(message: types.Message, state: FSMContext):
    """
    Ищем места в конкретном городе
    :param message: сообщение от пользователя
    :param state: статус
    """
    logger_message.info(f'{message.from_user.first_name}: {message.text}')
    await state.update_data(city_for_search=message.text)
    await message.answer('Сколько результатов необходимо показать? Максимум, доступно 30 результатов.')
    await state.set_state(SearchPlaces.waiting_for_count_results.state)


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
    await state.set_state(SearchPlaces.waiting_for_distance.state)


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
    await message.answer('Сколько результатов необходимо показать? Максимум, доступно 30 результатов.')
    await state.set_state(SearchPlaces.waiting_for_count_results.state)


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
        coordinates = (str(user_data['coordinates']['latitude']), str(user_data['coordinates']['longitude']))
        count_res = user_data['count_results']
        distance_res = user_data['distance']
        await message.answer(f'Вы указали:\nКоординаты: {", ".join(coordinates)}\nКоличество результатов: {count_res}\n'
                             f'Удаленность поиска: {distance_res} км.\nВсё верно?',
                             reply_markup=keyboards.yes_no_keyboard)
        await state.set_state(SearchPlaces.waiting_for_confirm_nearest.state)
    else:
        city = user_data['city_for_search']
        count_res = user_data['count_results']
        await state.set_state(SearchPlaces.waiting_for_confirm_city.state)
        await message.answer(f'Вы указали:\nГород поиска: {city}\nКоличество результатов: {count_res}.\nВсё верно?',
                             reply_markup=keyboards.yes_no_keyboard)


async def confirm_button(call: types.CallbackQuery, state: FSMContext):
    """
    Подтверждение данных для запроса
    """
    logger_message.info(f'{call.from_user.first_name}: {call.data}')
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer()
    user_data = await state.get_data()
    await state.finish()
    user = [call.message.chat.id, call.message.chat.username, call.message.chat.first_name]
    if call.data == 'confirm':
        if 'coordinates' in user_data:
            coordinates = (user_data['coordinates']['latitude'], user_data['coordinates']['longitude'])
            count_res = user_data['count_results']
            distance_res = user_data['distance']
            await call.message.answer('Пожалуйста, подождите, обрабатываю ваш запрос.',
                                      reply_markup=ReplyKeyboardRemove())
            results = nearest_places(user=user, coordinates=coordinates, count=count_res, distance_search=distance_res)
            await output_data(call, results)
        else:
            city = user_data['city_for_search']
            count_res = user_data['count_results']
            await state.finish()
            await call.message.answer('Пожалуйста, подождите, обрабатываю ваш запрос.',
                                      reply_markup=ReplyKeyboardRemove())
            results = search_places(user=user, city=city, count=count_res)
            await output_data(call, results)

    else:
        await call.message.answer('Действие отменено.',
                                  reply_markup=ReplyKeyboardRemove())


async def output_data(call, results):
    for n, i_data in enumerate(results):
        place_data = i_data[0]
        place_coordinates = i_data[1]
        await call.message.answer(text=f'<u><b>Результат №{n + 1}</b></u>\n{place_data}', parse_mode='HTML')
        if place_coordinates is not None:
            await call.message.answer_location(place_coordinates[0], place_coordinates[1])


def register_handlers_search_places(dps: Dispatcher):
    """
    Регистрируем все обработчики
    :param dps: диспетчер
    """
    dps.register_message_handler(start_search_places, commands="places", state="*")
    dps.register_message_handler(request_geo, state=SearchPlaces.waiting_for_user_location,
                                 content_types=ContentTypes.LOCATION)
    dps.register_message_handler(distance, state=SearchPlaces.waiting_for_distance)
    dps.register_message_handler(count_results, state=SearchPlaces.waiting_for_count_results)
    dps.register_message_handler(request_city, state=SearchPlaces.waiting_for_city)


def register_callbacks_places(dps: Dispatcher):
    """
    Регистрация коллбэков
    :param dps: диспетчер
    """
    dps.register_callback_query_handler(button_nearest_specific, Text(['nearest_places', 'specific_places']),
                                        state=SearchPlaces.waiting_for_place_search)
    dps.register_callback_query_handler(confirm_button, Text(['confirm', 'cancel']),
                                        state=[SearchPlaces.waiting_for_confirm_city,
                                               SearchPlaces.waiting_for_confirm_nearest])

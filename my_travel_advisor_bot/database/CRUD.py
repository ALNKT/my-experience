import datetime
import json

from database.models import db, Users, RequestsHotels, RequestsRestaurants, RequestsAttractions, LocationId
from settings import logger


def init_db():
    """
    Инициализация базы данных
    """
    db.connect()
    db.create_tables([Users, RequestsHotels, RequestsRestaurants, RequestsAttractions, LocationId])


def close_db():
    """
    Закрытие базы данных
    :return:
    """
    db.close()


def check_user_db(user):
    """
    Проверка наличия пользователя в базе данных
    :param user: username пользователя
    :return: bool
    """
    user_id, username, first_name = user
    if Users.select(Users.user_id_tg).where(Users.user_id_tg == user_id):
        return Users.get(Users.user_id_tg == user_id)
    record_user_db(user=user)
    return Users.get(Users.user_id_tg == user_id)


def check_city_db(city: str):
    """
    Проверка наличия города в базе данных
    :param city: город
    :return: bool
    """
    if LocationId.select(LocationId.city).where(LocationId.city == city):
        return True
    return False


def record_user_db(user):
    """
    Занесение пользователя в базу данных. Предварительно проверяем его наличие в таблице
    :param user: данные пользователя
    """
    user_id, username, first_name = user
    date = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    data_command = Users(date=date, user_id_tg=user_id, username=username, first_name=first_name)
    data_command.save()


def record_request(user, request, table, date=datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")):
    """
    Запись данных в таблицу с запросами пользователя
    :param user: данные пользователя
    :param date: текущая дата
    :param table: таблица, в которую записывать данные
    :param request: запрос пользователя
    """
    user_id = check_user_db(user=user)
    table(date=date, user_id=user_id, request=json.dumps(request, ensure_ascii=False)).save()


def record_location_city(location_city):
    """
    Запись location_id города в базу данных
    :param location_city: location_id города
    """
    try:
        location_id, city = location_city[0], location_city[1].lower()
        if not check_city_db(city):
            LocationId(location_id=location_id, city=city).save()
    except AttributeError:
        logger.exception('произошла ошибка при записи данных о населенном пункте:')


def read_location_city_from_db(city):
    """
    Получение location_id города из базы
    :param city: наименование города
    :return: location_id города
    """
    city = city.lower()
    if LocationId.select(LocationId.location_id).where(LocationId.city == city):
        return LocationId.get(LocationId.city == city).location_id
    return False


def read_data(user, category, count=1):
    """
    Получение данных из базы
    :param user: данные пользователя
    :param category: категория
    :param count: количество записей
    """
    user_id = check_user_db(user)
    if user_id:
        if category == 'restaurants':
            table = RequestsRestaurants
        elif category == 'hotels':
            table = RequestsHotels
        elif category == 'places':
            table = RequestsAttractions
        else:
            print(f'Неизвестная категория {category}')
            return
        data = table.select().where(table.user_id == user_id).\
            order_by(table.id.desc()).limit(count)
        if data:
            for i_data in data[::-1]:
                i_data = json.loads(i_data.request)
                if isinstance(i_data, str):
                    yield i_data, None
                else:
                    for i_result in i_data:
                        data_of_category, coordinates = i_result
                        yield data_of_category, coordinates
        else:
            yield 'Данные не обнаружены. Пожалуйста, сделайте первый запрос.', None
    else:
        yield 'Данные не обнаружены. Пожалуйста, сделайте первый запрос.', None

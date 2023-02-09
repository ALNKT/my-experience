from typing import Dict, Union, List

import requests

from database.CRUD import record_request, record_location_city, read_location_city_from_db
from database.models import RequestsRestaurants
from settings import SiteApiSettings, logger


def get_restaurants(data: Dict[str, Union[str, int, List[dict]]]) -> Union[Dict[str, Union[str, int, List[dict]]], str]:
    """
    Получаем из запроса по ресторанам необходимые нам данные

    :param data: данные
    :return: словарь с данными, если данные имеются, иначе строку
    """
    try:
        if len(data['data']) > 0:
            restaurants = {}
            location_city = [data['data'][0].get('ranking_geo_id'), data['data'][0].get('ranking_geo')]
            for i_restaurant in data['data']:
                if i_restaurant.get('name'):
                    tmp_restaurant = restaurants[i_restaurant.get('name')] = []
                else:
                    continue
                if not i_restaurant.get('is_closed'):
                    tmp_restaurant.append({'Открыто': 'Да'})
                else:
                    tmp_restaurant.append({'Открыто': 'Нет'})
                tmp_restaurant.append({'Рейтинг': i_restaurant.get('rating')})
                tmp_restaurant.append({'Кухня': i_restaurant.get('cuisine')})
                tmp_restaurant.append({'Расстояние': i_restaurant.get('distance_string')})
                tmp_restaurant.append({'Адрес': i_restaurant.get('address')})
                tmp_restaurant.append({'Телефон': i_restaurant.get('phone')})
                tmp_restaurant.append({'Фото':
                        i_restaurant.get('photo', dict()).get('images', dict()).get('medium', dict()).get('url')})
                tmp_restaurant.append({'Сайт': i_restaurant.get('web_url')})
                if i_restaurant.get('latitude') and i_restaurant.get('longitude'):
                    tmp_restaurant.append({'Координаты': (i_restaurant.get('latitude'), i_restaurant.get('longitude'))})
                else:
                    tmp_restaurant.append({'Координаты': None})

            return restaurants, location_city
        return 'Данные по запросу отсутствуют. Пожалуйста, попробуйте изменить параметры запроса.', None
    except KeyError:
        logger.exception('произошла ошибка при получении данных о ресторанах:')
        return 'Данные по запросу отсутствуют. Пожалуйста, попробуйте изменить параметры запроса.', None


def output_restaurants(restaurants):
    """
    Преобразуем данные по ресторанам в строковый тип и возвращаем данные по каждому ресторану
    :param restaurants: данные по ресторанам
    """
    data_of_all_restaurants = list()
    for i_restaurant, i_data in restaurants.items():
        coordinates = None
        if i_restaurant is not None:
            data_of_restaurant = f'Ресторан: {i_restaurant}\n'
        else:
            data_of_restaurant = f'Ресторан: Нет названия\n'
        for j_dict in i_data:
            data = {key: value for key, value in j_dict.items() if value is not None and len(value) > 0
                    and key != 'Координаты'}
            if j_dict.get('Кухня'):
                cuisine = [i_cuisine['name'] for i_cuisine in j_dict.get('Кухня')]
                data['Кухня'] = ', '.join(cuisine)
            if len(data) > 0:
                for key, value in data.items():
                    data_of_restaurant += f'{key}: {value}\n'
            if j_dict.get('Координаты'):
                coordinates = j_dict.get('Координаты')
        data_of_all_restaurants.append([data_of_restaurant, coordinates])
    return data_of_all_restaurants


X_RapidAPI_Key = SiteApiSettings().X_RapidAPI_Key.get_secret_value()
X_RapidAPI_Host = SiteApiSettings().X_RapidAPI_Host.get_secret_value()

headers = {
    "X-RapidAPI-Key": X_RapidAPI_Key,
    "X-RapidAPI-Host": X_RapidAPI_Host
}


def nearest_restaurants(user: str, coordinates: tuple, distance_search: int, count: int):
    """
    Поиск ресторанов по координатам (поблизости)

    :param user: данные пользователя
    :param coordinates: координаты пользователя
    :param distance_search: дистанция поиска (максимум 10 км)
    :param count: количество выдаваемых результатов (максимум 30)
    """
    url = "https://travel-advisor.p.rapidapi.com/restaurants/list-by-latlng"
    querystring = {"latitude": coordinates[0], "longitude": coordinates[1], "limit": count, "currency": "RUB",
                   "distance": distance_search, "open_now": "false", "lunit": "km", "lang": "ru_RU"}
    response = requests.request("GET", url, headers=headers, params=querystring)
    if response.status_code == 200:
        response = response.json()
        result_response, location_city = get_restaurants(response)
        if location_city is not None:
            record_location_city(location_city=location_city)
        if isinstance(result_response, str):
            record_request(user=user, request=result_response, table=RequestsRestaurants)
            yield result_response, None
        else:
            data_of_all_restaurants = output_restaurants(result_response)
            record_request(user=user, request=data_of_all_restaurants, table=RequestsRestaurants)
            for i_data in data_of_all_restaurants:
                data_of_restaurant, coordinates = i_data
                yield data_of_restaurant, coordinates
    else:
        err = 'Не удалось получить результаты, пожалуйста, повторите позднее.'
        record_request(user=user, request=err, table=RequestsRestaurants)
        yield err, None


def search_restaurants(user: str, city: str, count: int):
    """
    Поиск ресторанов по городу

    :param user: данные пользователя
    :param city: город
    :param count: количество выдаваемых результатов (максимум 30)
    :return:
    """
    location_id = read_location_city_from_db(city=city)
    if not location_id:
        url = "https://travel-advisor.p.rapidapi.com/locations/search"
        querystring = {"query": city, "limit": "1", "offset": "0", "units": "km", "location_id": "1",
                       "currency": "RUB", "sort": "relevance", "lang": "ru_RU"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        if response.status_code == 200:
            response = response.json()
            if response['data'][0]['result_type'] == 'geos':
                location_city = (response['data'][0]['result_object']['location_id'],
                                 response['data'][0]['result_object']['name'])
            else:
                location_city = (response['data'][0]['result_object']['ancestors'][0]['location_id'],
                                 response['data'][0]['result_object']['ancestors'][0]['name'])
            record_location_city(location_city=location_city)
            location_id = location_city[0]
        else:
            yield 'Не удалось получить результаты, пожалуйста, повторите позднее.', None
    url = "https://travel-advisor.p.rapidapi.com/restaurants/list"
    querystring = {"location_id": location_id, "restaurant_tagcategory": "10591",
                   "restaurant_tagcategory_standalone": "10591", "currency": "RUB", "lunit": "km", "limit": count,
                   "open_now": "false", "lang": "ru_RU"}
    response = requests.request("GET", url, headers=headers, params=querystring)
    if response.status_code == 200:
        response = response.json()
        result_response, location_city = get_restaurants(response)
        if isinstance(result_response, str):
            record_request(user=user, request=result_response, table=RequestsRestaurants)
            yield result_response, None
        else:
            data_of_all_restaurants = output_restaurants(result_response)
            record_request(user=user, request=data_of_all_restaurants, table=RequestsRestaurants)
            for i_data in data_of_all_restaurants:
                data_of_restaurant, coordinates = i_data
                yield data_of_restaurant, coordinates
    else:
        err = 'Не удалось получить результаты, пожалуйста, повторите позднее.'
        record_request(user=user, request=err, table=RequestsRestaurants)
        yield err, None

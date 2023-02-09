from typing import Dict, Union, List

import requests

from database.CRUD import record_location_city, record_request, read_location_city_from_db
from settings import SiteApiSettings, logger
from database.models import RequestsAttractions


X_RapidAPI_Key = SiteApiSettings().X_RapidAPI_Key.get_secret_value()
X_RapidAPI_Host = SiteApiSettings().X_RapidAPI_Host.get_secret_value()

headers = {
    "X-RapidAPI-Key": X_RapidAPI_Key,
    "X-RapidAPI-Host": X_RapidAPI_Host
}


def get_places(data: Dict[str, Union[str, int, List[dict]]]) -> Union[Dict[str, Union[str, int, List[dict]]], str]:
    """
    Получаем из запроса по местам необходимые нам данные

    :param data: данные
    :return: словарь с данными, если данные имеются, иначе строку
    """
    try:
        if len(data['data']) > 0:
            places = {}
            location_city = [data['data'][0].get('ranking_geo_id'), data['data'][0].get('ranking_geo')]
            for i_place in data['data']:
                if i_place.get('name'):
                    tmp_place = places[i_place.get('name')] = []
                else:
                    continue
                if i_place.get('subcategory'):
                    tmp_place.append({'Категория': i_place.get('subcategory')[0].get('name')})
                if not i_place.get('is_closed'):
                    tmp_place.append({'Открыто': 'Да'})
                else:
                    tmp_place.append({'Открыто': 'Нет'})
                tmp_place.append({'Рейтинг': i_place.get('rating')})
                tmp_place.append({'Описание': i_place.get('description')})
                tmp_place.append({'Расстояние': i_place.get('distance_string')})
                tmp_place.append({'Адрес': i_place.get('address')})
                tmp_place.append({'Телефон': i_place.get('phone')})
                tmp_place.append({'Фото':
                                i_place.get('photo', dict()).get('images', dict()).get('medium', dict()).get('url')})
                tmp_place.append({'Сайт': i_place.get('web_url')})
                if i_place.get('latitude') and i_place.get('longitude'):
                    tmp_place.append({'Координаты': (i_place.get('latitude'), i_place.get('longitude'))})
                else:
                    tmp_place.append({'Координаты': None})

            return places, location_city
        return 'Данные по запросу отсутствуют. Пожалуйста, попробуйте изменить параметры запроса.', None
    except KeyError:
        logger.exception('произошла ошибка при получении данных о достопримечательностях:')
        return 'Данные по запросу отсутствуют. Пожалуйста, попробуйте изменить параметры запроса.', None


def output_places(places):
    """
    Преобразуем данные по местам в строковый тип и возвращаем данные по каждому месту
    :param places: данные по местам
    """
    data_of_all_places = list()
    for i_place, i_data in places.items():
        coordinates = None
        if i_place is not None:
            data_of_place = f'Название: {i_place}\n'
        else:
            data_of_place = f'Название: Нет названия\n'
        for j_dict in i_data:
            data = {key: value for key, value in j_dict.items() if value is not None and len(value) > 0
                    and key != 'Координаты'}
            if len(data) > 0:
                for key, value in data.items():
                    data_of_place += f'{key}: {value}\n'
            if j_dict.get('Координаты'):
                coordinates = j_dict.get('Координаты')
        data_of_all_places.append([data_of_place, coordinates])
    return data_of_all_places


def nearest_places(user: List, coordinates: tuple, distance_search: int, count: int):
    """
    Поиск мест по координатам (поблизости)

    :param user: данные пользователя
    :param coordinates: координаты пользователя
    :param distance_search: дистанция поиска (максимум 10 км)
    :param count: количество выдаваемых результатов (максимум 30)
    """
    latitude, longitude = coordinates
    url = "https://travel-advisor.p.rapidapi.com/attractions/list-by-latlng"
    querystring = {"longitude": longitude, "latitude": latitude, "lunit": "km", "currency": "RUB", "limit": count,
                   "distance": distance_search, "lang": "ru_RU"}
    response = requests.request("GET", url, headers=headers, params=querystring)
    if response.status_code == 200:
        response = response.json()
        result_response, location_city = get_places(response)
        if location_city is not None:
            record_location_city(location_city=location_city)
        if isinstance(result_response, str):
            record_request(user=user, request=result_response, table=RequestsAttractions)
            yield result_response, None
        else:
            data_of_all_places = output_places(result_response)
            record_request(user=user, request=data_of_all_places, table=RequestsAttractions)
            for i_data in data_of_all_places:
                data_of_place, coordinates = i_data
                yield data_of_place, coordinates
    else:
        err = 'Не удалось получить результаты, пожалуйста, повторите позднее.'
        record_request(user=user, request=err, table=RequestsAttractions)
        yield err, None


def search_places(user: List, city: str, count: int):
    """
    Поиск мест по городу

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
    url = "https://travel-advisor.p.rapidapi.com/attractions/list"
    querystring = {"location_id": location_id, "currency": "RUB", "lang": "ru_RU", "lunit": "km", "limit": count,
                   "sort": "recommended"}
    response = requests.request("GET", url, headers=headers, params=querystring)
    if response.status_code == 200:
        response = response.json()
        result_response, location_city = get_places(response)
        if isinstance(result_response, str):
            record_request(user=user, request=result_response, table=RequestsAttractions)
            yield result_response, None
        else:
            data_of_all_restaurants = output_places(result_response)
            record_request(user=user, request=data_of_all_restaurants, table=RequestsAttractions)
            for i_data in data_of_all_restaurants:
                data_of_restaurant, coordinates = i_data
                yield data_of_restaurant, coordinates
    else:
        err = 'Не удалось получить результаты, пожалуйста, повторите позднее.'
        record_request(user=user, request=err, table=RequestsAttractions)
        yield err, None

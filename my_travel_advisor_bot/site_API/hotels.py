import json
from datetime import datetime
# from time import sleep

import requests

from database.CRUD import record_location_city, record_request, read_location_city_from_db
from settings import SiteApiSettings, logger
from database.models import RequestsHotels

X_RapidAPI_Key = SiteApiSettings().X_RapidAPI_Key.get_secret_value()
X_RapidAPI_Host = SiteApiSettings().X_RapidAPI_Host.get_secret_value()

headers = {
    "X-RapidAPI-Key": X_RapidAPI_Key,
    "X-RapidAPI-Host": X_RapidAPI_Host
}


def output_hotels(hotel):
    """
    Преобразуем данные по отелю в строковый тип и возвращаем данные по каждому месту
    :param hotel: данные по отелю
    :return: строковый тип данных по каждому отелю
    """
    data_of_hotel = ''
    coordinates = hotel.pop('Координаты отеля')
    for i_key, i_value in hotel.items():
        data_of_hotel += f'{i_key}: {i_value}\n'
    return data_of_hotel, coordinates


def nearest_hotels(user, data):
    """
    Поиск отелей поблизости
    :param user: данные пользователя
    :param data: данные отелей
    """
    my_coordinates = [str(data['coordinates']['latitude']), str(data['coordinates']['longitude'])]
    distance = data.pop('distance')
    adults, checkin, child_rm_ages, count, nights, price_max, price_min, rooms, stars = check_data(data)
    latitude, longitude = my_coordinates
    url = "https://travel-advisor.p.rapidapi.com/hotels/list-by-latlng"
    querystring = {"latitude": latitude, "longitude": longitude, "lang": "ru_RU", "hotel_class": stars,
                   "limit": count, "adults": adults, "rooms": rooms, "child_rm_ages": child_rm_ages,
                   "pricesmin": price_min, "pricesmax": price_max, "currency": "RUB", "checkin": checkin,
                   "nights": nights, "distance": distance}
    if not price_min:
        querystring.pop('pricesmin')
    elif not price_max:
        querystring.pop('pricesmax')
    elif not child_rm_ages:
        querystring.pop('child_rm_ages')
    data_of_all_hotels = list()
    coordinates = None
    response = requests.request("GET", url, headers=headers, params=querystring)
    if response.status_code == 200:
        response = response.json()
        # with open('all_hotels.json', 'w', encoding='utf-8') as file:  # запись в файл
        #     json.dump(response, file, indent=4, ensure_ascii=False)
        if len(response.get('data', [])) > 0:
            try:
                location_city = [response['data'][0].get('ranking_geo_id'), response['data'][0].get('ranking_geo')]
                record_location_city(location_city=location_city)
            except (IndexError, ValueError, TypeError):
                logger.exception('произошла ошибка при получении location_id при запросе отелей:')
            response = response.get('data')
            if response and len(response) > 0:
                location_id_hotels = [i_hotel.get('location_id') if i_hotel.get('name')
                                      else logger.info('произошла ошибка при получении отеля. '
                                                       'Отель отсутствует в общем списке отелей')
                                      for i_hotel in response]
                for i_hotel_details in get_details_of_hotels(location_id_hotels=location_id_hotels, checkin=checkin,
                                      adults=adults, child_rm_ages=child_rm_ages, nights=nights, rooms=rooms):
                    if not isinstance(i_hotel_details, str):
                        hotel_details, coordinates = output_hotels(hotel=i_hotel_details)
                        data_of_all_hotels.append([hotel_details, coordinates])
            record_request(user=user, request=data_of_all_hotels, table=RequestsHotels)
            for i_data in data_of_all_hotels:
                data_of_hotel, coordinates = i_data
                yield data_of_hotel, coordinates
        else:
            err = 'Не удалось получить результаты, пожалуйста, повторите позднее.'
            logger.exception(err)
            record_request(user=user, request=err, table=RequestsHotels)
            yield err, coordinates


def check_data(data):
    stars = ','.join(data.get('stars'))
    if data['price_level'] == 'price_range':
        price_min, price_max = data.get('prices')
    elif data['price_level'] == 'min_price':
        price_min, price_max = data.get('min_price'), 0
    else:
        price_min, price_max = 0, data.get('max_price')
    # price_min, price_max = float(price_min) // USD, float(price_max) // USD
    checkin = datetime.strptime(data.get('checkin'), '%d-%m-%Y').strftime('%Y-%m-%d')
    nights = data.get('nights')
    rooms = data.get('rooms')
    adults = data.get('adults')
    child_rm_ages = data.get('child_rm_ages')
    if child_rm_ages[0] != '0':
        child_rm_ages = ','.join(child_rm_ages)
    else:
        child_rm_ages = 0
    count = data.get('count_results')
    return adults, checkin, child_rm_ages, count, nights, price_max, price_min, rooms, stars


def search_hotels(user, data):
    """
    Поиск отелей в городе
    :param user: данные пользователя
    :param data: данные отелей
    """
    city = data.get('city_for_search')
    adults, checkin, child_rm_ages, count, nights, price_max, price_min, rooms, stars = check_data(data)
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

    url = "https://travel-advisor.p.rapidapi.com/hotels/list"
    querystring = {"location_id": location_id, "adults": adults, "rooms": rooms, "nights": nights, "checkin": checkin,
                   "pricesmax": price_max, "pricesmin": price_min, "hotel_class": stars, "currency": "RUB",
                   "child_rm_ages": child_rm_ages, "limit": count, "sort": "recommended", "lang": "ru_RU"}
    if not price_min:
        querystring.pop('pricesmin')
    elif not price_max:
        querystring.pop('pricesmax')
    elif not child_rm_ages:
        querystring.pop('child_rm_ages')
    print(querystring)
    data_of_all_hotels = list()
    response = requests.request("GET", url, headers=headers, params=querystring)
    if response.status_code == 200:
        response = response.json()
        with open('all_hotels.json', 'w', encoding='utf-8') as file:  # запись в файл
            json.dump(response, file, indent=4, ensure_ascii=False)
        yield from continue_search_hotels(adults, checkin, child_rm_ages, data_of_all_hotels, nights, response, rooms,
                                          user)


def continue_search_hotels(adults, checkin, child_rm_ages, data_of_all_hotels, nights, response, rooms, user):
    """
    При наличии всех данных об отелях, продолжаем поиск отелей в городе
    :param adults: кол-во людей
    :param checkin: дата заезда
    :param child_rm_ages: возраст детей
    :param data_of_all_hotels: данные обо всех отелей
    :param nights: кол-во ночей
    :param response: ответ от сервера
    :param rooms: кол-во номеров
    :param user: данные пользователя
    """
    if len(response.get('data', [])) > 0:
        response = response.get('data')
        if response and len(response) > 0:
            location_id_hotels = [i_hotel.get('location_id') if i_hotel.get('name')
                                  else logger.info('произошла ошибка при получении отеля. '
                                                   'Отель отсутствует в общем списке отелей')
                                  for i_hotel in response]
            for i_hotel_details in get_details_of_hotels(location_id_hotels=location_id_hotels, checkin=checkin,
                                                         adults=adults, child_rm_ages=child_rm_ages, nights=nights,
                                                         rooms=rooms):
                if not isinstance(i_hotel_details, str):
                    hotel_details, coordinates = output_hotels(hotel=i_hotel_details)
                    data_of_all_hotels.append([hotel_details, coordinates])
        record_request(user=user, request=data_of_all_hotels, table=RequestsHotels)
        for i_data in data_of_all_hotels:
            data_of_hotel, coordinates = i_data
            yield data_of_hotel, coordinates
    else:
        err = 'Не удалось получить результаты, пожалуйста, повторите позднее.'
        logger.exception(err)
        record_request(user=user, request=err, table=RequestsHotels)
        yield err, None


def get_details_of_hotels(location_id_hotels, checkin, adults, child_rm_ages, nights, rooms):
    """
    Получаем детали об отеле
    :return: данные по отелю
    """
    location_id_hotel = None
    hotel_details = dict()

    url = "https://travel-advisor.p.rapidapi.com/hotels/get-details"
    querystring = {"location_id": location_id_hotel, "checkin": checkin, "adults": adults, "lang": "ru_RU",
                   "child_rm_ages": child_rm_ages, "currency": "RUB", "nights": nights, "rooms": rooms}
    if not child_rm_ages:
        querystring.pop('child_rm_ages')
    for i_location_id_hotel in location_id_hotels:
        querystring.update({"location_id": i_location_id_hotel})
        # sleep(2)
        response = requests.request("GET", url, headers=headers, params=querystring)
        if response.status_code == 200:
            response = response.json()
            with open('hotel_details.json', 'a', encoding='utf-8') as f:  # запись в файл
                json.dump(response, f, indent=4, ensure_ascii=False)
            try:
                data = response.get('data')[0]
                if data and len(data) > 0:
                    hotel_details['Название отеля'] = data['name']
                    coordinates = [data.get('latitude'), data.get('longitude')]
                    hotel_details['Координаты отеля'] = coordinates
                    hotel_details['Количество звёзд'] = data.get('hotel_class')
                    hotel_details['Диапазон цен'] = data.get('price')
                    hotel_details['Адрес'] = data.get('address')
                    hotel_details['Телефон'] = data.get('phone', 'не указан')
                    hotel_details['E-mail'] = data.get('email', 'не указан')
                    hotel_details['Фото'] = data.get('photo', dict()).get('images', dict()).get('medium', dict()).get('url')
                    hotel_details['Сайт'] = data.get('web_url')
                else:
                    raise KeyError
            except (KeyError, IndexError):
                logger.exception('произошла ошибка при получении данных о конкретном отеле:')
                yield 'Данные по запросу отсутствуют. Пожалуйста, попробуйте изменить параметры запроса.'
            else:
                yield hotel_details

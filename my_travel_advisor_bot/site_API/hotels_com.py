import requests


def search_hotels(user, data):
    """
    Поиск отелей в городе
    :param user: данные пользователя
    :param data: данные отелей
    """
    city = data.get('city_for_search')
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"

    querystring = {"query": city, "locale": "ru_RU", "currency": "RUB"}

    headers = {
        "X-RapidAPI-Key": "13746d9c57msh07f4156bc0d6eaep1416bfjsnddd9395d6eba",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    if response.status_code == 200:
        response = response.json()
        data = response.get('suggestions')
        if data:
            destinationId = data[0].get('entities')[0].get('destinationId')

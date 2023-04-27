import json
import logging

import requests


class Hotels:
    def __init__(self, name):
        self.name = name
        self.price_string = None
        self.price_digit = None


def search_coordinates(country, town):
    coordinates = {}

    url = "https://hotels4.p.rapidapi.com/locations/v3/search"

    querystring = {"q": town, "locale": "en_US", "langid": "1033", "siteid": "300000001"}

    headers = {
        "X-RapidAPI-Key": "2f334e1821msh731ec8077f8ff4ep11950bjsn07c78c7458dc",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    response_json = json.loads(response.text)

    if response.status_code != 200:
        return True, coordinates

    for item in response_json['sr']:

        if 'name' not in item['hierarchyInfo']['country'].keys():
            continue

        if country == item['hierarchyInfo']['country']['name']:
            coordinates = {"latitude": float(item['coordinates']['lat']),
                           "longitude": float(item['coordinates']['long'])}
            break
        else:
            continue

    return False, coordinates


def search_hotels(coordinates, search_params):
    hotels_result = []

    url = "https://hotels4.p.rapidapi.com/properties/v2/list"

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "destination": {"coordinates": coordinates},
        "checkInDate": {
            "day": 10,
            "month": 10,
            "year": 2023
        },
        "checkOutDate": {
            "day": 15,
            "month": 10,
            "year": 2023
        },
        "rooms": [
            {
                "adults": 2,
                "children": [{"age": 5}, {"age": 7}]
            }
        ],
        "resultsStartingIndex": 0,
        "sort": "PRICE_LOW_TO_HIGH",
        "filters": {"price": {
            "max": search_params.cost_max,
            "min": search_params.cost_min
        }}
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "2f334e1821msh731ec8077f8ff4ep11950bjsn07c78c7458dc",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    response_json = json.loads(response.text)

    if response.status_code != 200:
        return True, hotels_result

    hotels_count = 0
    hotels = []

    for item in response_json['data']['propertySearch']['properties']:
        hotel = Hotels(item['name'])
        hotel.price_string = item['price']['lead']['formatted']
        hotel.price_digit = item['price']['lead']['amount']
        hotel.id = item['id']
        hotels.append(hotel)
        hotels_count += 1

    hotels = sorted(hotels, key=lambda d: d.price_digit, reverse=search_params.sort_revers)

    hotels_result = []
    hotels_count = 0

    for item in hotels:
        if hotels_count == int(search_params.count):
            break
        else:
            hotels_result.append(item)
            hotels_count += 1

    return False, hotels_result


def info_hotels(id_hotel, search_params):
    search_params.count_photo = int(search_params.count_photo)

    url = "https://hotels4.p.rapidapi.com/properties/v2/get-summary"

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "propertyId": id_hotel
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "2f334e1821msh731ec8077f8ff4ep11950bjsn07c78c7458dc",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    response_json = json.loads(response.text)

    address_photo_map = []
    address = (response_json['data']["propertyInfo"]['summary']['location']['address']['addressLine'])
    address_photo_map.append(address)

    images_group = []

    if search_params.count_photo != 0:
        for item in range(search_params.count_photo):
            image = response_json['data']["propertyInfo"]['propertyGallery']["images"][item]["image"]['url']
            images_group.append(image)

        address_photo_map.append(images_group)

    map_photo = response_json['data']["propertyInfo"]['summary']['location']["staticImage"]['url']
    address_photo_map.append(map_photo)
    return address_photo_map

import json

import requests


class Hotels:
    def __init__(self, name):
        self.name = name
        self.price = None
        self.photo = None


def search_region_id(town, country):
    url = "https://hotels4.p.rapidapi.com/locations/v3/search"

    querystring = {"q": town, "locale": "en_US", "langid": "1033", "siteid": "300000001"}

    headers = {
        "X-RapidAPI-Key": "ae48e3ae60mshe749d9f78159725p1f5710jsn177113c4f210",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    response_json = json.loads(response.text)


    two_list = []
    for item in response_json['sr']:

        if country in item["regionNames"]["fullName"]:
            coordinate_1 = item['coordinates']['lat']
            two_list.append(coordinate_1)
            coordinate_2 = item['coordinates']['long']
            two_list.append(coordinate_2)
            break

        elif country == item['hierarchyInfo']['country']['name']:
            coordinate_1 = item['coordinates']['lat']
            two_list.append(coordinate_1)
            coordinate_2 = item['coordinates']['long']
            two_list.append(coordinate_2)
            break

        # if country in item["regionNames"]["fullName"]:
        #     coordinate_1 = item['coordinates']['lat']
        #     two_list.append(coordinate_1)
        #     coordinate_2 = item['coordinates']['long']
        #     two_list.append(coordinate_2)
        #     break
        else:
            continue

    return two_list


def search_hotels(coordinate_1, coordinate_2, search_params):
    coordinate_1 = float(coordinate_1)
    coordinate_2 = float(coordinate_2)



    url = "https://hotels4.p.rapidapi.com/properties/v2/list"

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "destination": {"coordinates": {"latitude": coordinate_1, "longitude": coordinate_2}},
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
        "resultsSize": search_params.count,
        "sort": "PRICE_LOW_TO_HIGH",
        "filters": {"price": {
            "max": 1000,
            "min": 100
        }}
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "ae48e3ae60mshe749d9f78159725p1f5710jsn177113c4f210",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    response_json = json.loads(response.text)

    hotels = []
    hotels_count = 0

    for item in response_json['data']['propertySearch']['properties']:
        if hotels_count == int(search_params.count):
            break
        else:
            hotel = Hotels(item['name'])
            hotel.price = item['price']['lead']['formatted']
            hotel.photo = item['propertyImage']['image']['url']
            hotels.append(hotel)
            hotels_count += 1

    return hotels

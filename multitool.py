from pprint import pprint
import requests
import sys
import pygame
from PIL import Image
from io import BytesIO
from hashlib import md5 as _md
import json


def no_color(string):
    res = ''
    fill = True
    for i in string:
        if fill and i == '\x1b':
            fill = False
            continue
        if not fill and i == 'm':
            fill = True
            continue
        res += i
    return res


ERROR_STRING = '\x1b[31;1mError\x1b[0m \x1b[1m(\x1b[36;1m%s\x1b[1m): \x1b[4;1m%s\x1b[0m'
if 'win' in sys.platform:
    try:
        import colorama
        colorama.init()
    except ImportError:
        ERROR_STRING = no_color(ERROR_STRING)


URLS = {
    "geocode": "http://geocode-maps.yandex.ru/1.x/",
    "static": "https://static-maps.yandex.ru/1.x/",
    "search": "https://search-maps.yandex.ru/v1/"
}

GEOCODE = 'geocode'
STATIC = 'static'
SEARCH = 'search'
API_KEY = open('api_key', 'r').read()
SIZE = 600, 450


def md5(string):
    return str(_md(str(string).encode('utf-8')).hexdigest())


def get_coord(location, sco='longlat'):
    params = {
        "geocode": location,
        "sco": sco
    }
    response = get_request(GEOCODE, params)
    if response:
        res = response.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
        return tuple(map(float, res.split()))


def search_spn(geo_object):
    if type(geo_object) is not dict:
        geo_object = get_geo_object(*geo_object)
    data = geo_object["boundedBy"]["Envelope"]
    upper = tuple(map(float, data["upperCorner"].split()))
    lower = tuple(map(float, data["lowerCorner"].split()))
    return upper[0] - lower[0], upper[1] - lower[1]


def convert_bytes(bytes_string):
    im = Image.open(BytesIO(bytes_string)).convert("RGBA")
    return pygame.image.fromstring(im.tobytes(), im.size, im.mode)


def get_request(url, params=None, **kwargs):
    try:
        if url in URLS:
            if url == SEARCH:
                if params is None:
                    url += "&apikey=" + API_KEY + "&lang=ru_RU"
                else:
                    params['apikey'] = API_KEY
                    params['lang'] = 'ru_RU'

            if url == GEOCODE:
                if params is None:
                    url += "&format=json"
                else:
                    params['format'] = 'json'

            url = URLS[url]
        res = requests.get(url, params=params, **kwargs)
        if not res:
            print(ERROR_STRING % (res.status_code, res.reason), "\n\nURL:", res.url)
            sys.exit(res.status_code)
        else:
            return res
    except Exception as err:
        print(ERROR_STRING % (type(err).__name__, err))
        sys.exit(1)


def get_geo_object(locate):
    params = {
        "geocode": str_param(locate)
    }

    res = get_request(GEOCODE, params).json()
    geo_object = res["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    return geo_object


def str_param(*params):
    return ','.join(map(str, params))


def get_address(coords, postal_code=False):
    geo_object = get_geo_object(coords)["metaDataProperty"]["GeocoderMetaData"]  # type: dict
    json.dump(geo_object, open('geo.json', 'w'), ensure_ascii=False, indent=2)
    address = geo_object["text"]
    if postal_code and get_postal_code(coords):
        address += ", " + geo_object["Address"]['postal_code']
    return address


def get_postal_code(coords):
    geo_object = get_geo_object(coords)["metaDataProperty"]["GeocoderMetaData"]  # type: dict
    return geo_object.get("Address", {'postal_code': None}).get('postal_code', None)


def create_point(long, lat, style='pm2', color='wt', size='m', content=''):
    """
    https://tech.yandex.ru/maps/doc/staticapi/1.x/dg/concepts/markers-docpage/
    :return: point data
    """
    return str_param(long, lat, ''.join((style, color, size, content)))

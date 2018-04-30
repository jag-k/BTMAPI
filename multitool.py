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
SIZE_RECT = pygame.Rect((0, 0), SIZE)


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
        res = requests.get(url, params=params)
        if not res:
            print(ERROR_STRING % (res.status_code, res.reason), "\n\nURL:", res.url)
            sys.exit(res.status_code)
        else:
            return res
    except Exception as err:
        print(ERROR_STRING % (type(err).__name__, err))
        sys.exit(1)


def get_geo_object(locate):
    locate = locate if type(locate) in [tuple, list] else [locate]
    params = {
        "geocode": str_param(*locate)
    }

    res = get_request(GEOCODE, params).json()
    geo_object = res["response"]["GeoObjectCollection"]["featureMember"]
    return geo_object[0]["GeoObject"] if len(geo_object) > 0 else {}


def str_param(*params):
    return ','.join(map(str, params))


def get_address(coords, postal_code=False):
    try:
        geo_object = get_geo_object(coords)["metaDataProperty"]["GeocoderMetaData"]  # type: dict
        json.dump(geo_object, open('geo.json', 'w'), ensure_ascii=False, indent=2)
        address = geo_object["text"]
        if postal_code and get_postal_code(coords):
            address += ", " + geo_object["Address"]['postal_code']
    except KeyError:
        return "Error"
    return address


def get_postal_code(coords):
    geo_object = get_geo_object(coords)["metaDataProperty"]["GeocoderMetaData"]  # type: dict
    return geo_object.get("Address", {'postal_code': None}).get('postal_code', None)


# POINTS #
points = []


class Point:
    def __init__(self, long, lat, style='pm2', color='wt', size='m', content=''):
        """
        https://tech.yandex.ru/maps/doc/staticapi/1.x/dg/concepts/markers-docpage/
        :return: point data
        """
        self.pos = long, lat
        self.style = style
        self.color = color
        self.size = size
        self.content = content

    def __str__(self):
        return str_param(str_param(*self.pos), ''.join(filter(lambda x: x,
                                                              (self.style, self.color, self.size, self.content))))


def create_point(long, lat, style='pm2', color='wt', size='m', content=''):
    p = Point(long, lat, style, color, size, content)
    if len(points) <= 100:
        points.append(p)
        return p


def render_points():
    return '~'.join([str(points[i]) + (str(i + 1) if i < 99 else '') for i in range(len(points))])


if __name__ == '__main__':
    params = {
        "geocode": str_param(45.0200828, 53.12381011515711)
    }

    res = get_request(GEOCODE, params).json()
    geo_object = res["response"]["GeoObjectCollection"]["featureMember"]
    pprint(geo_object)

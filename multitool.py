import requests
import sys
import pygame
from PIL import Image
from io import BytesIO

if 'win' in sys.platform:
    try:
        import colorama
        colorama.init()
        ERROR_STRING = '\x1b[31;1mError\x1b[0;1m (\x1b[36;1m%s\x1b[1m): \x1b[4;1m%s\x1b[0m'
    except ImportError:
        ERROR_STRING = 'Error (%s): %s'
else:
    ERROR_STRING = '\x1b[31;1mError\x1b[0;1m (\x1b[36;1m%s\x1b[1m): \x1b[4;1m%s\x1b[0m'


URLS = {
    "geocode": "http://geocode-maps.yandex.ru/1.x/",
    "static": "https://static-maps.yandex.ru/1.x/",
    "search": "https://search-maps.yandex.ru/v1/"
}

GEOCODE = 'geocode'
STATIC = 'static'
SEARCH = 'search'
API_KEY = open('api_key').read()


def search_spn(geo_object):
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
                    url += "&apikey=" + API_KEY
                else:
                    params['apikey'] = API_KEY

            if url == GEOCODE:
                if params is None:
                    url += "&format=json" + API_KEY
                else:
                    params['format'] = 'json'

            url = URLS[url]
        res = requests.get(url, params=params, **kwargs)
        if not res:
            print(ERROR_STRING % (res.status_code, res.reason))
            sys.exit(res.status_code)
        else:
            return res
    except Exception as err:
        print(ERROR_STRING % (type(err).__name__, err))
        sys.exit(1)

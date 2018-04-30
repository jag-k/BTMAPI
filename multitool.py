from pprint import pprint
import requests
import sys
from io import BytesIO
from hashlib import md5 as _md
import json
from GUI import *

clock = pygame.time.Clock()
FPS = 60


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

RADIUS = 50 / 111144


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


def geo_search(coord):
    params = {
        "text": str_param(*coord),
        "ll": str_param(*coord),
        "spn": str_param(RADIUS, RADIUS),
        "type": "biz",
        "rspn": 1
    }
    return get_request(SEARCH, params).json()['features']


def screen_biz(coord, screen: pygame.Surface):
    res = "Организация: %s\n\n" \
          "Сайт: %s\n" \
          "Адресс: %s\n" \
          "Телефон(ы): %s\n" \
          "Почтовый Адресс: %s\n" \
          "Категории: %s"

    t = geo_search(coord)
    if not t:
        return

    biz = t[0]  # type: dict
    json.dump(biz, open("biz.json", "w"), indent=2, ensure_ascii=False)
    company = biz['properties']['CompanyMetaData']  # type: dict
    name = company['name']  # type: str

    postal_code = company.get('postalCode', 'Не найден')
    address = company.get('address', 'Адресс не найден')
    url = company.get('url', 'Сайт не найден')

    hour = company.get('Hours', {}).get("text", "")
    name += " (%s)" % hour if hour else ''

    categories = ', '.join(map(lambda x: x['name'], company.get('Categories', [])))
    categories = categories if categories else "Без категорий"

    phones = ', '.join(map(lambda x: x['formatted'], company.get('Phones', [])))
    phones = phones if phones else "Телефоны не найдены"

    res = res % (name, url, address, phones, postal_code, categories)

    bg = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    bg.fill(to_color("#FFFFFF99"))
    screen.blit(bg, (0, 0))
    rect = screen.get_rect()  # type: pygame.Rect
    rect.topleft = 5, 5
    rect.bottom -= 5
    rect.right -= 5
    l = Label(rect, res, "gray25", auto_line_break=True)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
                return True

        l.render(screen)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    res = geo_search((45.0200828, 53.12381011515711))
    json.dump(geo_search((45.0200828, 53.12381011515711)), open('test.json', 'w'), ensure_ascii=False, indent=2)
    json.dump(geo_search((37.764662, 55.719081)), open('test2.json', 'w'), ensure_ascii=False, indent=2)

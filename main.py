import requests
from multitool import pygame, search_spn, convert_bytes
import sys

ERROR_STRING = '\x1b[31;1mError\x1b[1m (\x1b[36;1m%s\x1b[1m): \x1b[4;1m%s\x1b[0m'
FPS = 60
size = 600, 450
spn = 0, 0
max_spn = 0, 0
SPN_STEP = 0.001

locate = "Красная площадь, 1"


def get_coord(location, sco='longlat'):
    url = "http://geocode-maps.yandex.ru/1.x/?geocode=%s&format=json&sco=%s" % (location, sco)
    response = requests.get(url)
    if response:
        res = response.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
        return tuple(map(float, res.split()))


def get_request(url, params=None, **kwargs):
    try:
        res = requests.get(url, params=params, **kwargs)
        if not res:
            print(ERROR_STRING % (res.status_code, res.reason))
            sys.exit(res.status_code)
        else:
            return res
    except Exception as err:
        print(ERROR_STRING % (type(err).__name__, err))
        sys.exit(1)


def str_param(*params):
    return ','.join(map(str, params))


def map_image(long, lat, l=['sat', 'skl']):
    url = 'https://static-maps.yandex.ru/1.x/'

    params = {
        "ll": str_param(long, lat),
        "l": ','.join(l),
        "size": str_param(*size),
        "spn": str_param(*spn)
    }

    res = get_request(url, params)

    return convert_bytes(res.content)


def get_geo_object(long, lat):
    url = 'https://geocode-maps.yandex.ru/1.x/'
    
    params = {
        "geocode": str_param(long, lat),
        "format": "json"
    }
    
    res = get_request(url, params).json()
    geo_object = res["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    return geo_object


def sum_spn(spn, s1, s2=None):
    if s2 is None:
        s2 = s1
    spn = list(spn)
    spn[0] += s1
    spn[1] += s2
    return tuple(spn)


coords = get_coord(locate)
image = map_image(*coords)

pygame.init()
clock = pygame.time.Clock()
surface = pygame.display.set_mode(size)
surface.blit(image, (0, 0))

running = True
max_spn = search_spn(get_geo_object(*coords))
print(max_spn)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PAGEUP:
                if sum_spn(spn, SPN_STEP) <= max_spn:
                    spn = sum_spn(spn, SPN_STEP)
            if event.key == pygame.K_PAGEDOWN:
                if sum_spn(spn, -SPN_STEP) >= (0, 0):
                    spn = sum_spn(spn, -SPN_STEP)                
    
    image = map_image(*coords)
    
    surface.blit(image, (0, 0))    

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()

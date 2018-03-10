from multitool import *

FPS = 60
size = 600, 450
spn = 0, 0
max_spn = 0, 0
SPN_STEP = 0.5

# locate = "Красная площадь, 1"
locate = "Россия"


def get_coord(location, sco='longlat'):
    params = {
        "geocode": location,
        "sco": sco
    }
    response = get_request(GEOCODE, params)
    if response:
        res = response.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
        return tuple(map(float, res.split()))


def str_param(*params):
    return ','.join(map(str, params))


def map_image(long, lat, l=['sat', 'skl']):
    params = {
        "ll": str_param(long, lat),
        "l": ','.join(l),
        "size": str_param(*size),
        "spn": str_param(*spn)
    }

    res = get_request(STATIC, params)

    return convert_bytes(res.content)


def get_geo_object(long, lat):
    params = {
        "geocode": str_param(long, lat)
    }
    
    res = get_request(GEOCODE, params).json()
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
pygame.display.set_icon(image)
pygame.display.set_caption(locate, locate)
surface = pygame.display.set_mode(size)
surface.blit(image, (0, 0))
pygame.display.flip()


running = True
max_spn = search_spn(get_geo_object(*coords))
print(max_spn)
spn = max_spn

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if event.type == pygame.KEYDOWN:
            print(event)
            if event.key == pygame.K_PAGEUP or event.key == pygame.K_KP9 and event.mod == 4096:
                if sum_spn(spn, SPN_STEP) <= max_spn:
                    spn = sum_spn(spn, SPN_STEP)
                    print(spn)
            if event.key == pygame.K_PAGEDOWN or event.key == pygame.K_KP3 and event.mod == 4096:
                if sum_spn(spn, -SPN_STEP) >= (0, 0):
                    spn = sum_spn(spn, -SPN_STEP)
                    print(spn)
    
    image = map_image(*coords)
    
    surface.blit(image, (0, 0))    

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()

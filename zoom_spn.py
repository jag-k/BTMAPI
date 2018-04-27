from multitool import *
import math

SPN_VALUES = [0.002, 0.005, 0.01, 0.02, 0.03, 0.1, 0.2, 0.5, 1, 2, 3, 6, 12, 24, 35]
ZOOM_VALUES = dict((SPN_VALUES[i], 17 - i) for i in range(len(SPN_VALUES)))


def get_nearby(value, iter):
    return min(iter, key=lambda x: math.fabs(int(x) - int(value)))


def search_spn(geo_object):
    if type(geo_object) is not dict:
        geo_object = get_geo_object(*geo_object)
    data = geo_object["boundedBy"]["Envelope"]
    upper = tuple(map(float, data["upperCorner"].split()))
    lower = tuple(map(float, data["lowerCorner"].split()))
    return get_nearby(upper[0] - lower[0], SPN_VALUES), get_nearby(upper[1] - lower[1], SPN_VALUES)


def get_zoom(spn):
    return ZOOM_VALUES.get(max(map(lambda x: get_nearby(x, SPN_VALUES), spn), key=lambda x: ZOOM_VALUES.get(x)), 0)


def screen_to_geo(pos, coords, spn):
    coord_to_geo_x, coord_to_geo_y = 0.0000428, 0.0000428
    z = get_zoom(spn)
    const_y, const_x = 225, 300

    dy = const_y - pos[1]
    dx = pos[0] - const_x
    lon, lat = coords

    # if z < 13 and z != 3:
    #     coord_to_geo_x, coord_to_geo_y = 0.0000856, 0.0000860

    return lon + dx * coord_to_geo_x * math.pow(2, 15 - z), \
           lat + dy * coord_to_geo_y * math.cos(math.radians(lat)) * math.pow(2, 15 - z)

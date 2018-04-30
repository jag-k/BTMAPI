from multitool import *
import math

SPN_VALUES = sorted([0.002, 0.005, 0.01, 0.02, 0.03, 0.1, 0.2, 0.5, 1, 2, 3, 6, 12, 24, 35, 37])
ZOOM_VALUES = dict((SPN_VALUES[i], 17 - i) for i in range(len(SPN_VALUES)))

GEO_X, GEO_Y = 0.0000428, 0.0000428


def screen_to_geo(pos, coords, z):
    lon, lat = coords
    return lon + (pos[0] - 300) * GEO_X * math.pow(2, 15 - z), \
           lat + (225 - pos[1]) * GEO_Y * math.cos(math.radians(lat)) * math.pow(2, 15 - z)


def get_nearby_spn(spn):
    if type(spn) not in (float, int):
        spn = max(spn)
    return min(SPN_VALUES, key=lambda x: math.fabs(x - spn))


def search_z(geo_object):
    if type(geo_object) is not dict:
        geo_object = get_geo_object(*geo_object)
    data = geo_object["boundedBy"]["Envelope"]
    upper = tuple(map(float, data["upperCorner"].split()))
    lower = tuple(map(float, data["lowerCorner"].split()))
    return get_zoom((get_nearby_spn(upper[0] - lower[0]), get_nearby_spn(upper[1] - lower[1])))


def get_zoom(spn):
    return ZOOM_VALUES.get(max(map(get_nearby_spn, spn), key=lambda x: ZOOM_VALUES.get(x)), 0)

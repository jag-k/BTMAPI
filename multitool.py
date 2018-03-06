import pygame
from PIL import Image
from io import BytesIO


def search_spn(geo_object):
    data = geo_object["boundedBy"]["Envelope"]
    upper = tuple(map(float, data["upperCorner"].split()))
    lower = tuple(map(float, data["lowerCorner"].split()))
    return upper[0] - lower[0], upper[1] - lower[1]


def convert_bytes(bytes_string):
    im = Image.open(BytesIO(bytes_string)).convert("RGBA")
    return pygame.image.fromstring(im.tobytes(), im.size, im.mode)

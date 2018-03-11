from GUI import GUI, Button, TextBox
from multitool import *

FPS = 60
next_spn = None
locate = "Красная площадь, 1"
# locate = "Австралия"
# locate = input("Enter locate: ")
# SPN_STEP = float(input("Enter the zoom-ratio: "))
SPN_STEP = 0.01
l_mode = 'гибрид'
L_DICT = {
    "гибрид": ['sat', 'skl'],
    "спутник": ['sat'],
    "схема": ['map'],
}


def map_image(long, lat, l=['sat', 'skl']):
    params = {
        "ll": str_param(long, lat),
        "l": ','.join(l),
        "size": str_param(*SIZE),
        "spn": str_param(*spn)
    }

    return convert_bytes(get_request(STATIC, params).content)


def sum_spn(spn, s1, s2=None):
    if s2 is None:
        s2 = s1
    spn = list(spn)
    spn[0] += s1
    spn[1] += s2
    return tuple(spn)


coords = get_coord(locate)
# print(spn)
spn = max_spn = search_spn(get_geo_object(*coords))
# print(max_spn)
image = map_image(*coords, L_DICT[l_mode])

pygame.init()
clock = pygame.time.Clock()
pygame.display.set_icon(image)
pygame.display.set_caption(locate, locate)
screen = pygame.display.set_mode(SIZE)
screen.blit(image, (0, 0))
pygame.display.flip()


gui = GUI()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PAGEUP or (event.key == pygame.K_KP9 and event.mod == 4096):
                new_spn = sum_spn(spn, SPN_STEP)
                if new_spn[0] <= max_spn[0] and new_spn[1] <= max_spn[0]:
                    next_spn = new_spn

            if event.key == pygame.K_PAGEDOWN or (event.key == pygame.K_KP3 and event.mod == 4096):
                new_spn = sum_spn(spn, -SPN_STEP)
                if new_spn[0] >= 0 and new_spn[1] >= 0:
                    next_spn = new_spn
                # print(next_spn)
        gui.get_event(event)

    if next_spn != spn and next_spn is not None:
        spn = next_spn
        image = map_image(*coords)
        screen.blit(image, (0, 0))

    gui.update()
    gui.render(screen)
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()

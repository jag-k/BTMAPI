from GUI import GUI, Button, TextBox
from multitool import *

FPS = 60
next_spn = None
locate = "Красная площадь, 1"
# locate = "Австралия"
# locate = input("Enter locate: ")
# SPN_STEP = float(input("Enter the zoom-ratio: "))
SPN_STEP = 0.003
l_mode = 'схема'
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
    print(params)

    return convert_bytes(get_request(STATIC, params).content)


def sum_spn(spn, s1, s2=None):
    if s2 is None:
        s2 = s1
    spn = list(spn)
    spn[0] += s1
    spn[1] += s2
    return tuple(spn)
    
def view_maps(num):
    # отрисовка карты
    if num < 3:
        image = map_image(*coords, L_DICT[maps[num]])
    else:
        num %= 3
        image = map_image(*coords, L_DICT[maps[num % 3]])
    screen.blit(image, (0, 0))  
    return num

coords = get_coord(locate)
# print(spn)
spn = max_spn = search_spn(get_geo_object(*coords))
# print(max_spn)
# вид карт
maps = ["схема", "спутник", "гибрид"]
n_maps = 0
# отрисовка карты по значению n_maps
image = map_image(*coords, L_DICT[maps[n_maps]])

pygame.init()
clock = pygame.time.Clock()
pygame.display.set_icon(image)
pygame.display.set_caption(locate, locate)
screen = pygame.display.set_mode(SIZE)
screen.blit(image, (0, 0))
pygame.display.flip()

gui = GUI()
running = True
g = Button((0, 0, 100, 30), maps[n_maps])
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

        if g.get_event(event):
            # количество нажатий
            n_maps += 1
            n_maps = view_maps(n_maps)
            # отрисовка новой кнопки
            g = Button((0, 0, 100, 30), maps[n_maps])
        

    if next_spn != spn and next_spn is not None:
        spn = next_spn
        image = map_image(*coords, L_DICT[maps[n_maps]])
        screen.blit(image, (0, 0))

    g.render(screen)
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()

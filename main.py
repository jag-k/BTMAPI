from GUI import GUI, Button, TextBox, to_color
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
    "Гибрид": ['sat', 'skl'],
    "Спутник": ['sat'],
    "Схема": ['map'],
}
KEY_CONTROL = {
    "up": [0, SPN_STEP],
    "down": [0, -SPN_STEP],
    "right": [SPN_STEP, 0],
    "left": [-SPN_STEP, 0],
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


def view_maps(num):
    # отрисовка карты
    if num < 3:
        image = map_image(coords[0], coords[1], L_DICT[maps[num]])
    else:
        num %= 3
        image = map_image(coords[0], coords[1], L_DICT[maps[num % 3]])
    screen.blit(image, (0, 0))
    return num


coords = get_coord(locate)
# print(spn)
spn = max_spn = search_spn(get_geo_object(coords[0], coords[1]))
# print(max_spn)
# вид карт
maps = ["Схема", "Спутник", "Гибрид"]
START_TYPE = 0
new_locate = False
image = map_image(coords[0], coords[1], L_DICT[maps[START_TYPE]])

pygame.init()
clock = pygame.time.Clock()
pygame.display.set_icon(image)
pygame.display.set_caption(locate, locate)
screen = pygame.display.set_mode(SIZE)
screen.blit(image, (0, 0))
pygame.display.flip()

gui = GUI()


# GUI ELEMENTS

def type_button_click(button: Button):
    button.text = maps[(maps.index(button.text) + 1) % 3]


def search_textbox_event(textbox: TextBox):
    global locate
    global coords
    global new_locate
    locate = textbox.text
    coords = get_coord(locate)
    new_locate = True


bg_color = to_color((240, 189, 0))
active_color = to_color((255, 204, 0))

search_textbox = TextBox((5, 5, 250, 35), locate, execute=search_textbox_event, placeholder="Поиск…",
                         bg_color=(255, 255, 255, 150))
search_button = Button((5, 50, 100, 35), 'Поиск', 'black', bg_color, active_color,
                       click_event=lambda x: search_textbox_event(search_textbox))

type_button_rect = pygame.Rect(0, 0, 100, 35)
type_button_rect.bottomright = (SIZE[0]-5, SIZE[1]-5)

type_button = Button(type_button_rect, maps[START_TYPE], 'black', bg_color, active_color,
                     click_event=type_button_click)
old_type = maps[START_TYPE]


gui = GUI(search_button, type_button, search_textbox)
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
            if pygame.key.name(event.key) in KEY_CONTROL and not search_textbox.focus:
                coords = sum_spn(coords, *KEY_CONTROL[pygame.key.name(event.key)])
                new_locate = True

        gui.get_event(event)

    if next_spn != spn and next_spn is not None or old_type != type_button.text or new_locate:
        spn = next_spn if next_spn is not None else spn
        image = map_image(coords[0], coords[1], L_DICT[type_button.text])
        old_type = type_button.text
        new_locate = False

        pygame.display.set_icon(image)
        pygame.display.set_caption(locate, locate)

        screen.blit(image, (0, 0))

    gui.update()
    gui.render(screen)
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()

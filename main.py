from GUI import *
from multitool import *

FPS = 60
next_spn = None
locate = "Красная площадь, 1"
# locate = "Австралия"
# locate = input("Enter locate: ")
# SPN_STEP = float(input("Enter the zoom-ratio: "))
SPN_STEP = 0.003
l_mode = 'гибрид'
points = []
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
        "spn": str_param(*spn),
        "pt": '~'.join([points[i] + (str(i + 1) if i < 99 else '') for i in range(len(points))])
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
spn = search_spn(get_geo_object(coords[0], coords[1]))
max_spn = spn[0] + 2*SPN_STEP, spn[1] + 2*SPN_STEP
# print(max_spn)
# вид карт
maps = ["Схема", "Спутник", "Гибрид"]
START_TYPE = maps.index(l_mode.title())
new_locate = False
image = map_image(coords[0], coords[1], L_DICT[maps[START_TYPE]])

pygame.init()
clock = pygame.time.Clock()
pygame.display.set_icon(image)
pygame.display.set_caption(get_address(coords), locate)
screen = pygame.display.set_mode(SIZE)
screen.blit(image, (0, 0))
pygame.display.flip()

throbber = GIFImage('Throbber-small.gif')
throbber_coords = (SIZE[0] / 2 - throbber.get_width() / 2, SIZE[1] / 2 - throbber.get_height() / 2)


# GUI ELEMENTS

def loading():
    throbber.render(screen, throbber_coords)
    pygame.display.flip()


def type_button_click(button):
    button.text = maps[(maps.index(button.text) + 1) % 3]


def search_textbox_event(textbox):
    global locate
    global coords
    global new_locate
    locate = textbox.text
    coords = get_coord(locate)
    points.append(create_point(*coords))
    if delete_last_button not in gui.element:
        gui.add_element(delete_last_button, full_address, index_button)
    new_locate = True


def delete_last_event(button):
    if points:
        del points[-1]
        global new_locate
        new_locate = True


def view_index(button: Button):
    global if_postal_code
    global adderss
    loading()
    if get_postal_code(coords):
        address = get_address(coords, postal_code=if_postal_code)
        full_address.text = address
        if_postal_code = not if_postal_code
        if if_postal_code:
            button.bg_color = button.active_color = index_button_active_color
        else:
            button.bg_color = button.active_color = index_button_disable_color
    else:
        button.active = False
        button.pressed = True
        button.bg_color = button.active_color = to_color("gray54")
    loading()


bg_color = to_color((240, 189, 0))
active_color = to_color((255, 204, 0))
label_bg_color = to_color("#ffffff99")
text_color = to_color("gray20")

# Переменная, которая сообщает, есть ли почтовый индекс у объекта по данным координатам
have_a_postal_code = get_postal_code(coords)
if_postal_code = bool(have_a_postal_code)


search_textbox = TextBox((5, 5, 330, 35), '', execute=search_textbox_event, placeholder="Поиск…",
                         bg_color=label_bg_color, text_color=text_color)

search_button = Button((5, 50, 100, 35), 'Поиск', 'black', bg_color, active_color,
                       click_event=lambda x: search_textbox_event(search_textbox))


type_button_rect = pygame.Rect(0, 0, 100, 35)
type_button_rect.bottomright = (SIZE[0]-5, SIZE[1]-5)

type_button = Button(type_button_rect, maps[START_TYPE], 'black', bg_color, active_color,
                     click_event=type_button_click)
old_type = maps[START_TYPE]

delete_last_rect = pygame.Rect(0, 0, 200, 35)
delete_last_rect.bottomleft = (5, SIZE[1]-5)

delete_last_button = Button(delete_last_rect, "Сброс поискового результата", 'black', bg_color, active_color,
                            click_event=delete_last_event)

# адрес найденного объекта
address = get_address(coords, postal_code=if_postal_code)
print(address)

full_address_rect = pygame.Rect(0, 0, 250, 35)
full_address_rect.topright = SIZE[0] - 5, 5

full_address = Label(full_address_rect, address, bg_color=label_bg_color,  text_position='right',
                     text_color=text_color,  auto_line_break=True, real_fill_bg=True)


# кнопка вывода индекса
index_rect = pygame.Rect(210, 410, 100, 35)

index_button_active_color = to_color((200, 19, 0))
index_button_disable_color = to_color((19, 200, 0))

index_button_bg_color = index_button_active_color if if_postal_code else index_button_disable_color

index_button = Button(index_rect, "Индекс", "black", index_button_bg_color, click_event=view_index,
                      active=if_postal_code, active_color=index_button_bg_color)

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

        loading()
        pygame.display.flip()
        image = map_image(coords[0], coords[1], L_DICT[type_button.text])

        loading()
        pygame.display.flip()

        address = get_address(coords, postal_code=if_postal_code)
        # print(address)
        full_address.text = address

        loading()
        pygame.display.flip()

        old_type = type_button.text
        new_locate = False

        pygame.display.set_icon(image)

        pygame.display.set_caption(address, locate)

        screen.blit(image, (0, 0))

    if not points:
        gui.delete(delete_last_button)
        gui.delete(full_address)
        gui.delete(index_button)
        # Сюда добавить удаление кнопки

    screen.blit(image, (0, 0))
    gui.update()
    gui.render(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()

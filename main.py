from zoom_spn import *

new_zoom = None
# locate = "Москва, Красная площадь, 1"
locate = "Пенза, Центральная 1в"
# locate = "Россия"
# locate = input("Enter locate: ")
# COORD_STEP = float(input("Enter the zoom-ratio: "))
COORD_STEP = 0.003
l_mode = 'гибрид'
L_DICT = {
    "Гибрид": ['sat', 'skl'],
    "Спутник": ['sat'],
    "Схема": ['map'],
}
KEY_CONTROL = {
    "up": [0, COORD_STEP],
    "down": [0, -COORD_STEP],
    "right": [COORD_STEP, 0],
    "left": [-COORD_STEP, 0],
}


def map_image(long, lat, l=['sat', 'skl']):
    params = {
        "ll": str_param(long, lat),
        "l": ','.join(l),
        "size": str_param(*SIZE),
        "z": z,
        "pt": render_points()
    }

    return convert_bytes(get_request(STATIC, params).content)


def sum_spn(spn, s1, s2=None):
    if s2 is None:
        s2 = s1
    spn = list(spn)
    spn[0] += s1
    spn[1] += s2
    return tuple(spn)


def get_new_zoom(c: int):
    return c + z if c + z in range(3, 18) else z


coords = get_coord(locate)
z = search_z(get_geo_object(locate))
# print(z)

# вид карт
maps = ["Схема", "Спутник", "Гибрид"]
START_TYPE = maps.index(l_mode.title())
new_locate = False
image = map_image(coords[0], coords[1], L_DICT[maps[START_TYPE]])

pygame.init()
pygame.display.set_icon(image)
pygame.display.set_caption(get_address(locate), locate)
screen = pygame.display.set_mode(SIZE)  # type: pygame.Surface
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


def search_textbox_event(textbox, coord=None):
    global locate
    global coords
    global render
    global new_locate
    if coord is None:
        locate = get_address(textbox.text)
        coords = get_coord(locate)
        coord = coords
        gui.delete(organization_label)
        new_locate = True
    else:
        locate = get_address(coord)
        render = True
    create_point(*coord)
    if delete_last_button not in gui.element:
        gui.add_element(delete_last_button, full_address, index_checkbox)


def delete_last_event(button):
    if points:
        del points[-1]
        global render
        render = True


def event_index(cb: Checkbox2):
    loading()
    global address
    address = full_address.text = get_address(locate, cb.pressed)
    loading()


bg_color = to_color((240, 189, 0))
active_color = to_color((255, 204, 0))
label_bg_color = to_color("#ffffff99")
text_color = to_color("gray20")

# Переменная, которая сообщает, есть ли почтовый индекс у объекта по данным координатам
have_a_postal_code = get_postal_code(locate)
if_postal_code = bool(have_a_postal_code)


search_textbox = TextBox((5, 5, 330, 35), locate, execute=search_textbox_event, placeholder="Поиск…",
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
address = get_address(locate, postal_code=if_postal_code)

full_address_rect = pygame.Rect(0, 0, 250, 35)
full_address_rect.topright = SIZE[0] - 5, 5

full_address = Label(full_address_rect, address, bg_color=label_bg_color,  text_position='right',
                     text_color=text_color,  auto_line_break=True, real_fill_bg=True)


# кнопка вывода индекса
index_rect = pygame.Rect(0, 0, 35, 35)
index_rect.bottomleft = delete_last_rect.right + 5, SIZE[1] - 5

index_checkbox = Checkbox2(index_rect, 'Индекс', text_color=text_color, box_color=active_color,
                           if_work=have_a_postal_code, click_event=event_index)


organization_label = Label(pygame.Rect(5, SIZE[1] - 45 - 35, 10, 35), '', text_color, label_bg_color, real_fill_bg=True)


gui = GUI(search_button, type_button, search_textbox)
running = True


def screen_render():
    screen.blit(image, (0, 0))

    r = pygame.Rect((0, SIZE[1] - 45, SIZE[0], 45))
    s = pygame.Surface(r.size, pygame.SRCALPHA)
    s.fill(label_bg_color)
    screen.blit(s, r)


render = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

        if event.type == pygame.MOUSEBUTTONDOWN and not search_textbox.focus:
            if event.button in (4, 5):
                new_zoom = get_new_zoom((1 if event.button == 4 else -1))
                # print("Zoom %d (%d)" % (z, (new_zoom - z)))

        if event.type == pygame.KEYDOWN and not search_textbox.focus:
            if event.key == pygame.K_PAGEUP or (event.key == pygame.K_KP9 and event.mod == 4096):
                new_zoom = get_new_zoom(-1)
                # print("Zoom up: %d" % new_zoom)

            if event.key == pygame.K_PAGEDOWN or (event.key == pygame.K_KP3 and event.mod == 4096):
                new_zoom = get_new_zoom(1)
                # print("Zoom down: %d" % new_zoom)

            if pygame.key.name(event.key) in KEY_CONTROL:
                coords = sum_spn(coords, *KEY_CONTROL[pygame.key.name(event.key)])
                new_locate = True

        in_gui = gui.get_event(event)
        if not in_gui and event.type == pygame.MOUSEBUTTONDOWN and event.button not in (4, 5):
            click = screen_to_geo(event.pos, coords, z)
            if event.button == 1:
                locate = get_address(click, if_postal_code)
                search_textbox_event(search_textbox, click)
                gui.delete(organization_label)
                render = True
                # print(click, locate)
            elif event.button == 3:
                search_textbox_event(search_textbox, click)
                org = geo_search(click)
                search_textbox_event(search_textbox, click)
                if org:
                    if organization_label not in gui.element:
                        gui.element.insert(0, organization_label)
                    organization_label.text = org[0]['properties']['CompanyMetaData']['name']
                    create_point(*org[0]['geometry']['coordinates'])
                else:
                    gui.delete(organization_label)

    if render or (new_zoom != z and new_zoom is not None) or old_type != type_button.text or new_locate:
        z = new_zoom if new_zoom is not None else z
        edit_z = new_zoom is None
        new_zoom = None
        render = False

        loading()
        have_a_postal_code = get_postal_code(locate)

        if_postal_code = if_postal_code and have_a_postal_code
        index_checkbox.pressed = if_postal_code
        index_checkbox.work = bool(have_a_postal_code)

        loading()
        address = get_address(locate, postal_code=if_postal_code)
        # print(address)
        full_address.text = address

        if edit_z and new_locate:
            z = search_z(get_geo_object(locate))
            edit_z = False

        loading()
        image = map_image(coords[0], coords[1], L_DICT[type_button.text])

        loading()
        old_type = type_button.text
        new_locate = False

        pygame.display.set_icon(image)

        pygame.display.set_caption(address, locate)

        screen_render()

    if not points:
        gui.delete(delete_last_button)
        gui.delete(full_address)
        gui.delete(index_checkbox)
        # Сюда добавить удаление кнопки

    screen_render()
    gui.update()
    gui.render(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()

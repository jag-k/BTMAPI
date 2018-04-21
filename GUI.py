from PIL import Image
import pygame
from pygame.locals import *
import time
pygame.init()


def to_color(color):
    if color is None:
        return None
    if color == -1:
        return pygame.Color(0, 0, 0, 0)
    if type(color) is pygame.Color:
        return color
    if type(color) is tuple:
        return pygame.Color(*color)
    return pygame.Color(color)


def split_line(text, width, font):

    def if_in_rect(t):
        return font.render(t, 1, to_color('black')).get_rect().width <= width

    w = font.render(text, 1, to_color('black')).get_rect().width
    try:
        if w > width:
            new = ''
            index = 0
            while if_in_rect(' '.join(text.split()[:index+1])):
                new = ' '.join(text.split()[:index+1])
                index += 1
            return [new] + split_line(' '.join(text.split()[index:]), width, font)
        return [' '.join(text.split())]
    except RecursionError:
        raise BaseException("This text (%s) does not fit in the field! Please increase the width!" % text)


class GUI:
    def __init__(self, *elemets):
        self.element = list(elemets)
        self.active_tb = len(self.textbox_list)-1
        self.check = True

    @property
    def textbox_list(self):
        return list(filter(lambda x: type(x) is TextBox, self.element))

    def add_element(self, *element):
        self.element += element
        return self

    def render(self, surface, text=None):
        for i in self.element:
            render = getattr(i, "render", None)
            if callable(render):
                i.render(surface)

    def update(self):
        for i in self.element:
            render = getattr(i, "update", None)
            if callable(render):
                i.update()

        if all(map(lambda x: not x.focus, self.textbox_list)):
            self.active_tb = 0
        elif not self.check:
            for i in self.textbox_list:
                if i.focus:
                    self.active_tb = self.textbox_list.index(i)

        if self.check and self.textbox_list:
            for i in self.textbox_list:
                i.focus = False
            self.textbox_list[self.active_tb].focus = True
            self.check = False

        # print('\r%d' % self.active_tb, end='', flush=True)

    def get_event(self, event):
        for i in self.element:
            get_event = getattr(i, "get_event", None)
            if callable(get_event):
                i.get_event(event)
        if event.type == pygame.KEYDOWN and event.key == 9 and self.textbox_list:
            self.active_tb += 1
            self.active_tb = self.active_tb % len(self.textbox_list)
            self.check = True

    def delete(self, item):
        if item in self.element:
            del self.element[self.element.index(item)]


class OldLabel:
    def __init__(self, rect, text, text_color='gray', bg_color=-1, text_position='left'):
        self.Rect = pygame.Rect(rect)
        self.text = text
        self.text_pos = text_position
        self.font_color = to_color(text_color)
        self.bg_color = None if bg_color == -1 else to_color(bg_color)
        self.font = pygame.font.Font(None, self.Rect.height - 4)
        self.rendered_text = None
        self.rendered_rect = None

    def render(self, surface, text=None):
        if text is None:
            text = self.text
        if self.bg_color is not None:
            screen = pygame.Surface(self.Rect.size, pygame.SRCALPHA)
            screen.fill(self.bg_color)
            surface.blit(screen, self.Rect)

        self.rendered_text = self.font.render(text, 1, self.font_color)
        self.rendered_rect = self.rendered_text.get_rect(x=self.Rect.x + 2, centery=self.Rect.centery)

        if self.text_pos == 'center':
            self.rendered_rect.centerx = self.Rect.centerx
        elif self.text_pos == 'right':
            self.rendered_rect.right = self.Rect.right

        surface.blit(self.rendered_text, self.rendered_rect)


class Label:
    def __init__(self, rect, text, text_color='gray', bg_color=-1, text_position='left',
                 line_spacing=5, font_size=None, auto_line_break=False, real_fill_bg=False):

        self.Rect = pygame.Rect(rect)
        self.text = text
        self.text_pos = text_position
        self.font_color = to_color(text_color)
        self.bg_color = to_color(bg_color)
        self.line_break = auto_line_break
        self.real_fill = real_fill_bg

        text = text.split('\n')

        font_size = self.Rect.height // len(text) - 4 - len(text) * line_spacing + line_spacing if font_size is None \
            else font_size

        self.font = pygame.font.Font(None, font_size)
        self.line_spacing = line_spacing

    def render(self, surface, text=None):
        screen = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        if not self.real_fill:
            screen.fill(self.bg_color, self.Rect)
        else:
            bg = pygame.Surface(surface.get_size(), pygame.SRCALPHA)

        text = self.text.split('\n') if text is None else text.split('\n')
        step = 0
        start_pos = [max(0, self.Rect.x - 2), max(0, self.Rect.y - 2)]
        end_pos = [self.Rect.x, self.Rect.y]

        for j in text:
            for i in (split_line(j, self.Rect.width - 4, self.font) if self.line_break else (j, )):
                rendered_text = self.font.render(i, 1, self.font_color)
                rendered_rect = rendered_text.get_rect(x=self.Rect.x + 2, y=self.Rect.y + 2 + step)

                if self.text_pos == 'center':
                    rendered_rect.centerx = self.Rect.centerx
                elif self.text_pos == 'right':
                    rendered_rect.right = self.Rect.right - 2

                end_pos = rendered_rect.bottomright
                step += self.line_spacing + rendered_rect.h

                screen.blit(rendered_text, rendered_rect)

        if self.real_fill:
            bg.fill(self.bg_color, (start_pos, tuple(map(lambda x: x + 2, end_pos))))
            surface.blit(bg, (0, 0))

        surface.blit(screen,  (0, 0))


class TextBox(OldLabel):
    def __init__(self, rect, text, max_len=None, execute=(lambda self: self.set_focus()), placeholder=None,
                 bg_color='white', text_color='gray'):
        super().__init__(rect, text, text_color=text_color, bg_color=bg_color)
        self.focus = False
        self.blink = True
        self.blink_timer = 0
        self.shift = 0
        self.max_len = max_len
        self.execute = execute
        self.placeholder = placeholder

    def can_write(self, text=None):
        if text is None:
            text = self.text
        return self.font.size(text)[0] < self.Rect.width if self.max_len is None else len(text) <= self.max_len

    @property
    def get_text(self):
        return [self.text[:len(self.text)-self.shift] if self.shift else self.text,
                self.text[len(self.text)-self.shift:]]

    def get_event(self, event):
        if event.type == pygame.KEYDOWN and self.focus:
            if event.key == pygame.K_ESCAPE:
                self.focus = False
                return None
            text = self.get_text
            if event.key in (pygame.K_KP_ENTER, pygame.K_RETURN, 27):
                self.execute(self)
            elif event.key == pygame.K_BACKSPACE:
                self.text = text[0][:-1] + text[1]

            elif event.key == pygame.K_DELETE:
                self.text = text[0] + text[1][1:]
                self.shift -= int(bool(self.shift))

            elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                if event.key % 2:
                    self.shift -= int(self.shift > 0)
                else:
                    self.shift += int(self.shift < len(self.text))
            else:
                text[0] += event.unicode if (event.unicode.isprintable() or event.unicode == ' ') else ''
                if self.can_write(''.join(text)):
                    self.text = ''.join(text)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.focus = self.Rect.collidepoint(*event.pos)
            if self.focus:
                t = ''
                in_text = False
                for i in self.text+' ':
                    rect = self.font.render(t, 1, self.font_color).get_rect(x=self.Rect.x + 2,
                                                                            centery=self.Rect.centery)
                    if rect.collidepoint(*event.pos):
                        self.shift = len(self.text) - len(t)
                        in_text = True
                        break
                    t += i
                self.shift = 0 if not in_text else self.shift

    def update(self):
        if pygame.time.get_ticks() - self.blink_timer > 200:
            self.blink = not self.blink
            self.blink_timer = pygame.time.get_ticks()

    def render(self, surface, text=None):
        super().render(surface, text=self.text if self.text or self.placeholder is None else self.placeholder)
        if self.focus and self.blink:
            self.rendered_text = self.font.render(self.get_text[0], 1, self.font_color)
            self.rendered_rect = self.rendered_text.get_rect(x=self.Rect.x + 2, centery=self.Rect.centery)

            is_shift = (2 if not self.shift else 0)
            pygame.draw.line(surface, (0, 0, 0), (self.rendered_rect.right + is_shift, self.rendered_rect.top + 2),
                             (self.rendered_rect.right + is_shift, self.rendered_rect.bottom - 2))


class Button(OldLabel):
    def __init__(self, rect, text, text_color='gray', bg_color=pygame.Color('blue'),
                 active_color=pygame.Color("lightblue"), active=True, click_event=(lambda self: self)):
        super().__init__(rect, text, text_color=text_color, bg_color=bg_color, text_position='center')
        self.active_color = to_color(active_color)
        self.color = self.bg_color
        self.pressed = False
        self.active = active
        self.button_up = False
        self.click_event = click_event

    def __bool__(self):
        if self.button_up and self.active:
            self.button_up = False
            return True
        return False

    def render(self, surface, text=None):
        surface.fill(self.color, self.Rect)
        text = ''
        for t in self.text:
            text += t
            if self.font.size(text+'...')[0] > self.Rect.width - 7 or self.font.size(text)[0] > self.Rect.width:
                text = text+('...' if not text.startswith(self.text) else '')
                break
        self.rendered_text = self.font.render(text, 1, self.font_color)

        if self.pressed and self.active:
            color1 = pygame.Color("black")
            color2 = pygame.Color("white")
            self.rendered_rect = self.rendered_text.get_rect(centerx=self.Rect.centerx + 4,
                                                             centery=self.Rect.centery + 2)
        else:
            color1 = pygame.Color("white")
            color2 = pygame.Color("black")
            self.rendered_rect = self.rendered_text.get_rect(centerx=self.Rect.centerx + 3,
                                                             centery=self.Rect.centery)
        # рисуем границу
        pygame.draw.rect(surface, color1, self.Rect, 2)
        pygame.draw.line(surface, color2, (self.Rect.right - 1, self.Rect.top),
                         (self.Rect.right - 1, self.Rect.bottom), 2)
        pygame.draw.line(surface, color2, (self.Rect.left, self.Rect.bottom - 1),
                         (self.Rect.right, self.Rect.bottom - 1), 2)
        # выводим текст
        surface.blit(self.rendered_text, self.rendered_rect)

    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.pressed = self.Rect.collidepoint(*event.pos)
            if self.pressed:
                self.click_event(self)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.button_up = self.pressed
            self.pressed = False
            return True
        if event.type == pygame.MOUSEMOTION and self.active:
            self.color = self.active_color if self.Rect.collidepoint(*event.pos) else self.bg_color


class Checkbox:
    def __init__(self, rect, text, text_color='white', box_color='blue', if_work=True,
                 click_event=(lambda x: x)):
        self.Rect = rect if type(rect) is pygame.Rect else pygame.Rect(rect)
        self.text = text
        self.color = to_color(box_color)
        self.font_color = to_color(text_color)
        self.font = pygame.font.Font(None, self.Rect.height - 4)
        self.rendered_text = None
        self.rendered_rect = None
        self.pressed = False
        self.work = if_work
        self.click_event = click_event

    def render(self, surface, text=None, status=None):
        if not self.work:
            return
        if status is None:
            status = self.pressed

        r = self.Rect
        self.rendered_text = self.font.render(self.text, 1, self.font_color)
        self.rendered_rect = self.rendered_text.get_rect(x=r.x + r.width + 5, centery=r.centery)
        surface.blit(self.rendered_text, self.rendered_rect)
        pygame.draw.rect(surface, self.color, r, 1)

        if status:
            pygame.draw.line(surface, self.color, r.topleft, r.bottomright)
            pygame.draw.line(surface, self.color, r.topright, r.bottomleft)

    def get_event(self, event):
        try:
            if event.type == pygame.MOUSEBUTTONDOWN and \
                    (self.Rect.collidepoint(*event.pos) or self.rendered_rect.collidepoint(event.pos)):
                self.pressed = not self.pressed
                return self.click_event(self)
        except AttributeError:
            return


class Checkbox2(Checkbox):
    def __init__(self, rect, text, space=5, text_color='white', box_color='blue', if_work=True,
                 click_event=(lambda x: x)):
        super().__init__(rect, text, text_color, box_color, if_work, click_event)
        self.space = space

    def render(self, surface, text=None, status=None):
        if not self.work:
            return
        super().render(surface, text, False)
        if status is None:
            status = self.pressed

        r = self.Rect
        if status:
            pygame.draw.rect(surface, self.color, (r.left + self.space, r.top + self.space,
                                                   r.width - self.space * 2, r.height - self.space * 2))


"""GIFImage by Matthew Roe"""


class GIFImage(object):
    def __init__(self, filename):
        self.filename = filename
        self.image = Image.open(filename)
        self.frames = []
        self.get_frames()

        self.cur = 0
        self.ptime = time.time()

        self.running = True
        self.breakpoint = len(self.frames)-1
        self.startpoint = 0
        self.reversed = False

    def get_rect(self):
        return pygame.rect.Rect((0, 0), self.image.size)

    def get_frames(self):
        image = self.image

        pal = image.getpalette()
        base_palette = []
        for i in range(0, len(pal), 3):
            rgb = pal[i:i+3]
            base_palette.append(rgb)

        all_tiles = []
        try:
            while 1:
                if not image.tile:
                    image.seek(0)
                if image.tile:
                    all_tiles.append(image.tile[0][3][0])
                image.seek(image.tell()+1)
        except EOFError:
            image.seek(0)

        all_tiles = tuple(set(all_tiles))

        try:
            while 1:
                try:
                    duration = image.info["duration"]
                except:
                    duration = 100

                duration *= .001  # convert to milliseconds!
                cons = False

                x0, y0, x1, y1 = (0, 0) + image.size
                if image.tile:
                    tile = image.tile
                else:
                    image.seek(0)
                    tile = image.tile
                if len(tile) > 0:
                    x0, y0, x1, y1 = tile[0][1]

                if all_tiles:
                    if all_tiles in ((6,), (7,)):
                        cons = True
                        pal = image.getpalette()
                        palette = []
                        for i in range(0, len(pal), 3):
                            rgb = pal[i:i+3]
                            palette.append(rgb)
                    elif all_tiles in ((7, 8), (8, 7)):
                        pal = image.getpalette()
                        palette = []
                        for i in range(0, len(pal), 3):
                            rgb = pal[i:i+3]
                            palette.append(rgb)
                    else:
                        palette = base_palette
                else:
                    palette = base_palette

                pi = pygame.image.fromstring(image.tobytes(), image.size, image.mode)
                pi.set_palette(palette)
                if "transparency" in image.info:
                    pi.set_colorkey(image.info["transparency"])
                pi2 = pygame.Surface(image.size, SRCALPHA)
                if cons:
                    for i in self.frames:
                        pi2.blit(i[0], (0,0))
                pi2.blit(pi, (x0, y0), (x0, y0, x1-x0, y1-y0))

                self.frames.append([pi2, duration])
                image.seek(image.tell()+1)
        except EOFError:
            pass

    def render(self, screen, pos):
        if self.running:
            if time.time() - self.ptime > self.frames[self.cur][1]:
                if self.reversed:
                    self.cur -= 1
                    if self.cur < self.startpoint:
                        self.cur = self.breakpoint
                else:
                    self.cur += 1
                    if self.cur > self.breakpoint:
                        self.cur = self.startpoint

                self.ptime = time.time()

        screen.blit(self.frames[self.cur][0], pos)

    def seek(self, num):
        self.cur = num
        if self.cur < 0:
            self.cur = 0
        if self.cur >= len(self.frames):
            self.cur = len(self.frames)-1

    def set_bounds(self, start, end):
        if start < 0:
            start = 0
        if start >= len(self.frames):
            start = len(self.frames) - 1
        if end < 0:
            end = 0
        if end >= len(self.frames):
            end = len(self.frames) - 1
        if end < start:
            end = start
        self.startpoint = start
        self.breakpoint = end

    def pause(self):
        self.running = False

    def play(self):
        self.running = True

    def rewind(self):
        self.seek(0)

    def fastforward(self):
        self.seek(self.length()-1)

    def get_height(self):
        return self.image.size[1]

    def get_width(self):
        return self.image.size[0]

    def get_size(self):
        return self.image.size

    def length(self):
        return len(self.frames)

    def reverse(self):
        self.reversed = not self.reversed

    def reset(self):
        self.cur = 0
        self.ptime = time.time()
        self.reversed = False

    def copy(self):
        new = GIFImage(self.filename)
        new.running = self.running
        new.breakpoint = self.breakpoint
        new.startpoint = self.startpoint
        new.cur = self.cur
        new.ptime = self.ptime
        new.reversed = self.reversed
        return new

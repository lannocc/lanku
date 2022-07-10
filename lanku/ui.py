from .config import *

from pyglet.window import Window as PWin
from pyglet.graphics import Batch
from pyglet.shapes import Rectangle
from pyglet.image import ImageData
from pyglet.text import Label as PLabel
from pyglet.gui import Frame as PFrame, PushButton, TextEntry as PTextEntry
from pyglet import clock
import pyglet.resource
pyglet.resource.path = ['@lanku']
pyglet.resource.reindex()

import platform


def image(name):
    return pyglet.resource.image(f'assets/{name}')


class LWin(PWin):
    def __init__(self, app, caption, w, h, save_name=None, resizable=True):
        self.app = app
        self.save_name = save_name

        super().__init__(w, h, caption=caption, resizable=resizable,
            visible=False)

        self.xywh = [0, 0, w, h]
        self.load()
        self.hidden = False
        self.minimized = False

        icon = self.app.icon
        self.set_icon(ImageData(icon.width, icon.height, 'RGBA',
            icon.tobytes(), pitch=-icon.width*4))

        self.frame = PFrame(self)
        self.batch = Batch()
        self.components = [ ]

        self.offset_for = None
        self.offset = None

    def _add_(self, child):
        self.components.append(child)

    def on_draw(self):
        self.clear()
        self.batch.draw()
        for child in self.components:
            child.draw()

    def save(self):
        if not self.save_name or not self.xywh: return
        save_win_config(self.save_name,
                        self.xywh[0], self.xywh[1],
                        self.xywh[2], self.xywh[3])

    def load(self):
        if not self.save_name: return
        config = load_win_config(self.save_name)
        if not config: return

        #print(f'load: {config}')
        self.xywh = config

    def place(self):
        if not self.xywh: return
        #print(f'location set: {self.xywh[0]}, {self.xywh[1]}')
        x = self.xywh[0]
        y = self.xywh[1]

        if self.offset:
            x += self.offset[0]
            y += self.offset[1]
        else:
            self.offset_for = (x, y)

        #print(f'actual set_location: {x}, {y}')
        self.set_size(self.xywh[2], self.xywh[3])
        self.set_location(x, y)

        if not self.offset:
            clock.schedule_once(self.place_offset, 0.5)

    def place_offset(self, dt):
        #print(f'location get: {self.get_location()}')
        x = self.offset_for[0]
        y = self.offset_for[1]

        #if x != self.offset_for[0] or y != self.offset_for[1]:
        #    print('bail')
        #    return

        pos = self.get_location()
        self.offset = (x - pos[0], y - pos[1])
        #print(f'computed window offset: {self.offset}')

        if any(self.offset):
            #self.place()
            self.xywh[0] += self.offset[0]
            self.xywh[1] += self.offset[1]
            #print(f'adjusted xywh: {self.xywh}')

        #self.offset_for = None

    def null(self, dt):
        #print('null')
        pass

    def set_visible(self, visible=True):
        #print(f'set_visible {visible}')
        self.hidden = not visible
        restore = self.minimized and visible

        if not visible:
            self.save()

        super().set_visible(visible)

        if restore:
            #print('restore')

            if platform.system() == 'Windows':
                # hack: only way to restore on Windows?
                xywh = list(self.xywh)
                self.maximize()
                self.xywh = xywh

        if visible:
            self.place()

            if not restore:
                # hack: sometimes necessary to trigger redraw on Linux
                clock.schedule_once(self.null, 0.1)

    def on_show(self):
        #print('show')
        self.minimized = False

    def on_hide(self):
        #print('hide')
        if not self.hidden:
            #print('minimized')
            self.minimized = True

    def on_move(self, x, y):
        #print(f'move {x},{y}')
        if x < 0 or y < 0: return

        if not self.offset_for and self.offset:
            x += self.offset[0]
            y += self.offset[1]

        if self.xywh:
            self.xywh[0] = x
            self.xywh[1] = y
        else:
            w, h = self.get_size()
            self.xywh = [x, y, w, h]

    def on_resize(self, w, h):
        #print(f'resize {w},{h}')
        if self.xywh:
            self.xywh[2] = w
            self.xywh[3] = h
        else:
            x, y = self.get_location()
            self.xywh = [x, y, w, h]
        super().on_resize(w, h)

    def on_close(self):
        self.save()
        super().on_close()


class LFrame(PFrame):
    def __init__(self, win, enabled=True, cell_size=64, order=0):
        self.enabled = enabled
        super().__init__(win, cell_size, order)
        self.stack = [ ]

    def _add_(self, child):
        self.stack.append(child)

    def _del_(self, child):
        del self.stack[self.stack.index(child)]

    def enable(self):
        self.enabled = True
        for child in self.stack:
            if child.visible:
                child.cframe.enable()

    def disable(self):
        self.enabled = False
        for child in self.stack:
            if child.visible:
                child.cframe.disable()

    def on_mouse_press(self, x, y, btns, mods):
        if not self.enabled: return
        super().on_mouse_press(x, y, btns, mods)

    def on_mouse_release(self, x, y, btns, mods):
        if not self.enabled: return
        super().on_mouse_release(x, y, btns, mods)

    def on_mouse_drag(self, x, y, dx, dy, btns, mods):
        if not self.enabled: return
        super().on_mouse_drag(x, y, dx, dy, btns, mods)

    def on_mouse_scroll(self, x, y, index, direction):
        if not self.enabled: return
        super().on_mouse_scroll(x, y, index, direction)

    def on_mouse_motion(self, x, y, dx, dy):
        if not self.enabled: return
        super().on_mouse_motion(x, y, dx, dy)

    def on_text(self, text):
        if not self.enabled: return
        super().on_text(text)

    def on_text_motion(self, motion):
        if not self.enabled: return
        super().on_text_motion(motion)

    def on_text_motion_select(self, motion):
        if not self.enabled: return
        super().on_text_motion_select(motion)


class Component:
    def __init__(self, parent, x, y, visible=True):
        self.parent = parent
        if isinstance(self.parent, LWin):
            self.win = self.parent
        else:
            self.win = self.parent.win
        self.pos = [x, y] # relative
        self._visible_ = visible

        self.cbatch = Batch()
        self.cframe = LFrame(self.win, self.visible)

        self.stack = [ ]
        self.parent._add_(self)

    def _add_(self, child):
        self.stack.append(child)
        self.cframe._add_(child)

    def _del_(self, child):
        del self.stack[self.stack.index(child)]
        self.cframe._del_(child)

    @property
    def visible(self):
        return self._visible_

    @visible.setter
    def visible(self, visible):
        self._visible_ = visible
        if visible:
            self.cframe.enable()
        else:
            self.cframe.disable()

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def draw(self):
        if not self.visible: return
        self.cbatch.draw()
        for child in self.stack:
            child.draw()

    def get_abs_pos(self):
        if isinstance(self.parent, LWin):
            return self.pos

        else:
            pos = self.parent.get_abs_pos()
            return [pos[0] + self.pos[0], pos[1] + self.pos[1]]

    def null(self, dt):
        pass


class Label(Component, PLabel):
    def __init__(self, parent, x, y, text):
        Component.__init__(self, parent, x, y)
        pos = self.get_abs_pos()
        PLabel.__init__(self, text, x=pos[0], y=pos[1], batch=self.cbatch)
        #self.cframe.add_widget(self)


class TextEntry(Component, PTextEntry):
    def __init__(self, parent, x, y, w, text=None, mask=None):
        Component.__init__(self, parent, x, y)
        pos = self.get_abs_pos()
        PTextEntry.__init__(self, text, pos[0], pos[1], w,
            caret_color=(0, 255, 0), batch=self.cbatch)
        self.mask = mask

        if self.mask:
            self.real_val = ''
            self._del_text_orig_ = self._doc.delete_text
            self._doc.delete_text = self._del_text_

        self.cframe.add_widget(self)

    def on_mouse_motion(self, x, y, dx, dy):
        if not self.enabled:
            return

        self._set_focus(self._check_hit(x, y))

    @property
    def value(self):
        if self.mask:
            return self.real_val

        else:
            return super().value

    def on_text(self, text):
        if not self.enabled: return

        if self.mask:
            pos = self._caret.position
            self.real_val = self.real_val[:pos] + text + self.real_val[pos:]
            text = self.mask

        super().on_text(text)

    def _del_text_(self, start, end):
        self.real_val = self.real_val[:start] + self.real_val[end:]
        self._del_text_orig_(start, end)


class Button(Component, PushButton):
    def __init__(self, parent, x, y, normal, pushed, hovering):
        Component.__init__(self, parent, x, y)
        pos = self.get_abs_pos()
        PushButton.__init__(self, pos[0], pos[1], pushed, normal, hovering,
            batch=self.cbatch)
        self.cframe.add_widget(self)

    def set_pos(self, x, y):
        self.pos = [x, y]
        pos = self.get_abs_pos()
        self._x = pos[0]
        self._y = pos[1]
        self._update_position()

    def remove(self):
        self.cframe.remove_widget(self)
        self.parent._del_(self)


class ToggleButton(Button):
    def __init__(self, parent, x, y, normal, pushed, hovering,
            toggle_normal, toggle_pushed, toggle_hovering, toggled=False):

        if toggled:
            super().__init__(parent, x, y, toggle_normal, toggle_pushed,
                             toggle_hovering)
        else:
            super().__init__(parent, x, y, normal, pushed, hovering)

        self.normal = normal
        self.pushed = pushed
        self.hovering = hovering
        self.toggle_normal = toggle_normal
        self.toggle_pushed = toggle_pushed
        self.toggle_hovering = toggle_hovering

        self._toggled_ = toggled

    @property
    def toggled(self):
        return self._toggled_

    @toggled.setter
    def toggled(self, toggled):
        self._toggled_ = toggled

        if toggled:
            self._depressed_img = self.toggle_normal
            self._pressed_img = self.toggle_pushed
            self._hover_img = self.toggle_hovering

        else:
            self._depressed_img = self.normal
            self._pressed_img = self.pushed
            self._hover_img = self.hovering

    def on_press(self):
        self.toggled = not self.toggled
        self.dispatch_event('on_toggle', self.toggled)

ToggleButton.register_event_type('on_toggle')


class TabGroup(Component):
    def __init__(self, parent, x, y, w, h):
        super().__init__(parent, x, y)
        self.size = [w, h]

        self.tabs = [ ]
        self.tabs_width = 0

        pos = self.get_abs_pos()
        self.rect = Rectangle(pos[0], pos[1], w, h, color=(42, 42, 42),
            batch=self.cbatch)

    def set_size(self, w, h):
        if w != self.size[0]:
            self.rect.width = w

        if h != self.size[1]:
            self.rect.height = h

        self.size = [w, h]

    def tab(self, panel, normal, active, hover):
        tab = Tab(self, normal, active, hover)

        if self.tabs:
            panel.hide()

        else:
            panel.show()
            tab._pressed = True
            tab._sprite.image = tab._pressed_img

        self.tabs_width += max(normal.width, active.width, hover.width)
        self.tabs.append((tab, panel))

        return tab


class Tab(Button):
    def __init__(self, tab_group, normal, active, hover):
        x = tab_group.tabs_width
        y = max(normal.height, active.height, hover.height)

        super().__init__(tab_group, x, -y, normal, active, hover)

    def select(self):
        self.on_press()

    def on_press(self):
        for tab, panel in self.parent.tabs:
            if tab is self:
                tab._pressed = True
                tab._sprite.image = tab._pressed_img
                panel.show()

            elif tab._pressed:
                tab._pressed = False
                tab._sprite.image = tab._depressed_img
                panel.hide()

    def on_mouse_release(self, x, y, btns, mods):
        pass


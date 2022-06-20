from .config import *

from pyglet.window import Window as PWin
from pyglet.graphics import Batch
from pyglet.shapes import Rectangle
from pyglet.image import ImageData
from pyglet.text import Label as PLabel
from pyglet.gui import Frame as PFrame, PushButton
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

        self.load()
        self.hidden = False
        self.minimized = False

        icon = self.app.icon
        self.set_icon(ImageData(icon.width, icon.height, 'RGBA',
            icon.tobytes(), pitch=-icon.width*4))

        self.frame = PFrame(self)
        self.batch = Batch()
        self.components = [ ]

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
        self.set_location(self.xywh[0], self.xywh[1])
        self.set_size(self.xywh[2], self.xywh[3])

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


class Label(Component, PLabel):
    def __init__(self, parent, x, y, text):
        Component.__init__(self, parent, x, y)
        pos = self.get_abs_pos()
        PLabel.__init__(self, text, x=pos[0], y=pos[1], batch=self.cbatch)
        #self.cframe.add_widget(self)


class Button(Component, PushButton):
    def __init__(self, parent, x, y, normal, pushed, hovering):
        Component.__init__(self, parent, x, y)
        pos = self.get_abs_pos()
        PushButton.__init__(self, pos[0], pos[1], pushed, normal, hovering,
            batch=self.cbatch)
        self.cframe.add_widget(self)


class TabGroup(Component):
    def __init__(self, parent, x, y, w, h):
        super().__init__(parent, x, y)
        self.size = [w, h]

        self.tabs = [ ]
        self.tabs_width = 0

        pos = self.get_abs_pos()
        self.rect = Rectangle(pos[0], pos[1], w, h, color=(42, 42, 42),
            batch=self.cbatch)

    def tab(self, panel, normal, active, hover):
        panel.hide()
        tab = Tab(self, normal, active, hover)
        self.tabs_width += max(normal.width, active.width, hover.width)
        self.tabs.append((tab, panel))


class Tab(Button):
    def __init__(self, tab_group, normal, active, hover):
        x = tab_group.tabs_width
        y = max(normal.height, active.height, hover.height)

        super().__init__(tab_group, x, -y, normal, active, hover)

    def on_press(self):
        for tab, panel in self.parent.tabs:
            if tab is self:
                tab._pressed = True
                tab._sprite.image = self._pressed_img
                panel.show()

            elif tab._pressed:
                tab._pressed = False
                tab._sprite.image = tab._depressed_img
                panel.hide()

    def on_mouse_release(self, x, y, btns, mods):
        pass


class LFrame(PFrame):
    def __init__(self, win, enabled=True, cell_size=64, order=0):
        self.enabled = enabled
        super().__init__(win, cell_size, order)
        self.stack = [ ]

    def _add_(self, child):
        self.stack.append(child)

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


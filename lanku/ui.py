from .config import *

from pyglet.window import Window as PWin
from pyglet.image import ImageData
from pyglet.text import Label
from pyglet import clock

import platform


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
                #clock.schedule_once(self.refresh, 0.1)
                clock.schedule_once(self.null, 0.1)

    def on_draw(self):
        #print('draw')
        self.clear()
        self.label.draw()

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


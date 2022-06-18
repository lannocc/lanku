from . import __version__
from .config import *

from pyglet.window import Window as Base
from pyglet.image import ImageData
from pyglet.text import Label
from pyglet import clock


class Window(Base):
    def __init__(self, app):
        self.app = app
        super().__init__(333, 555, caption='lanku',
            resizable=True, visible=False)

        self.minimized = False

        icon = self.app.icon
        self.set_icon(ImageData(icon.width, icon.height, 'RGBA',
            icon.tobytes(), pitch=-icon.width*4))

        self.label = Label(f'lanku v{__version__}')

    def save(self):
        if self.minimized: return
        x, y = self.get_location()
        w, h = self.get_size()
        save_home_config(x, y, w, h)

    def load(self):
        config = load_home_config()
        if not config: return

        self.set_location(config[0], config[1])
        self.set_size(config[2], config[3])

    def refresh(self, dt):
        #print('refresh')
        pass

    def set_visible(self, visible=True):
        if not visible:
            self.save()

        refresh = not self.minimized and visible
        super().set_visible(visible)

        if visible:
            self.load()

        if refresh:
            # sometimes it doesn't redraw automatically... this fixes it
            clock.schedule_once(self.refresh, 0.1)

    def on_draw(self):
        #print('draw')
        self.clear()
        self.label.draw()

    def on_show(self):
        self.minimized = False

    def on_hide(self):
        self.save()
        self.minimized = True

    def on_close(self):
        self.save()
        super().on_close()


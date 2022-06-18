from . import __version__

from pyglet.window import Window as Base
from pyglet.image import ImageData
from pyglet.text import Label
from pyglet import clock


class Window(Base):
    def __init__(self, app):
        super().__init__(333, 777, caption='lanku',
            resizable=True, visible=False)

        self.app = app
        self.minimized = False

        icon = self.app.icon
        self.set_icon(ImageData(icon.width, icon.height, 'RGBA',
            icon.tobytes(), pitch=-icon.width*4))

        self.label = Label(f'lanku v{__version__}')

    def refresh(self, dt):
        #print('refresh')
        pass

    def set_visible(self, visible=True):
        refresh = not self.minimized and visible
        super().set_visible(visible)
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
        self.minimized = True


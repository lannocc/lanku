from .__version__ import __version__
from .systray import Icon as TrayIcon
from .home import Window as Home

import pyglet.app
from PIL import Image, ImageDraw

from threading import Thread


#icon.notify('this is a test', 'lanku alert')


class Application:
    def __init__(self):
        self.icon = create_image(64, 64, 'green', 'white')
        self.tray_icon = TrayIcon(self)
        self.tray = Thread(target=self.tray_icon.run)
        self.home = Home(self)

        self.finished = False
        self.exiting = False

    def run(self):
        print(f'lanku v{__version__}')
        try:
            self.tray.start()
            self.show_hide()
            pyglet.app.run()
            self.finished = True

        except KeyboardInterrupt:
            pass

        finally:
            self.quit()
            self.tray.join()

    def show_hide(self):
        if self.home.minimized:
            self.home.set_visible(True)

        else:
            self.home.set_visible(not self.home.visible)
            #if self.home.visible:
            #    self.home.set_location(100, 100)

    def quit(self):
        if self.exiting: return
        self.exiting = True
        print('quit')

        self.tray_icon.stop()

        if not self.finished:
            self.home.save()

        pyglet.app.exit()


def create_image(width, height, color1, color2):
    image = Image.new('RGBA', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)

    return image


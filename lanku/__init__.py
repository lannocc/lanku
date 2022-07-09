from .__version__ import __version__
from .home import Window as Home
from .node import Client as Node
from .peer import Master as Peer
from .systray import Icon as TrayIcon

import lank.name
import pyglet.app
from PIL import Image, ImageDraw

from threading import Thread
import sys


#icon.notify('this is a test', 'lanku alert')


class Application:
    def __init__(self):
        self.icon = create_image(64, 64, 'green', 'white')
        self.tray_icon = TrayIcon(self)
        self.tray_thread = Thread(target=self.tray_icon.run)

        self.node = None

        self.home = Home(self)

        self.finished = False
        self.exiting = False

    def run(self):
        print(f'lanku v{__version__}')
        try:
            self.tray_thread.start()
            self.show_hide()
            pyglet.app.run()
            self.finished = True

        except KeyboardInterrupt:
            pass

        finally:
            self.quit()
            self.tray_thread.join()

    def show_hide(self):
        if self.home.minimized:
            self.home.set_visible(True)

        else:
            self.home.set_visible(not self.home.visible)

    def quit(self):
        if self.exiting: return
        self.exiting = True
        print('quit')

        self.tray_icon.stop()

        if not self.finished:
            self.home.save()

        self.disconnect()
        pyglet.app.exit()

    def connect(self):
        print('connecting')
        #print(f'pass: {self.home.pnl_config.pwd.value}')

        self.node = Node(self)
        self.node.start()

    def disconnect(self):
        if not self.node: return
        print('disconnecting')
        node = self.node
        self.node = None
        node.stop()
        node.join()
        print('finished')

    def notify(self, signed):
        if signed.name == lank.name.REGISTER:
            self.tray_icon.notify(
                f'{signed.label} has changed keys.',
                f'{signed.label} | lanku')

        elif signed.name == lank.name.PEER:
            self.tray_icon.notify(
                f'{signed.label} has signed on.',
                f'{signed.label} | lanku')

        else:
            self.tray_icon.notify(
                f'{signed.label} has done something.',
                f'{signed.label} | lanku')


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


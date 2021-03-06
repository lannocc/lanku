from .__version__ import __version__
from .home import Window as Home
from .node import Client as Node
from .peer import Master as Peer

import lank.name
import pyglet.app
from PIL import Image, ImageDraw

from threading import Thread
import sys


class Application:
    def __init__(self):
        print(f'lanku v{__version__}')
        self.icon = create_image(64, 64, 'green', 'white')
        try:
            from .systray import Icon as TrayIcon
            self.tray_icon = TrayIcon(self)
            self.tray_thread = Thread(target=self.tray_icon.run)

        except Exception as e:
            em = str(e)
            if not em: em = type(e)
            print(f'WARNING - Unable to setup system tray icon: {em}')
            self.tray_icon = None
            self.tray_thread = None

        self.node = None

        self.home = Home(self)

        self.finished = False
        self.exiting = False

    def run(self):
        try:
            if self.tray_thread:
                self.tray_thread.start()
            self.show_hide()
            pyglet.app.run()
            self.finished = True

        except KeyboardInterrupt:
            pass

        finally:
            self.quit()
            if self.tray_thread:
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

        if self.tray_icon:
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
            self._notify_(signed.label, f'{signed.label} has changed keys.')

        elif signed.name == lank.name.PEER:
            msg = f'{signed.label} signed on'
            if ':' in signed.key[signed.key.index(':')+1:]:
                alias = signed.key[signed.key.index(':')+1:]
                alias = alias[alias.index(':')+1:]
                msg += f' as {alias}'
            msg += '.'
            self._notify_(signed.label, msg)

        else:
            self._notify_(signed.label, f'{signed.label} has done something.')

    def _notify_(self, title, msg):
        if self.tray_icon:
            self.tray_icon.notify(msg, f'{title} | lanku')

        else:
            print(f'@@ NOTICE [{title}] @@')
            print(f'   >>   {msg}')


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


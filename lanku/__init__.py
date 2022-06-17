from .__version__ import __version__

import pyglet
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

import threading


def quit():
    pyglet.app.exit()
    icon.stop()


def create_image(width, height, color1, color2):
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)

    return image


icon = Icon(
    'lanku',
    icon=create_image(64, 64, 'green', 'white'),
    menu=Menu(
        MenuItem(
            'With submenu',
            Menu(
                MenuItem(
                    'Submenu item 1',
                    lambda icon, item: 1),
                MenuItem(
                    'Submenu item 2',
                    lambda icon, item: 2))),
        MenuItem('Quit', quit)))
#icon.run_detached()
tray = threading.Thread(target=icon.run)
tray.start()

print('hello?')


class Main(pyglet.window.Window):
    def __init__(self):
        super().__init__()

        image = create_image(32, 32, 'green', 'red')
        self.set_icon(pyglet.image.ImageData(image.width, image.height, 'RGB',
            image.tobytes(), pitch=-image.width*3))

        self.label = pyglet.text.Label('Hello, world!')

    def run(self):
        pyglet.app.run()

    def on_draw(self):
        self.clear()
        self.label.draw()

    def on_close(self):
        icon.stop()
        super().on_close()


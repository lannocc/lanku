from .__version__ import __version__

import pyglet


class Main(pyglet.window.Window):
    def __init__(self):
        super().__init__()

        self.label = pyglet.text.Label('Hello, world!')

    def run(self):
        pyglet.app.run()

    def on_draw(self):
        self.clear()
        self.label.draw()


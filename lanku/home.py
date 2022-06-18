from . import __version__
from .ui import *


class Window(LWin):
    def __init__(self, app):
        super().__init__(app, 'lanku', 333, 555, save_name='home')

        self.label = Label(f'lanku v{__version__}')


from . import __version__
from .ui import *


class Window(LWin):
    def __init__(self, app):
        super().__init__(app, 'lanku', 333, 555, save_name='home')

        self.lbl_version = Label(f'lanku v{__version__}', batch=self.batch)

        self.tabs = TabGroup()
        self.frame.add_widget(Tab(self.tabs,
            10, 50,
            image('tab_peers-pushed.png'),
            image('tab_peers.png'),
            image('tab_peers-hover.png'),
            batch=self.batch))
        self.frame.add_widget(Tab(self.tabs,
            100, 50,
            image('tab_nodes-pushed.png'),
            image('tab_nodes.png'),
            image('tab_nodes-hover.png'),
            batch=self.batch))


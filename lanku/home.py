from . import __version__
from .ui import *


class Window(LWin):
    def __init__(self, app):
        super().__init__(app, 'lanku', 333, 555, save_name='home')

        Label(self, 3, 3, f'lanku v{__version__}')

        self.tabs = TabGroup(self, 40, 60, 200, 500)
        self.tabs.tab(
            Peers(self.tabs),
            image('tab_peers.png'),
            image('tab_peers-active.png'),
            image('tab_peers-hover.png'))
        self.tabs.tab(
            Nodes(self.tabs),
            image('tab_nodes.png'),
            image('tab_nodes-active.png'),
            image('tab_nodes-hover.png'))

class Peers(Component):
    def __init__(self, parent):
        super().__init__(parent, 0, 0)

        Label(self, 3, 3, f'PEERS')


class Nodes(Component):
    def __init__(self, parent):
        super().__init__(parent, 0, 0)

        Label(self, 3, 3, f'NODES')


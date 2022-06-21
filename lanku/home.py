from . import __version__
from .ui import *


class Window(LWin):
    def __init__(self, app):
        super().__init__(app, 'lanku', 333, 555, save_name='home')
        self.set_minimum_size(250, 250)

        Label(self, 3, 3, f'lanku v{__version__}')

        self.tabs = TabGroup(self, 20, 60, self.xywh[2]-40, self.xywh[3]-100)
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

        self.btn_connect = ToggleButton(self,
            self.xywh[2] / 2 - 58, self.xywh[3] - 35,
            image('btn_connect.png'),
            image('btn_connect-push.png'),
            image('btn_connect-hover.png'),
            image('btn_disconnect.png'),
            image('btn_disconnect-push.png'),
            image('btn_disconnect-hover.png'))

    def on_resize(self, w, h):
        super().on_resize(w, h)
        self.tabs.set_size(w-40, h-100)
        self.btn_connect.set_pos(w / 2 - 58, h - 35)


class Peers(Component):
    def __init__(self, parent):
        super().__init__(parent, 0, 0)

        Label(self, 3, 3, f'PEERS')


class Nodes(Component):
    def __init__(self, parent):
        super().__init__(parent, 0, 0)

        Label(self, 3, 3, f'NODES')


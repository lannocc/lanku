from . import __version__
from .ui import *

import lank.node
import lank.peer


class Window(LWin):
    def __init__(self, app):
        super().__init__(app, 'lanku', 333, 555, save_name='home')
        self.set_minimum_size(300, 250)

        Label(self, 3, 3, f'lanku v{__version__}')

        self.tabs = TabGroup(self, 20, 60, self.xywh[2]-40, self.xywh[3]-100)
        self.pnl_peers = Peers(self.tabs)
        self.pnl_labels = Labels(self.tabs)
        self.pnl_config = Config(self.tabs)

        self.tabs.tab(self.pnl_peers,
            image('tab_peers.png'),
            image('tab_peers-active.png'),
            image('tab_peers-hover.png'))
        self.tabs.tab(self.pnl_labels,
            image('tab_labels.png'),
            image('tab_labels-active.png'),
            image('tab_labels-hover.png'))
        self.tabs.tab(self.pnl_config,
            image('tab_config.png'),
            image('tab_config-active.png'),
            image('tab_config-hover.png')).select()

        self.btn_connect = ToggleButton(self,
            self.xywh[2] / 2 - 58, self.xywh[3] - 35,
            image('btn_connect.png'),
            image('btn_connect-push.png'),
            image('btn_connect-hover.png'),
            image('btn_disconnect.png'),
            image('btn_disconnect-push.png'),
            image('btn_disconnect-hover.png'))
        self.btn_connect.on_toggle = self.on_connect_toggle

    def on_resize(self, w, h):
        super().on_resize(w, h)
        self.tabs.set_size(w-40, h-100)
        self.btn_connect.set_pos(w / 2 - 58, h - 35)

    def on_connect_toggle(self, toggled):
        if toggled:
            self.app.connect()

        else:
            self.app.disconnect()


class Peers(Component):
    def __init__(self, parent):
        super().__init__(parent, 0, 0)

        Label(self, 3, 3, f'PEERS')


class Labels(Component):
    def __init__(self, parent):
        super().__init__(parent, 0, 0)

        self.labels = [ ]
        #self.refresh_labels(['foo', 'bar'])

    def refresh_labels(self, labels=None):
        clock.schedule_once(self._refresh_labels_, 0, labels)

    def _refresh_labels_(self, dt, labels=None):
        for button, label in self.labels:
            button.remove()
            label.delete()

        self.labels = [ ]

        if labels:
            y = 30
            for label in labels:
                def toggle(label):
                    def toggle(toggled):
                        if self.win.app.node:
                            self.win.app.node.notify(label, toggled)
                    return toggle

                btn = ToggleButton(self, 3, y,
                    image('btn_bell.png'),
                    image('btn_bell-push.png'),
                    image('btn_bell-hover.png'),
                    image('btn_bell-push.png'),
                    image('btn_bell-hover.png'),
                    image('btn_bell-push.png'))
                btn.on_toggle = toggle(label)

                self.labels.append((btn, Label(self, 33, y+7, label)))
                y += 30


class Config(Component):
    NODE_HOST = 'localhost'
    NODE_PORT = lank.node.DEFAULT_PORT
    PEER_PORT = lank.peer.DEFAULT_PORT

    def __init__(self, parent):
        super().__init__(parent, 0, 0)

        y = 180
        #Label(self, 5, y, 'Node Host:')
        #self.node_host = TextEntry(self, 100, y, 150, self.NODE_HOST)
        y -= 40
        #Label(self, 5, y, 'Node Port:')
        #self.node_port = TextEntry(self, 100, y, 75, str(self.NODE_PORT))
        y -= 40
        Label(self, 5, y, 'Local Port:')
        self.peer_port = TextEntry(self, 100, y, 75, str(self.PEER_PORT))
        y -= 40
        Label(self, 5, y, 'Label:')
        self.label = TextEntry(self, 100, y, 150)
        y -= 40
        Label(self, 5, y, 'Password:')
        self.pwd = TextEntry(self, 100, y, 150, mask='*')


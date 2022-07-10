from ..ui import *
from .link import Window as Link


class Panel(Component):
    def __init__(self, parent):
        super().__init__(parent, 0, 0)

        self.peers = { }

    def add_peer(self, label):
        if label in self.peers:
            self.peers[label][0] = True

        else:
            self.peers[label] = [True, None]

        self.refresh_peers()

    def del_peer(self, label):
        if label not in self.peers:
            return

        self.peers[label][0] = False
        self.refresh_peers()

    def refresh_peers(self):
        clock.schedule_once(self._refresh_peers_, 0)

    def _refresh_peers_(self, dt):
        y = 30
        for name, data in self.peers.items():
            keep = data[0]
            widgets = data[1]

            if widgets:
                widgets[0].delete()
                widgets[1].remove()
                #widgets[2].remove()
                data[1] = None

            if keep:
                def link_push(peers, name):
                    def pusher():
                        peers[name][1][2].set_visible(True)

                    return pusher

                btn_link = Button(self, 10, y,
                    image('btn_link.png'),
                    image('btn_link-push.png'),
                    image('btn_link-hover.png'))
                btn_link.on_press = link_push(self.peers, name)

                data[1] = [
                    Label(self, 40, y+8, name),
                    btn_link,
                    Link(self.win.app, name)
                ]
                y += 30


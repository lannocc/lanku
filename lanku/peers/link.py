from ..ui import *

import lank.name


class Window(LWin):
    def __init__(self, app, label):
        super().__init__(app, f'Link to {label} | lanku', 700, 300, 'link')
        self.label = label

        self.items = [ ]

    def on_show(self):
        super().on_show()
        self.app.node.get_history(self.label, self.refresh)

    def refresh(self, history):
        clock.schedule_once(self._refresh_, 0, history)

    def _refresh_(self, dt, history):
        for item in self.items:
            if item[0]: item[0].remove()
            item[1].delete()

        self.items = [ ]
        y = 3

        for item in history.items:
            dt = item._to_datetime_(item.timestamp).astimezone().strftime(
                '%a, %d %b %Y @ %I:%M %p')

            if item.name == lank.name.REGISTER:
                self.items.append((None, Label(self, 130, y+5,
                    f'{dt}: Created new key-pair')))

            elif item.name == lank.name.PEER:
                msg = f'{dt}: Signed on'
                if ':' in item.key[item.key.index(':')+1:]:
                    alias = item.key[item.key.index(':')+1:]
                    alias = alias[alias.index(':')+1:]
                    msg += f' as {alias}'
                msg += f' at {item.address}'
                self.items.append((
                    Button(self, 3, y,
                        image('btn_connect.png'),
                        image('btn_connect-push.png'),
                        image('btn_connect-hover.png')),
                    Label(self, 130, y+5, msg)))

            else:
                self.items.append((None, Label(self, 3, y+5,
                    f'{dt}: Did something')))

            y += 30

        clock.schedule_once(self.null, 0.1)

    def null(self, dt):
        self.place()


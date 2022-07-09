from ..ui import *


class Panel(Component):
    def __init__(self, parent):
        super().__init__(parent, 0, 0)

        Label(self, 3, 3, f'PEERS')


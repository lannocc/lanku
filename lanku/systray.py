from pystray import Icon as Base, Menu, MenuItem


class Icon(Base):
    def __init__(self, app):
        self.app = app

        super().__init__(
            'lanku',
            icon=app.icon,
            menu=Menu(
                #MenuItem(
                #    'With submenu',
                #    Menu(
                #        MenuItem(
                #            'Submenu item 1',
                #            lambda icon, item: 1
                #        ),
                #        MenuItem(
                #            'Submenu item 2',
                #            lambda icon, item: 2
                #        )
                #    )
                #),
                MenuItem('Show / Hide', self.app.show_hide, default=True),
                MenuItem('Quit', self.app.quit)
            )
        )


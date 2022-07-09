from lank.peer import Master as Base
from lank.crypto import get_handler as get_crypto
from requests import get
#from miniupnpc import UPnP


class Master(Base):
    def __init__(self, app):
        super().__init__(int(app.home.pnl_config.peer_port.value))
        self.app = app

    def get_public_ip(self):
        return get('https://api.ipify.org').content.decode('utf-8')

    '''
    def upnp(self):
        upnp = UPnP()
        upnp.discoverdelay = 10
        upnp.discover()
        upnp.selectigd()
        upnp.addportmapping(self.port, 'TCP', upnp.lanaddr,
                            self.port, 'lanku', '')
    '''


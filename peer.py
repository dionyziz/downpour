import random

# one of our remote peers to whom we can upload or download from
class Peer:
    IP = '0.0.0.0'
    id = ''
    port = 0
    chocked = True
    interested = False
    connected = False
    clientName = 'Unknown'
    clientVersion = ''
    has = []
    local = True

    def __generateId( self ):
        self.id = "".join( map( chr, [ random.randint( 0, 255 ) for i in range( 0, 20 ) ] ) )
    def __init__( self, ip = None, port = None ):
        if ip is None:
            self.local = True
            self.__generateId()
        else:
            self.local = False
            self.ip = ip
        if port is not None:
            self.port = port


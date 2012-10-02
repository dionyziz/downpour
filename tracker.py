import log
import utilities

class Tracker:
    URL = ''
    host = '0.0.0.0'
    port = 0
    protocol = '' # http, udp, ...
    supported = False
    announceRequestURI = ''
    scrapeRequestURI = ''
    scrapeSupport = False
    id = ''
    seedersCount = 0
    leechersCount = 0

    def __init__( self, URL, info_hash, peer_id ):
        self.__parseURL( URL )
    def announceRequest( self ):
        pass
    def __protocolSupported( self, protocol ):
        return protocol == 'http'
    def __protocolPort( self, protocol ):
        if protocol == 'http':
            return 80
        raise NameError( 'Protocol "%s" is not supported.' % protocol )
    def __URLparts( self, URL ):
        pos = URL.index( ':' )
        protocol = URL[ 0:pos ]
        # remove the protocol part from the URL
        URL = URL[ ( pos + len( '://' ) ): ]
        pos = URL.index( '/' )
        host = URL[ :pos ]
        # remove the host:port part of the URL
        URL = URL[ pos: ] 
        port = 0

        if ':' in host:
            ( host, port ) = host.split( ':', 2 )

        try:
            port = int( port )
        except ValueError:
            log.warning( 'Tracker "%s" uses non-numeric port "%s". Using default port.' % ( URL, port ) )
            port = 0

        if port <= 0 or port > 65535:
            log.warning( 'Tracker "%s" uses invalid port number "%i". Using default port.' % ( URL, port ) )
            port = 0

        return ( protocol, host, port, URL )
    def __parseURL( self, URL ):
        self.URL = URL
        ( self.protocol, self.host, self.port, self.announceRequestURI ) = self.__URLparts( URL )

        try:
            defaultPort = self.__protocolPort( self.protocol )
        except NameError:
            log.warning( 'Tracker "%s" is using unsupported protocol "%s".' % ( URL, self.protocol ) )
            return

        if self.port == 0:
            self.port = defaultPort
        self.supported = True
        pos = self.announceRequestURI.rindex( '/' )
        
        lastPart = self.announceRequestURI[ ( pos + 1 ): ]
        if lastPart.find( 'announce' ) == 0:
            self.scrapeRequestURI = 'scrape' + lastPart.split( 'announce', 2 )[ 1 ]
            self.scrapeSupport = True

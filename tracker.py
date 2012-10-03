import log
import utilities
import urllib, urllib2
import urlparse
import bencoding
import struct

class TrackerException( Exception ):
    pass

class TrackerTimeoutException( TrackerException ):
    pass

# a torrent tracker (http support only)
class Tracker:
    NUM_WANT = 30
    HTTP_TIMEOUT = 5

    URL = ''
    URLParse = ''

    supported = False
    announceRequestURI = ''
    scrapeRequestURI = ''
    scrapeSupport = False
    id = ''
    seedersCount = 0
    leechersCount = 0
    torrent = None
    interval = 0
    peers = [] # array of ( ip, port ) tuples

    __trackerId = None

    def __init__( self, URL, torrent ):
        self.URL = URL
        self.__parseURL( URL )
        self.torrent = torrent
    def announceRequest( self ):
        getParams = {
            'info_hash': self.torrent.dotTorrent.infoHash,
            'peer_id': self.torrent.localPeer.id,
            'port': 16885,
            'uploaded': self.torrent.bytesUploaded,
            'downloaded': self.torrent.bytesDownloaded,
            'left': self.torrent.bytesLeft,
            'compact': 1,
            # 'no_peer_id': 0,
            'event': 'started',
            # 'ip': '127.0.0.1',
            'num_want': self.NUM_WANT,
            # 'key':,
        }
        if self.__trackerId is not None:
            getParams[ 'trackerid' ] = self.__trackerId
        url = urlparse.urlunparse( (
            self.URLParse.scheme,
            self.URLParse.netloc,
            self.URLParse.path,
            self.URLParse.params,
            urllib.urlencode(
                urlparse.parse_qsl( self.URLParse.query )
              + getParams.items()
            ),
            self.URLParse.fragment
        ) )
        log.info( 'Requesting announce: %s' % ( url ) )
        f = urllib2.urlopen( url, None, self.HTTP_TIMEOUT )
        try:
            pass
        except urllib2.HTTPError as e:
            log.warning( 'Tracker HTTP error ' + str( e.code ) )
            raise TrackerException
        except urllib2.URLError:
            raise TrackerTimeoutException

        self.__parseAnnounceResponse( f.read() )
    def __parseAnnounceResponse( self, response ):
        response = bencoding.decode( response )
        if 'failure reason' in response:
            log.error( 'Tracker announce request failed: %s' % ( response[ 'failure reason' ] ) )
            raise TrackerException
        if 'warning message' in response:
            log.warning( 'Tracker announce warning: %s' % ( response[ 'warning message' ] ) )
        self.seedersCount = response[ 'complete' ]
        self.leechersCount = response[ 'incomplete' ]
        if 'tracker id' in response:
            self.__trackerId = response[ 'tracker id' ]
        self.__parsePeers( response[ 'peers' ] )
    def __parsePeers( self, peers ):
        assert( len( peers ) % 6 == 0 )

        for i in range( 0, len( peers ), 6 ):
            self.__parsePeer( peers[ i:( i + 6 ) ] )
    def __parsePeer( self, peer ):
        ip = [ 0, 0, 0, 0 ]
        ( ip[ 0 ], ip[ 1 ], ip[ 2 ], ip[ 3 ] ) = struct.unpack( '!BBBB', peer[ :4 ] )
        port = struct.unpack( '!H', peer[ 4: ] )[ 0 ]
        ip = '.'.join( map( str, ip ) )
        self.peers.append( ( ip, port ) )
    def __protocolSupported( self, protocol ):
        return protocol == 'http' or protocol == 'https'
    def __parseURL( self, URL ):
        self.URLParse = urlparse.urlparse( URL )

        if not self.__protocolSupported( self.URLParse.scheme ):
            log.warning( 'Tracker "%s" is using unsupported protocol "%s".' % ( URL, self.URLParse.scheme ) )
            return

        self.supported = True
        pos = self.URLParse.path.rindex( '/' )
        
        lastPart = self.URLParse.path[ ( pos + 1 ): ]
        if lastPart.find( 'announce' ) == 0:
            self.scrapeRequestURI = 'scrape' + lastPart.split( 'announce', 2 )[ 1 ]
            self.scrapeSupport = True

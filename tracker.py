import log
import utilities
import urllib, urllib2
import urlparse
import bencoding

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

    __trackerId = None

    def __init__( self, URL, torrent ):
        self.URL = URL
        self.__parseURL( URL )
        self.torrent = torrent
    def announceRequest( self ):
        getParams = {
            'info_hash': self.torrent.dotTorrent.infoHash,
            'peer_id': self.torrent.me.id,
            'port': 6885,
            'uploaded': self.torrent.bytesUploaded,
            'downloaded': self.torrent.bytesDownloaded,
            'left': self.torrent.bytesLeft,
            # 'compact': 0,
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
        try:
            f = urllib2.urlopen( url, None, self.HTTP_TIMEOUT )
        except urllib2.HTTPError:
            raise TrackerException
        except urllib2.URLError:
            raise TrackerTimeoutExeption

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
    def __protocolSupported( self, protocol ):
        return protocol == 'http'
    def __protocolPort( self, protocol ):
        if protocol == 'http':
            return 80
        raise NameError( 'Protocol "%s" is not supported.' % protocol )
    def __parseURL( self, URL ):
        self.URLParse = urlparse.urlparse( URL )

        if not self.__protocolSupported( self.URLParse.scheme ):
            log.warning( 'Tracker "%s" is using unsupported protocol "%s".' % ( URL, self.URLParse.scheme ) )
            return

        self.supported = True
        pos = self.URLParse.path.rindex( '/' )
        
        lastPart = self.announceRequestURI[ ( pos + 1 ): ]
        if lastPart.find( 'announce' ) == 0:
            self.scrapeRequestURI = 'scrape' + lastPart.split( 'announce', 2 )[ 1 ]
            self.scrapeSupport = True

from dottorrent import DotTorrent
from tracker import Tracker
import log

class Piece:
    byteSize = 0
    sha1 = 0

class Block:
    pass

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

    def __init__( self ):
        pass

class File:
    byteSize = 0
    path = ''
    md5 = ''

class Torrent:
    trackers = []
    tracker = None
    seedersCount = 0
    leechersCount = 0
    files = []
    peers = []
    me = Peer()

    def __init__( self, torrentFileName ):
        dotTorrent = DotTorrent( torrentFileName )
        if not dotTorrent.valid:
            log.error( 'No torrent files found. Bailing out.' )
            return

        hasTrackers = False
        for url in dotTorrent.trackerURLs:
            tracker = Tracker( url )
            if tracker.supported:
                self.trackers.append( tracker )
                hasTrackers = True
        log.info( 'Found %i supported trackers: ' % ( len( self.trackers ) ) )
        for tracker in self.trackers:
            log.info( tracker.URL )

        if not hasTrackers:
            log.error( 'No supported trackers found for torrent. Aborting.' )
            return

        self.tracker = self.trackers[ 0 ]
        log.info( 'Using tracker: ' + self.tracker.URL )
        self.tracker.request()
    def beginDownload(): 
        pass

Torrent( 'example2.torrent' )

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

class File:
    byteSize = 0
    path = ''
    md5 = ''

class Torrent:
    trackers = []
    seedCount = 0
    peerCount = 0
    files = []

    def __init__( self, torrentFileName ):
        example = DotTorrent( torrentFileName )
        hasTrackers = False
        for url in example.trackerURLs:
            tracker = Tracker( url )
            if tracker.supported:
                self.trackers.append( tracker )
                hasTrackers = True
        if not hasTrackers:
            log.error( 'No supported trackers found for torrent. Aborting.' )
    def beginDownload(): 
        pass

Torrent( 'example.torrent' )

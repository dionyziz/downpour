from dottorrent import DotTorrent
from tracker import Tracker
from peer import Peer
import log
import random
import utilities

class Piece:
    byteSize = 0
    sha1 = 0

class Block:
    pass

# a torrent download
class Torrent:
    # list of tracker objects
    trackers = []
    # the tracker object that we're currently utilizing
    tracker = None
    seedersCount = 0
    leechersCount = 0
    files = []
    peers = []
    me = Peer()
    bytesLeft = 0
    bytesDownloaded = 0
    bytesUploaded = 0
    # an object representing the metainfo file used to initiate this torrent
    dotTorrent = None

    def __init__( self, torrentFileName ):
        log.info( 'Loading torrent file "%s"' % torrentFileName )
        self.dotTorrent = DotTorrent( torrentFileName )
        log.info( 'Torrent "%s" loaded.' % self.dotTorrent.name )
        if not self.dotTorrent.valid:
            log.error( 'No valid torrent files found. Bailing out.' )
            return
        if self.dotTorrent.createdBy is not None:
            log.info( 'Torrent created by "%s"' % self.dotTorrent.createdBy )
        if self.dotTorrent.creationDate is not None:
            log.info( 'Torrent created on %s' % self.dotTorrent.creationDate )
        if self.dotTorrent.comment is not None:
            log.info( '(Torrent creator comment: "%s")' % self.dotTorrent.comment )

        if len( self.dotTorrent.files ) == 1:
            fiels = 'file'
        else:
            files = 'files'

        if self.dotTorrent.singleFile:
            log.info( 'Entering single file mode.' )
        else:
            log.info( 'Entering multi file mode.' )

        log.info( 'Found %i %s to download:' % ( len( self.dotTorrent.files ), files ) ) 

        for file in self.dotTorrent.files:
            log.info( ' - %s (%s)' % ( '/'.join( file.path ), utilities.humanFileSize( file.byteSize ) ) )

        hasTrackers = False
        for url in self.dotTorrent.trackerURLs:
            tracker = Tracker( url, self )
            if tracker.supported:
                self.trackers.append( tracker )
                hasTrackers = True
        log.info( 'Found %i supported trackers: ' % ( len( self.trackers ) ) )
        for tracker in self.trackers:
            log.info( tracker.URL )

        if not hasTrackers:
            log.error( 'No supported trackers found for torrent. Aborting.' )
            return

        trackerFound = False
        while not trackerFound:
            self.tracker = random.choice( self.trackers )
            log.info( 'Using tracker: ' + self.tracker.URL )
            log.info( 'Making tracker announce request' )
            try:
                self.tracker.announceRequest()
                trackerFound = True
            except TrackerTimeoutException:
                log.warning( 'Tracker request timed out.' )
            except TrackerException:
                log.warning( 'Tracker error.' )
        log.info( 'Seeders: %i' % self.tracker.seedersCount )
        log.info( 'Leechers: %i' % self.tracker.leechersCount )
    def beginDownload(): 
        pass

Torrent( 'crysis.torrent' )

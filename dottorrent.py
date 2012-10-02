import bencoding
import os 
import utilities
import datetime
import log

class DotTorrent:
    filename = ''
    byteSize = 0

    trackerURLs = set()
    creationDate = ''
    comment = ''
    createdBy = ''
    encoding = ''
    pieceLength = 0
    pieces = {}
    private = 0
    valid = False

    def __init__( self, filename ):
        self.filename = filename
        try:
            self.byteSize = os.path.getsize( filename )
            f = open( filename, 'r' )
            data = f.read()
        except:
            log.error( 'Could not open torrent file "%s". File does not exist or is not readable.' % filename )
            return
        metainfo = self.__parse( data )
        self.__populate( metainfo )
        self.valid = True
    def __parse( self, data ):
        return bencoding.decode( data )
    def __populate( self, metainfo ):
        # a torent file may have a single tracker, multiple trackers,
        # or both a reference to a single tracker and multiple trackers (for backwards compatibility)
        if 'announce' in metainfo:
            # single tracker
            self.trackerURLs.add( metainfo[ 'announce' ] )
        if 'announce-list' in metainfo:
            # multiple trackers
            self.trackerURLs |= set( utilities.flatten( metainfo[ 'announce-list' ] ) )
        if 'created by' in metainfo:
            self.createdBy = metainfo[ 'created by' ]
        if 'comment' in metainfo:
            self.comment = metainfo[ 'comment' ]
        if 'encoding' in metainfo:
            self.encoding = metainfo[ 'encoding' ]
        if 'creation date' in metainfo:
            self.creationDate = datetime.datetime.fromtimestamp( metainfo[ 'creation date' ] )

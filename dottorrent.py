import bencoding
import os 
import utilities

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

    def __init__( self, filename ):
        self.filename = filename
        self.byteSize = os.path.getsize( filename )
        f = open( filename, 'r' )
        data = f.read()
        metainfo = self.__parse( data )
        self.__populate( metainfo )
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

print( DotTorrent( 'example.torrent' ).trackerURLs )

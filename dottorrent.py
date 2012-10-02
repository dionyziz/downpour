import bencoding
import os 
import utilities
import datetime
import log
from file import File

# represents a .torrent metainfo file loaded into memory
class DotTorrent:
    filename = ''
    byteSize = 0

    trackerURLs = set()
    creationDate = None
    comment = None
    createdBy = None
    encoding = ''
    pieceLength = 0
    pieces = {}
    private = 0
    valid = False
    name = ''
    files = []
    singleFile = True

    infoHash = ''

    __parseDepth = 0
    __parseInInfo = False
    __parseInfoFound = False
    __parseInfoBegin = 0
    __parseInfoEnd = 0

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
    # we need to look for the position of the info dictionary within the bencoded data
    # we can achieve this using bencoding callbacks to get the appropriate offsets
    def __parseBegin( self, what, offset ):
        if self.__parseInInfo:
            self.__parseDepth += 1
    def __parseEnd( self, what, offset, value ):
        if self.__parseInInfo:
            self.__parseDepth -= 1
            if self.__parseDepth == 0:
                self.__parseInInfo = False
                self.__parseInfoFound = True
                self.__parseInfoEnd = offset
        else:
            if what == 'key' and value == 'info' and not self.__parseInfoFound:
                self.__parseInInfo = True
                self.__parseInfoBegin = offset
    def __parse( self, data ):
        decoder = bencoding.Decoder()
        decoder.setCallback( self.__parseBegin, self.__parseEnd )
        decoded = decoder.decode( data )
        self.infoHash = utilities.sha1( data[ self.__parseInfoBegin:self.__parseInfoEnd ] )
        return decoded
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
        if 'files' in metainfo[ 'info' ]:
            # multi file mode
            self.singleFile = False
            self.name = metainfo[ 'info' ][ 'name' ]
            self.files = []
            for file in metainfo[ 'info' ][ 'files' ]:
                self.files.append( File( file[ 'path' ], file[ 'length' ] ) )
        if 'length' in metainfo[ 'info' ]:
            # single file mode
            self.singleFile = True
            self.name = metainfo[ 'info' ][ 'name' ]
            self.files = [ File( [ metainfo[ 'info' ][ 'name' ] ], metainfo[ 'info' ][ 'length' ] ) ]

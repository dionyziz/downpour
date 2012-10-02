# a file within a torrent
class File:
    byteSize = 0
    path = ''
    md5 = ''

    def __init__( self, path, byteSize ):
        self.byteSize = byteSize
        self.path = path

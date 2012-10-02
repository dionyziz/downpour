import hashlib

def flatten( l ):
    return [ item for sublist in l for item in sublist ]

def sha1( string ):
    h = hashlib.new( 'sha1' )
    h.update( string )
    return h.digest()

# code from http://stackoverflow.com/a/1094933/126342
def humanFileSize( num ):
    for x in [ 'bytes','KB','MB','GB' ]:
        if num < 1024.0 and num > -1024.0:
            return "%3.1f%s" % ( num, x )
        num /= 1024.0
    return "%3.1f%s" % ( num, 'TB' )

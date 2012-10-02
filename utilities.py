def flatten( l ):
    return [ item for sublist in l for item in sublist ]

def beginsWith( haystack, needle ):
    return haystack[ :len( needle ) ] == needle

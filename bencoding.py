def decode( data ):
    def decode_one( data ):
        if data[ 0 ] == 'i':
            # data is an integer
            pos = data.index( 'e' )
            return ( int( data[ 1:pos ] ), data[ ( pos + 1 ): ] )
        if data[ 0 ] == 'l':
            # data is a list
            data = data[ 1: ]
            l = []
            while data[ 0 ] != 'e':
                ( item, data ) = decode_one( data )
                l.append( item )
            return ( l, data[ 1: ] )
        if data[ 0 ] == 'd':
            # data is a dictionary
            data = data[ 1: ]
            d = {}
            while data[ 0 ] != 'e':
                ( key, data ) = decode_one( data )
                ( value, data ) = decode_one( data )
                d[ key ] = value
            return ( d, data[ 1: ] )
        # default case: data is a string
        pos = data.index( ':' )
        length = int( data[ 0:pos ] )
        data = data[ ( pos + 1 ): ]
        return ( data[ 0:length ], data[ length: ] )
    return decode_one( data )[ 0 ]

def encode( data ):
    if type( data ) is str:
        return str( len( data ) ) + ':' + data
    if type( data ) is int:
        return 'i' + str( data ) + 'e'
    if type( data ) is list:
        return 'l' + ''.join( map( encode, data ) ) + 'e'
    if type( data ) is dict:
        flattened = [ item for sublist in data.items() for item in sublist ]
        encoded = map( encode, flattened )
        joined = ''.join( encoded )
        return 'd' + joined + 'e'

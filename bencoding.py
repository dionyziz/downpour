import utilities

class Decoder:
    offset = 0
    beginCallback = None
    endCallback = None

    def __begin( self, what, offset ):
        if self.beginCallback is not None:
            self.beginCallback( what, offset )
    def __end( self, what, offset, value ):
        if self.endCallback is not None:
            self.endCallback( what, offset, value )
    def setCallback( self, begin, end ):
        self.beginCallback = begin
        self.endCallback = end
    def decode( self, data ):
        self.offset = 0
        def decode_one( data ):
            if data[ 0 ] == 'i':
                # data is an integer
                self.__begin( 'integer', self.offset )
                self.offset += 1
                data = data[ 1: ]
                pos = data.index( 'e' )
                value = int( data[ 0:pos ] )
                self.offset += pos + 1
                data = data[ ( pos + 1 ): ]
                self.__end( 'integer', self.offset, value )
                return ( value, data )
            if data[ 0 ] == 'l':
                # data is a list
                self.__begin( 'list', self.offset )
                self.offset += 1
                data = data[ 1: ]
                value = []
                while data[ 0 ] != 'e':
                    ( item, data ) = decode_one( data )
                    value.append( item )
                self.offset += 1
                data = data[ 1: ]
                self.__end( 'list', self.offset, value )
                return ( value, data )
            if data[ 0 ] == 'd':
                # data is a dictionary
                self.__begin( 'dictionary', self.offset )
                self.offset += 1
                data = data[ 1: ]
                d = {}
                while data[ 0 ] != 'e':
                    self.__begin( 'key', self.offset )
                    ( key, data ) = decode_one( data )
                    self.__end( 'key', self.offset, key )
                    self.__begin( 'value', self.offset )
                    ( value, data ) = decode_one( data )
                    self.__end( 'value', self.offset, value )
                    d[ key ] = value
                self.offset += 1
                data = data[ 1: ]
                self.__end( 'dictionary', self.offset, d ) 
                return ( d, data )
            # default case: data is a string
            self.__begin( 'string', self.offset )
            pos = data.index( ':' )
            length = int( data[ :pos ] )
            self.offset += pos + 1
            data = data[ ( pos + 1 ): ]
            value = data[ 0:length ]
            self.offset += length
            data = data[ length: ]
            self.__end( 'string', self.offset, value )
            return ( value, data )
        return decode_one( data )[ 0 ]

def decode( data ):
    # def begin( what, offset ):
    #     print( "Starting %s at %i." % ( what, offset ) )
    # def end( what, offset, value ):
    #     print( "Ending %s with value '%s' at %i." % ( what, value, offset ) )
    decoder = Decoder()
    # decoder.setCallback( begin, end )
    return decoder.decode( data )

def encode( data ):
    if type( data ) is str:
        return str( len( data ) ) + ':' + data
    if type( data ) is int:
        return 'i' + str( data ) + 'e'
    if type( data ) is list:
        return 'l' + ''.join( map( encode, data ) ) + 'e'
    if type( data ) is dict:
        flattened = utilities.flatten( data.items() )
        encoded = map( encode, flattened )
        joined = ''.join( encoded )
        return 'd' + joined + 'e'

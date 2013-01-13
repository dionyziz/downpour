import random
import socket
import log
import struct

# one of our remote peers to whom we can upload or download from
class Peer:
    torrent = None

    IP = '0.0.0.0'
    id = ''
    port = 0
    chocked = True
    interested = False
    connected = False
    clientName = 'Unknown'
    clientVersion = ''
    # array with boolean value True if peer has the piece or False if they don't
    have = []
    local = True

    __localChoke = True
    __localInterested = False
    __remoteChoke = True
    __remoteInterested = False

    __socket = None

    __lastMsgSent = ''
    __lastMsgRecv = ''
    __buffer = ''

    def __log( self, msg ):
        log.info( '[peer %s:%i] %s' % ( self.ip, self.port. msg ) )
    def __beginSend( self, msg ):
        self.__lastMsgSent = msg
        log.info( 'Sending %s.' % msg )
    def __finishSend( self ):
        log.info( 'Sent %s.' % self.__lastMsg )
    def __beginRecv( self, msg ):
        self.__lastMsgRecv = msg
        log.info( 'Receiving %s.' % msg )
    def __finishRecv( self ):
        log.info( 'Received %s.' % self.__lastMsg )
    def __sendByte( self, b ):
        self.socket.send( struct.pack( '!B', b ) )
    def __sendInt( self, i ):
        self.socket.send( struct.pack( '!I', i ) )
    def __sendString( self, s ):
        if len( s ) == 0:
            return
        self.socket.send( s )
    def __sendTorrentMessage( messageId, payload, length = None ):
        if length is None:
            length = 1 + len( payload )
        if length == 0:
            # keep-alive message; the only message with len = 0 and no id
            self.__sendInt( length )
            return
        self.__sendInt( length )
        self.__sendByte( messageId )
        self.__sendString( payload )
        pass
    def __sendHandshake( self ):
        self.__beginSend( 'handshake' )
        pstr = 'BitTorrent protocol'
        pstrlen = len( pstr )
        self.__sendByte( pstrlen )
        self.__sendString( pstr )
        self.__sendString( 8 * '\0' )
        infoHash = self.torrent.dotTorrent.infoHash
        self.__sendString( infoHash )
        self.__sendString( self.id )
        self.__finishSend()
        pass
    def __sendKeepAlive( self ):
        self.__beginSend( 'keep-alive' )
        self.__sendTorrentMessage( None, None, 0 )
        self.__finishSend()
        pass
    def __sendChoke( self ):
        self.__beginSend( 'choke' )
        self.__sendTorrentMessage( 0 )
        self.__finishSend()
        pass
    def __sendUnchoke( self ):
        self.__beginSend( 'unchoke' )
        self.__sendTorrentMessage( 1 )
        self.__finishSend()
        pass
    def __sendInterested( self ):
        self.__beginSend( 'interested' )
        self.__sendTorrentMessage( 2 )
        self.__finishSend()
        pass
    def __sendUninterested( self ):
        self.__beginSend( 'uninterested' )
        self.__sendTorrentMessage( 3 )
        self.__finishSend()
        pass
    def __sendHave( self, have ):
        self.__beginSend( 'have' )
        self.__sendTorrentMessage( 4, struct.pack( '!I', pieceIndex ) )
        self.__finishSend()
        pass
    def __sendBitfield( self, have ):
        self.__beginSend( 'bitfield' )
        bitfield = ''
        byte = 0
        exponent = 8
        for bit in have:
            if exponent == 0:
                exponent = 8
                bitfield += struct.pack( '!B', byte )
            exponent -= 1
            byte |= bit << exponent
        self.__sendTorrentMessage( 5, bitfield )
        self.__finishSend()
        pass
    def __sendRequest( self, index, begin, length ):
        self.__beginSend( 'request' )
        self.__sendTorrentMessage( 6, struct.pack( '!III', index, begin, length ) )
        self.__finishSend()
        pass
    def __sendPiece( self, index, begin, block ):
        self.__beginSend( 'piece' )
        self.__sendTorrentMessage( 7, struct.pack( '!II', index, begin ) + block )
        self.__finishSend()
        pass
    def __sendCancel( self, index, begin, length ):
        self.__beginSend( 'cancel' )
        self.__sendTorrentMessage( 8, struct.pack( '!III', index, begin, length ) )
        self.__finishSend()
        pass
    def __handleHandshake( self, infoHash, peerId ):
        self.__beginRecv( 'handshake' )
        # TODO: handle handshake
        self.__finishRecv()
        pass
    def __handleKeepAlive( self ):
        self.__beginRecv( 'keep-alive' )
        self.__finishRecv()
        pass
    def __handleChoke( self ):
        self.__beginRecv( 'choke' )
        # TODO: handle choke
        self.__finishRecv()
        pass
    def __handleUnchoke( self ):
        self.__beginRecv( 'unchoke' )
        # TODO: handle unchoke
        self.__finishRecv()
        pass
    def __handleInterested( self ):
        self.__beginRecv( 'interested' )
        # TODO: handle interested
        self.__finishRecv()
        pass
    def __handleUninterested( self ):
        self.__beginRecv( 'uninterested' )
        # TODO: handle uninterested
        self.__finishRecv()
        pass
    def __handleHave( self, pieceIndex ):
        self.__beginRecv( 'have' )
        # TODO: handle have
        self.__finishRecv()
        pass
    def __handleBitfield( self, bitField ):
        # TODO: assert the length of the bitfield matches the number of pieces
        self.__beginRecv( 'bitfield' )
        # TODO: handle bitfield
        self.__finishRecv()
        pass
    def __handleRequest( self ):
        self.__beginRecv( 'request' )
        # TODO: handle request
        self.__finishRecv()
        pass
    def __handlePiece( self, index, begin, block ):
        # TODO: assert index is less than the total number of pieces
        # TODO: assert begin is less than piece size
        # TODO: assert that the whole block is within the piece
        self.__beginRecv( 'piece' )
        # TODO: handle piece
        self.__finishRecv()
        pass
    def __handleCancel( self ):
        self.__beginRecv( 'cancel' )
        # TODO: handle cancel
        self.__finishRecv()
        pass
    def __handleIncomingBytes( self, bytes ):
        # some bytes have arrived
        # each time this function is called, either it returns immediately if no new messages
        # have yet (fully) arrived,
        # or, if there is some new message, it removes that message from the buffer, parses it,
        # and calls the appropriate handlers
        self.__buffer += bytes
        if len( self.__buffer ) < 4:
            # we still haven't received the length of the message
            # wait for more bytes
            return
        # get the length of the message
        length = struct.unpack( '!I', self.__buffer[ :4 ] )[ 0 ]
        # length is the length of the following message
        # check if we have yet received all the data promised for the message
        if len( self.__buffer ) < 4 + length:
            # we still haven't received the full message
            # wait for more bytes
            return
        # remove the length from the buffer
        self.__buffer = self.__buffer[ 4: ]
        if length == 0:
            # 0-length message (keep-alive), so we're done
            self.__handleTorrentMessage( None, None, 0 )
            return
        # get the messageId
        messageId = ord( self.__buffer[ 0 ] )
        # remove the messageId from the buffer
        self.__buffer = self.__buffer[ 1: ]
        # get the payload, which has length equal to the total length of the message
        # minus 1 for the messageId byte
        payload = self.__buffer[ :( length - 1 ) ]
        self.__handleTorrentMessage( messageId, payload, length )
        # remove the payload from the buffer
        # call handler again to handle potentially multiple messages received simultaniously
        self.__handleIncomingBytes( '' )
    def __handleTorrentMessage( self, messageId, payload, length = None ):
        if length == 0:
            # 0-length message is a keep-alive
            return self.__handleKeepAlive()
        if messageId == 0: # choke
            assert( length == 1 )
            return self.__handleChoke()
        if messageId == 1: # unchoke
            assert( length == 1 )
            return self.__handleUnchoke()
        if messageId == 2: # interested
            assert( length == 1 )
            return self.__handleInterested()
        if messageId == 3: # uninterested
            assert( length == 1 )
            return self.__handleUninterested()
        if messageId == 4: # have
            assert( length == 5 )
            pieceIndex = unpack( '!I', payload )[ 0 ]
            return self.__handleHave( payload )
        if messageId == 5: # bitfield
            return self.__handleBitfield( payload )
        if messageId == 6: # request
            assert( length == 13 )
            ( requestIndex, requestBegin, requestLength ) = unpack( '!III', payload )
            return self.__handleRequest( requestIndex, requestBegin, requestLength )
        if messageId == 7: # piece
            pieceLocation = payload[ :8 ]
            ( pieceIndex, pieceBegin ) = unpack( '!II', pieceLocation )
            pieceBlock = payload[ 8: ]
            return self.__handlePiece( pieceIndex, pieceBegin, pieceBlock )
        if messageId == 8: # cancel
            assert( length == 13 )
            ( cancelIndex, cancelBegin, cancelLength ) = unpack( '!III', payload )
            return self.__handleCancel( cancelIndex, cancelBegin, cancelLength )
        # TODO: handshake
        self.__log( 'Unknown p2p wire protocol message id %i.' % messageId ) 
    def choke( self ):
        if self.__localChoke:
            return
        self.__localChoke = True
        self.__sendChoke()
    def unchoke( self ):
        if not self.__localChoke:
            return
        self.__localChoke = False
        self.__sendUnchoke()
    def interested( self ):
        if self.__localInterested:
            return
        self.__localInterested = True
        self.__sendInterested()
    def uninterested( self ):
        if not self.__localInterested:
            return
        self.__localInterested = False
        self.__sendUninterested()
        
    def connect( self ):
        self.socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.__log( 'Connecting...' )
        self.socket.settimeout( 3 )
        try:
            self.socket.connect( ( self.ip, self.port ) )
        except:
            self.__log( 'Connection failed.' )
            return
        self.__log( 'Connected.' )
        self.__sendHandshake()
        self.__log( 'Waiting for data...' )
        data = self.socket.recv( 1024 )
        self.__log( 'Got some data of length %i' % len( data ) )
        self.__handleIncomingBytes( data )
    def __generateId( self ):
        self.id = '-DZ0000-' + "".join( map( chr, [ random.randint( 0, 255 ) for i in range( 0, 12 ) ] ) )
    def __init__( self, torrent, ip = None, port = None ):
        self.torrent = torrent
        if ip is None:
            self.local = True
            self.__generateId()
        else:
            self.local = False
            self.ip = ip
        if port is not None:
            self.port = port

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

    __lastMsg = ''
    __buffer = ''

    def __beginSend( self, msg ):
        self.__lastMsg = msg
        log.info( 'Sending %s to peer %s:%i.' % ( msg, self.ip, self.port ) )
    def __finishSend( self ):
        log.info( '%s sent to peer %s:%i.' % ( self.__lastMsg, self.ip, self.port ) )
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
        log.info( 'Sending handshake to peer %s:%i...' % ( self.ip, self.port ) )
        pstr = 'BitTorrent protocol'
        pstrlen = len( pstr )
        self.__sendByte( pstrlen )
        self.__sendString( pstr )
        self.__sendString( 8 * '\0' )
        infoHash = self.torrent.dotTorrent.infoHash
        self.__sendString( infoHash )
        self.__sendString( self.id )
        log.info( 'Handshake sent to peer %s:%i.' % ( self.ip, self.port ) )
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
    def __handleHandshake( self ):
        pass
    def __handleKeepAlive( self ):
        pass
    def __handleChoke( self ):
        pass
    def __handleUnchoke( self ):
        pass
    def __handleInterested( self ):
        pass
    def __handleUninterested( self ):
        pass
    def __handleHave( self ):
        pass
    def __handleBitfield( self ):
        pass
    def __handleRequest( self ):
        pass
    def __handlePiece( self ):
        pass
    def __handleCancel( self ):
        pass
    def __handleIncomingBytes( self, bytes ):
        self.__buffer += bytes
        # TODO: parse and call appropriate handler
        pass
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
        log.info( 'Connecting to peer %s:%i' % ( self.ip, self.port ) + '...' )
        self.socket.settimeout( 3 )
        try:
            self.socket.connect( ( self.ip, self.port ) )
        except:
            log.info( 'Connection to peer %s:%i failed.' % ( self.ip, self.port ) )
            return
        log.info( 'Connected to peer %s:%i successfully.' % ( self.ip, self.port ) )
        self.__sendHandshake()
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

import log

class Tracker:
    URL = ''
    protocol = '' # http, udp, ...
    supported = False

    def __init__( self, url ):
        pos = url.index( ':' )
        self.protocol = url[ 0:pos ]
        if self.protocol == 'udp':
            self.supported = False
            log.warning( 'Tracker "' + url + '" is using unsupported UDP protocol.' )
            return
        if self.protocol == 'https':
            self.supported = False
            log.warning( 'Tracker "' + url + '" is using unsupported HTTPS protocol.' )
            return
        if self.protocol == 'http':
            # http is fine
            self.supported = True
            return
        log.warning( 'Tracker "' + url + '" is using unknown protocol.' )

BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'

def info( msg ):
    print( BLUE + msg + ENDC )

def warning( msg ):
    print( YELLOW + 'Warning: ' + msg + ENDC )

def error( msg ):
    print( RED + 'Error: ' + msg + ENDC )

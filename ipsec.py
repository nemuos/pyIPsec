import sys
import getopt

from conn import *
from fhandler import *

ADD = 0
DELETE = 1
MODIFY = 2

def updateIPsecConfFile(conn, confFile):
    fh = fhandler(confFile)
    fh.storeFileLines()
    print fh

    fh.replaceLines(conn) 

    print fh

def createNewConnection(name, lines):
    conn = connection(name)

    for line in lines:
        pair = line.split('=')
        conn.__setitem__(pair[0], pair[1])

    return conn


def validateOptions(lines):
    validOptions = [
        'rightauth',
        'leftauth'
    ]
    
    # Check for only one '=' character
    for line in lines:
        if line.count('=') != 1:
            print "Wrongly formatted option given : %s" % line
            return False

        pair = line.split('=')

        if pair[0] not in validOptions:
            print "Invalid option or multiple option: %s" % pair[0]
            return False
       
        validOptions.remove(pair[0])
    
    return True


def main():
    """
        Parse command line arguments
    """
    connArg = False
    confFile = '/etc/ipsec.conf'
    lines = []

    shortopts = 'adm'
    longopts = ['conn=', 'line=', 'file=']

    optlist, args = getopt.getopt(sys.argv[1:], shortopts, longopts)

    # First argument must be one of -a or -d or -m
    if optlist[0][0] not in ['-a', '-d', '-m']:
        print "Wrong first argument"
        sys.exit(1)

    if optlist[0][0] == '-a':
        action = ADD
    elif optlist[0][0] == '-d':
        action = DELETE
    else:
        action = MODIFY


    # Rest are long opts
    optlist = optlist[1:]

    # Check for unrecognized options
    for opt in optlist:
        if opt[0] not in ['--conn', '--line', '--file']:
            print "Unrecognized option %s" % opt[0]

    # One and only one connection option must be present
    for opt in optlist:
        if opt[0] == '--conn':
            connArg = True
            connName = opt[1]
            optlist.remove(opt)
            longopts.remove('conn=')

    if connArg == False:
        print "No connection argument"
        sys.exit(1)

    for opt in optlist:
        if opt[0] == '--file':
            confFile = opt[1]
        elif opt[0] == '--line':
            lines.append(opt[1])

    if not validateOptions(lines):
        sys.exit(1)

    # All checks passeggd, create new connection
    conn = createNewConnection(connName, lines)
    print conn 

    updateIPsecConfFile(conn, confFile)

if __name__ == '__main__':
    main()

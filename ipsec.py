import os
import sys
import getopt

from conn import *
from fmod import *
from actions import *


def main():
    """
        Parse command line arguments
    """
    connArg = False
    lineArg = False
    confFile = '/etc/ipsec.conf'
    lines = []

    shortopts = 'admrs'
    longopts = ['conn=', 'line=', 'file=', 'keylen=', 'rsa-key=']

    optlist, args = getopt.getopt(sys.argv[1:], shortopts, longopts)

    # First argument must be one of [-a, -d, -m, -r, -s]
    if optlist[0][0] not in ['-a', '-d', '-m', '-r', '-s']:
        print "Wrong first argument\nShould be [-a, -d, -m, -r, -s]"
        sys.exit(1)

    if optlist[0][0] == '-a':
        addOrModActionHandler(optlist)
    elif optlist[0][0] == '-d':
        delActionHandler(optlist)
    elif optlist[0][0] == '-m':
        addOrModActionHandler(optlist)
    elif optlist[0][0] == '-r':
        rsaKeyGenActionHandler(optlist)
    elif optlist[0][0] == '-s':
        rsaKeySaveActionHandler(optlist)


if __name__ == '__main__':
    main()

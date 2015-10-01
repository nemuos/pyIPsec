import os
import sys

ADD = 0
DELETE = 1
MODIFY = 2

def updateIPsecConfFile(conn, confFile, action):
    fm = fmod(confFile)
    fm.storeFileLines()

    if action == MODIFY:
        fm.replaceLines(conn) 
    elif action == ADD:
        fm.addLines(conn)
    else:
        fm.deleteLines(conn)
    
    # delete old file
    os.remove(confFile)

    # write conf in new file
    fh = open(confFile, 'w')
    for line in fm.lines:
        fh.write(line)
        
    fh.close()


def createNewConnection(name, lines):
    conn = connection(name)

    for line in lines:
        pair = line.split('=', 1)
        conn.__setitem__(pair[0], pair[1])

    return conn


def validateOptions(lines):
    validOptions = [
        'rightauth',
        'leftauth',
        'keyingtries',
        'ikelifetime',
        'lifetime',
        'lifepackets',
        'lifebytes'
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


def addorModActionHandler(optlist):
    connArg = False
    lineArg = False
    fileArg = False
    confFile = '/etc/ipsec.conf'
    lines = []

    if optlist[0] == '-a':
        action = ADD
    else:
        action = MODIFY

    optlist = optlist[1:]

    # Check for unrecognized options
    for opt in optlist:
        if opt[0] not in ['--conn', '--line', '--file']:
            print 'Unrecognized option %s' % opt[0]
            sys.exit(1)
    
    for opt in optlist:
        if connArg == False and opt[0] == '--conn':
            connArg = True
            connName = opt[1]
            optlist.remove(opt)
        elif connArg == True and opt[0] == '--conn':
            print 'More than one connection option'
            sys.exit(1)
        elif opt[0] == '--line':
            lineArg = True
            lines.append(opt[1])
        elif fileArg == False and opt[0] == '--file':
            confFile = opt[1]
            fileArg = True
        elif fileArg == True and opt[0] == '--file':
            print 'More than one file option'
            sys.exit(1)

    if connArg == False:
        print 'No connection option'
        sys.exit(1)
                
    if lineArg == False:
        print 'At lease one --line option should be in add/modify'
        sys.exit(1)
    
    if not validateOptions(lines):
        sys.exit(1)

    # All checks passed, create new connection
    conn = createNewConnection(connName, lines)

    updateIPsecConfFile(conn, confFile, action)


def delActionHandler(optlist):
    connArg = False
    fileArg = False
    confFile = '/etc/ipsec.conf'
    lines = []

    action = DELETE
    optlist = optlist[1:]

    # Check for unrecognized options
    for opt in optlist:
        if opt[0] not in ['--conn', '--file']:
            print 'Unrecognized option %s' % opt[0]
            sys.exit(1)
    
    for opt in optlist:
        if connArg == False and opt[0] == '--conn':
            connArg = True
            connName = opt[1]
            optlist.remove(opt)
        elif connArg == True and opt[0] == '--conn':
            print 'More than one connection option'
            sys.exit(1)
        elif fileArg == False and opt[0] == '--file':
            confFile = opt[1]
            fileArg = True
        elif fileArg == True and opt[0] == '--file':
            print 'More than one file option'
            sys.exit(1)
    
    if connArg == False:
        print 'No connection option'
        sys.exit(1)

    # All checks passed, create new connection
    conn = createNewConnection(connName, lines)

    updateIPsecConfFile(conn, confFile, action)


def rsaKeyGenActionHandler(optlist):
    fileArg = False
    keylenArg = False
    keylen = 2048

    optlist = optlist[1:]
    
    # Check for unrecognized options
    for opt in optlist:
        if opt[0] not in ['--keylen', '--file']:
            print 'Unrecognized option %s' % opt[0]
            sys.exit(1)

    for opt in optlist:
        if fileArg == False and opt[0] == '--file':
            fileArg = True
            fileName = opt[1]
        elif fileArg == True and opt[0] == '--file': 
            print 'Only one file option should be present'
            sys.exit(1)
        elif keylenArg == False and opt[0] == '--keylen':
            keylenArg = True
            keylen = opt[1]
        elif keylenArg == True and opt[0] == '--keylen':
            print 'Only one keylen option should be present'
            sys.exit(1)

    if fileArg == False:
        print '--file option missing'
        sys.exit(1)

    dirPath = '/'.join(fileName.split('/')[0:-1])
    pubFile, ext = os.path.basename(fileName).split('.')
    priFile = dirPath + '/' + pubFile + '-pri.' + ext
    pubFile = dirPath + '/' + pubFile + '.' + ext

    os.system('openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:%s \
               -pkeyopt rsa_keygen_pubexp:3 -out %s >> /dev/null 2>&1' 
               % (keylen, priFile))

    os.system('openssl pkey -in %s -out %s -pubout >> /dev/null 2>&1' 
               % (priFile, pubFile))


def rsaKeySaveActionHandler(optlist):
    fileArg = False
    keyArg = False

    optlist = optlist[1:]
    
    # Check for unrecognized options
    for opt in optlist:
        if opt[0] not in ['--rsa-key', '--file']:
            print 'Unrecognized option %s' % opt[0]
            sys.exit(1)

    for opt in optlist:
        if fileArg == False and opt[0] == '--file':
            fileArg = True
            fileName = opt[1]
        elif fileArg == True and opt[0] == '--file': 
            print 'Only one file option should be present'
            sys.exit(1)
        elif keyArg == False and opt[0] == '--rsa-key':
            keyArg = True
            rsaKey = opt[1]
        elif keyArg == True and opt[0] == '--rsa-key':
            print 'Only one keylen option should be present'
            sys.exit(1)

    if fileArg == False:
        print '--file option missing'
        sys.exit(1)
    
    if keyArg == False:
        print '--rsa-key option missing'
        sys.exit(1)

    # delete existing file of same name
    if (os.path.isfile(fileName)):
        os.remove(fileName)

    startLine = '-----BEGIN PUBLIC KEY-----\n' 
    endLine = '-----END PUBLIC KEY-----\n'

    fh = open(fileName, "w")
    fh.write(startLine) 
    
    while (len(rsaKey) >= 64):
        line = rsaKey[0:64] + '\n'
        fh.write(line)
        rsaKey = rsaKey[64:]

    if len(rsaKey) != 0:
        fh.write(rsaKey + '\n')

    fh.write(endLine) 
    
    fh.close()

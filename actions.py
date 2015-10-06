import os
import sys
from pyparsing import *

from conn import *
from fmod import *

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


def parseOptions(optList, validList):
    parsedArgs = {}

    for opt in optList:
        if opt[0] in validList and opt[0] in parsedArgs:
            print 'Only one %s option should be present' % opt[0]
            sys.exit(1)

        parsedArgs[opt[0]] = opt[1]  


def addOrModActionHandler(optlist):
    connArg = False
    lineArg = False
    fileArg = False
    confFile = '/etc/ipsec.conf'
    lines = []

    if optlist[0][0] == '-a':
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
            #optlist.remove(opt)
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
            #optlist.remove(opt)
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


def getSaGrammar():
    ParserElement.setDefaultWhitespaceChars('\t ')                              
    SOL = LineStart().suppress()                                                
    EOL = LineEnd().suppress()                                                  
                                                                                
    ipv4Addr = (Combine(Word(nums) + ('.' + Word(nums))*3))                     
    hashAlgo = Literal('hmac(') + (Literal('sha1') | Literal('md5')).setResultsName('hashAlgo') + Literal(')')
    encAlgo = Literal('cbc(') + (Literal('des3_ede') | Literal('aes128')).setResultsName('encAlgo') + Literal(')')
    proto = (Literal('esp') | Literal('ah')).setResultsName('proto')            
    spi = Word(nums + 'abcdefx').setResultsName('spi')                          
    mode = (Literal('tunnel') | Literal('transport')).setResultsName('mode')    
    hashKey = Word(nums + 'abcdefx')                                            
    hashLen = Word(nums)                                                        
    encKey = Word(nums + 'abcdefx')                                             
                                                                                
    paragraph = Group(SOL + \
                Literal('src') + ipv4Addr.setResultsName('src') + \
                Literal('dst') + ipv4Addr.setResultsName('dst') + \
                EOL + \
                Literal('proto') + proto + \
                Literal('spi') + spi + \
                Literal('reqid') + Word(nums) + \
                Literal('mode') + mode + \
                EOL + \
                Literal('replay-window') + Word(nums) + \
                Literal('flag') + Word(alphas + '-') + \
                EOL + \
                Literal('auth-trunc') + hashAlgo + \
                hashKey + hashLen + \
                EOL + \
                Literal('enc') + encAlgo + \
                encKey + \
                EOL)

    grammar = OneOrMore(paragraph)

    return grammar




def saShowHandler(optlist):
    fileArg = False
    peerArg = False

    peerIP = None

    optlist = optlist[1:]
    
    # Check for unrecognized options
    for opt in optlist:
        if opt[0] not in ['--file', '--peer']:
            print 'Unrecognized option %s' % opt[0]
            sys.exit(1)

    for opt in optlist:
        if fileArg == False and opt[0] == '--file':
            fileArg = True
            fileName = opt[1]
        elif fileArg == True and opt[0] == '--file': 
            print 'Only one file option should be present'
            sys.exit(1)
        if peerArg == False and opt[0] == '--peer':
            peerArg = True
            peerIP = opt[1]
        elif peerArg == True and opt[0] == '--peer': 
            print 'Only one peer option should be present'
            sys.exit(1)

    if fileArg == False:
        print '--file option missing'
        sys.exit(1)

    #if not peerIP:
        #os.system("ip xfrm state ls > %s" % fileName);
    #else
        #os.system("ip xfrm state ls dst %s > %s" % (peerIP, fileName))
        #os.system("ip xfrm state ls src %s > %s" % (peerIP, fileName))

    saGrammar = getSaGrammar()

    try:
        parsedState = saGrammar.parseFile(fileName)

        print "Dst           Src           Proto   Encrypt   Hash  Mode      Spi"
        print "------------------------------------------------------------------------"

        for state in parsedState:
            print "%-14s%-14s%-8s%-10s%-6s%-10s%s" % \
                (state.dst, state.src, state.proto, state.encAlgo, 
                 state.hashAlgo, state.mode , state.spi)

        print ""
        
    except ParseException:
        print 'Parse exception'
        sys.exit(1)

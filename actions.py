import os
import sys
from pyparsing import *

from conn import *
from fmod import *

ADD = 0
DELETE = 1
MODIFY = 2

OPTIONAL = 0
MANDATORY = 1

SINGLE = 0
MULTI = 1


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


def parseOptions(optlist, template):
    for opt in optlist:
        if opt[0] not in template:
            print '%s option not valid in current context' % opt[0]
            sys.exit(1)

    parsedArgs = {}
    for key in template.keys():
        parsedArgs[key] = [False]


    for opt in optlist:
        if parsedArgs[opt[0]][0] == False:
            parsedArgs[opt[0]][0] = True
            parsedArgs[opt[0]].append(opt[1])

        elif parsedArgs[opt[0]][0] == True and template[opt[0]][1] == SINGLE:
            print 'More than one %s option' % opt[0]
            sys.exit(1)

        elif parsedArgs[opt[0]][0] == True and template[opt[0]][1] == MULTI:
            parsedArgs[opt[0]].append(opt[1])

    for arg in template.keys():
        if template[arg][0] == MANDATORY and parsedArgs[arg][0] == False:
            print 'No %s option present' % arg
            sys.exit(1)

    for key in parsedArgs.keys():
        if parsedArgs[key][0] == False:
            del parsedArgs[key]
        else:
            parsedArgs[key] = parsedArgs[key][1:]

    return parsedArgs            


def addOrModActionHandler(optlist):
    confFile = '/etc/ipsec.conf'

    if optlist[0][0] == '-a':
        action = ADD
    else:
        action = MODIFY

    optlist = optlist[1:]
   
    template = \
        {
            '--file'    :   [OPTIONAL, SINGLE],
            '--conn'    :   [MANDATORY, SINGLE],
            '--line'    :   [MANDATORY, MULTI]
        }
   
    parsedArgs = parseOptions(optlist, template)
    print parsedArgs

    lines = parsedArgs['--line']
    connName = parsedArgs['--conn'][0]
    if '--file' in parsedArgs:
        confFile = parsedArgs['--file'][0]

    if not validateOptions(lines):
        sys.exit(1)

    # All checks passed, create new connection
    conn = createNewConnection(connName, lines)

    updateIPsecConfFile(conn, confFile, action)


def delActionHandler(optlist):
    confFile = '/etc/ipsec.conf'

    action = DELETE
    optlist = optlist[1:]
    
    template = \
        {
            '--file'    :   [OPTIONAL, SINGLE],
            '--conn'    :   [MANDATORY, SINGLE],
        }
   
    parsedArgs = parseOptions(optlist, template)
    print parsedArgs

    connName = parsedArgs['--conn'][0]
    if '--file' in parsedArgs:
        confFile = parsedArgs['--file'][0]


    # All checks passed, create new connection
    conn = createNewConnection(connName, [])

    updateIPsecConfFile(conn, confFile, action)


def rsaKeyGenActionHandler(optlist):
    keylen = 2048

    optlist = optlist[1:]
    
    template = \
        {
            '--file'    :   [MANDATORY, SINGLE],
            '--keylen'  :   [OPTIONAL, SINGLE],
        }
   
    parsedArgs = parseOptions(optlist, template)
    print parsedArgs

    fileName = parsedArgs['--file'][0]

    if '--keylen' in parsedArgs:
        keylen = parsedArgs['--keylen'][0]
   
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
    optlist = optlist[1:]
    
    template = \
        {
            '--file'    :   [MANDATORY, SINGLE],
            '--rsa-key' :   [MANDATORY, SINGLE],
        }
   
    parsedArgs = parseOptions(optlist, template)
    print parsedArgs

    fileName = parsedArgs['--file'][0]
    rsaKey = parsedArgs['--rsa-key'][0]

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
    peerIP = None

    optlist = optlist[1:]
     
    template = \
        {
            '--file'    :   [MANDATORY, SINGLE],
            '--peer'    :   [OPTIONAL, SINGLE],
        }
   
    parsedArgs = parseOptions(optlist, template)
    print parsedArgs

    fileName = parsedArgs['--file'][0]
    if '--peer' in parsedArgs:
        peerIP = parsedArgs['--peer'][0]
   
    #if not peerIP:
        #os.system("ip xfrm state ls > %s" % fileName);
    #else
        #os.system("ip xfrm state ls dst %s > %s" % (peerIP, fileName))
        #os.system("ip xfrm state ls src %s > %s" % (peerIP, fileName))

    if not os.path.isfile(fileName):
        print 'file not present'
        sys.exit(1)

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

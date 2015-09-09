class fhandler(list):
    def __init__(self, confFile):
        self.confFile = confFile
        self.lines = []

    def storeFileLines(self):
        fh = open(self.confFile, 'r')
       
        while True:
            line = fh.readline()
            if line == '':
                break
            
            self.lines.append(line)

        fh.close()         

    def replaceLines(self, conn):
        connName = conn.name
        lines = len(self.lines)
        confEnd = -1

        for i in range(0, lines):
            line = self.lines[i]

            if line.find(connName) != -1:   # start of connection conf
                confStart = i

        for i in range(confStart, lines):
            line = self.lines[i]

            if line == '\n':    # end of connection conf
                confEnd = i
               
        if confEnd == -1:   # last connection in file, with no newline after it
            confEnd = lines - 1

        for key in conn.data.keys():
            found = 0
            for i in range(confStart, confEnd + 1):
                line = self.lines[i]

                if line.find(key) != -1: # param found, replace it inplace
                    newLine = '  ' + key + '=' + conn.data[key] + '\n'
                    self.lines[i] = newLine
                    found = 1

            if found == 0: # new param, add it at the end of conf
                newLine = '  ' + key + '=' + conn.data[key] + '\n'
                self.lines.insert(confEnd, newLine)

    def __str__(self):
        desc = self.confFile + "\n"
        return desc + str(self.lines)


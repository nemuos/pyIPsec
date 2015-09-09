TAB = '  '

class fmod(list):
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


    def deleteLines(self, conn):
        connName = conn.name
        lines = len(self.lines)

        if self.lines[lines - 1] != '\n':
            self.lines.append('\n')
            lines = lines + 1
       
        for i in range(0, lines):
            line = self.lines[i]

            if line.find(connName) != -1:   # start of connection conf
                confStart = i

        for i in range(confStart, lines):
            line = self.lines[i]

            if line == '\n':    # end of connection conf
                confEnd = i
                break

        tempList = self.lines[:confStart]
        tempList = tempList + self.lines[(confEnd + 1):]
        self.lines = tempList


    def addLines(self, conn):
        connName = conn.name
        lines = len(self.lines)

        if lines == 0 or self.lines[lines - 1] != '\n':
            self.lines.append('\n')

        # add connection name
        newLine = 'conn ' + connName + '\n'
        self.lines.append(newLine)

        # add params
        for key in conn.data.keys():
            newLine = TAB + key + '=' + conn.data[key] + '\n'
            self.lines.append(newLine)

        self.lines.append('\n')     

        if lines == 0:
            self.lines = self.lines[1:]


    def replaceLines(self, conn):
        connName = conn.name
        lines = len(self.lines)

        if self.lines[lines - 1] != '\n':
            self.lines.append('\n')
            lines = lines + 1

        for i in range(0, lines):
            line = self.lines[i]

            if line.find(connName) != -1:   # start of connection conf
                confStart = i

        for i in range(confStart, lines):
            line = self.lines[i]

            if line == '\n':    # end of connection conf
                confEnd = i
                break

        for key in conn.data.keys():
            found = 0
            for i in range(confStart, confEnd + 1):
                line = self.lines[i]

                if line.find(key) != -1: # param found, replace it inplace
                    newLine = TAB + key + '=' + conn.data[key] + '\n'
                    self.lines[i] = newLine
                    found = 1

            if found == 0: # new param, add it at the end of conf
                newLine = TAB + key + '=' + conn.data[key] + '\n'
                self.lines.insert(confEnd, newLine)


    def __str__(self):
        desc = self.confFile + "\n"
        return desc + str(self.lines)


from os import listdir


def aggreg(dir, filename):
    fileO = open(filename, 'w')
    listFile = listdir(dir)
    fileO.write("seed;graphSize;graphDepth;sdComp;sdComm;CCR;nbproc;prio;cost;placement;BIM;ins;bsa;makespan;time\n")
    for fileName in listFile:
        file = open(dir + "/" + fileName, "r")
        firstLine = True
        toSub = 0
        seed = graphSize = graphDepth = sdComp = sdComm = CCR = nbproc = None
        for index, line in enumerate(file.readlines()):
            if line.startswith("#@"):
                param = line.split()[0][2:]
                val = line.split()[1]
                if param == 'seed':
                    seed = val
                elif param == 'graphSize':
                    graphSize = val
                elif param == 'graphDepth':
                    graphDepth = val
                elif param == 'sdComp':
                    sdComp = val
                elif param == 'sdComm':
                    sdComm = val
                elif param == 'CCR':
                    CCR = val
                elif param == 'nbproc':
                    nbproc = val
                continue
            elif line == '\n':
                continue
            elif firstLine:
                firstLine = False
                sdComp = round(float(sdComp) * float(CCR), 2)
                continue
            lineT = f'{seed};{graphSize};{graphDepth};{sdComp};{sdComm};{CCR};{nbproc};{line}'
            fileO.write(lineT)
    fileO.close()


if __name__ == '__main__':
    aggreg('res', 'ress.csv')

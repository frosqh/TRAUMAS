from os import listdir

from numpy import mean, median

meanFilename = "meanres.txt"
maxFilename = "maxres.txt"
minFilename = "minres.txt"
medianFilename = "medianres.txt"
firstQFilename = "firstQres.txt"
lastQFilename = "lastQres.txt"


def analyse(dir):
    listFile = listdir(dir)
    heurRanks = {}
    for fileName in listFile:
        file = open(dir + "/" + fileName, "r")
        firstLine = True
        toSub = 0
        for index, line in enumerate(file.readlines()):
            if line.startswith("#@") or line == '\n':
                continue
            if firstLine:
                firstLine = False
                toSub = index
                continue
            heur, mk, rt = line[:-1].split(" ")
            heurRanks.setdefault(heur, []).append(index - toSub)
    l = sorted(heurRanks.keys(), key=lambda x: mean(heurRanks[x]))
    n = len(l)
    file = open(meanFilename, 'w')
    for h in l:
        file.write(f"{h} {mean(heurRanks[h])}\n")
    file.close()

    l = sorted(heurRanks.keys(), key=lambda x: max(heurRanks[x]))
    file = open(maxFilename, 'w')
    for h in l:
        file.write(f"{h} {max(heurRanks[h])}\n")
    file.close()

    l = sorted(heurRanks.keys(), key=lambda x: min(heurRanks[x]))
    file = open(minFilename, 'w')
    for h in l:
        file.write(f"{h} {min(heurRanks[h])}\n")
    file.close()

    l = sorted(heurRanks.keys(), key=lambda x: median(heurRanks[x]))
    file = open(medianFilename, 'w')
    for h in l:
        file.write(f"{h} {median(heurRanks[h])}\n")
    file.close()

    l = sorted(heurRanks.keys(), key=lambda x: sum(list(map(lambda y: y >= n * 0.75, heurRanks[x]))))
    file = open(lastQFilename, 'w')
    for h in l:
        file.write(f"{h} {sum(list(map(lambda y: y >= n * 0.75, heurRanks[h])))}\n")
    file.close()

    l = sorted(heurRanks.keys(), key=lambda x: sum(list(map(lambda y: y <= n * 0.25, heurRanks[x]))), reverse=True)
    file = open(firstQFilename, 'w')
    for h in l:
        file.write(f"{h} {sum(list(map(lambda y: y <= n * 0.25, heurRanks[h])))}\n")
    file.close()


if __name__ == '__main__':
    analyse("res")

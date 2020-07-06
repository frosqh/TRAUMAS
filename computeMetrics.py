from os import listdir
from statistics import mean, median, stdev

from computations.Priorities import getCP
from help.FileReader import readFile
from metrics.Sequential import sequentialScheduleLength

if __name__ == '__main__':
    writeFile = open("resSLR.log", "w")
    listFile = listdir("res")
    SLRs = []
    speedups = []
    effs = []
    for seed in range(4320):
        if seed % 100 == 0:
            print(f"Treating seed {seed}, length listFile {len(listFile)}")
        graph = readFile(f"graphs/tmp{seed}.gml", converter=False, verbose=False)
        fileName = ""
        line = ""
        for fileName in listFile:
            if fileName.endswith(f"-{seed}.csv"):
                file = open("res/" + fileName)
                file.readline()
                file.readline()
                file.readline()
                file.readline()
                file.readline()
                file.readline()
                file.readline()
                line = file.readline()
                file.close()
                break
        listFile.remove(fileName)
        mk = (float(line.split()[1]))
        print(mk)
        minCP = getCP(graph, costFunction="minmin")
        minMakespan = sum(map(lambda n: min(graph.graph['costmatrix'][n - 1]), minCP))
        seqMakespan = sequentialScheduleLength(graph, False)
        speedup = seqMakespan / mk
        eff = speedup/graph.graph["nbproc"]
        SLRs.append(mk / minMakespan)
        speedups.append(speedup)
        effs.append(eff)
        writeFile.write(f"SLR : {mk / minMakespan} for seed {seed} \n")
    writeFile.close()
    print(f"Mean :\n-----------\nSLR : {mean(SLRs)}\nSpeedup : {mean(speedups)}\nEfficiency : {mean(effs)}\n")
    print(f"Median :\n-----------\nSLR : {median(SLRs)}\nSpeedup : {median(speedups)}\nEfficiency : {median(effs)}\n")
    print(f"Std :\n-----------\nSLR : {stdev(SLRs)}\nSpeedup : {stdev(speedups)}\nEfficiency : {stdev(effs)}\n")

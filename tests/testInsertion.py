from computations.Placements import findBestProcEFT
from help.FileReader import readFile

if __name__ == '__main__':
    graph = readFile("testIns.gml", converter=False, verbose=False)
    schedule = {0: (0, 0., 1), 1: (0, 1, 2.), 3: (0, 5, 6)}
    print(schedule)
    findBestProcEFT(graph, 2, schedule, "", False, True, False, [0, 1, 2, 3, 4])
    print(schedule)

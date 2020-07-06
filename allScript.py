import os
from multiprocessing import Process
from os import listdir

from blessings import Terminal
from progressbar import ProgressBar

sizes = [15, 30, 50, 100]
cv = [0.1, 0.3, 1]
depths = [0.17, 0.34]
sdComps = [0.1, 0.3, 1]
CCRs = [0.1, 1, 10]
nbProcs = [3, 6]

pregraphDir = "pregraphs"
graphDir = "graphs"
resDir = "res"

class Writer(object):
    """Create an object with a write method that writes to a
    specific place on the screen, defined at instantiation.
    This is the glue between blessings and progressbar.
    """

    def __init__(self, location, termi, seed):
        """
        Input: location - tuple of ints (x, y), the position
                          of the bar in the terminal
        """
        self.term = termi
        self.location = location
        self.seed = seed

    def write(self, string):
        with self.term.location(*self.location):
            print(f"Thread n°{self.seed} : {string}")

    def flush(self):
        pass


def script(seed, pbar: ProgressBar, seeds):
    tot = len(depths) * len(sdComps) * len(CCRs) * len(cv) * len(nbProcs) * len(sizes)
    cnt = 0
    pbar.maxval = tot
    pbar.start()
    for size in sizes:
        for depth in depths:
            for sdComp in sdComps:
                for CCR in CCRs:
                    for sdComm in map(lambda x: x * CCR, cv):
                        for totProc in nbProcs:
                            if str(seed) not in seeds:
                                os.system(
                                    f'python3 main.py null -g {size} {int(depth * size)} '
                                    f'{graphDir}/tmp{seed}.gml {sdComp} {sdComm} {CCR} -s {seed} -n -p {totProc}')
                                filename = f"{resDir}/output{size}-{totProc}-{int(depth * size)}-{sdComp}" \
                                           f"-{CCR}-{round(sdComm, 3)}-{seed}.csv"
                                os.system(
                                    f'python3 main.py {filename} -G {graphDir}/tmp{seed}.gml -a 1 -s {seed} -p {totProc}')
                            seed += 1
                            cnt += 1
                            pbar.update(cnt)
    pbar.finish()


def main(seeds):
    nbThread = 5
    proc = []
    writers = [Writer((0, x + 1), term, s) for x, s in enumerate(range(nbThread))]
    pbars = [ProgressBar(fd=writer) for writer in writers]
    with term.location(0, 0):
        print("Progress :")
    for i in range(nbThread):
        # window.addstr(index + 1, 0, f"Seed n°{s} :")
        tot = len(depths) * len(sdComps) * len(CCRs) * len(cv) * len(nbProcs) * len(sizes)
        p = Process(target=script, args=(nbThread*tot + i * tot, pbars[i], seeds))
        p.start()
        proc.append(p)
    for p in proc:
        p.join()


if __name__ == '__main__':
    if not os.path.exists(graphDir):
        os.makedirs(graphDir)
    if not os.path.exists(pregraphDir):
        os.makedirs(pregraphDir)
    if not os.path.exists(resDir):
        os.makedirs(resDir)
    listFile = listdir(resDir)
    treatedSeed = []
    for fileName in listFile:
        seed = fileName.split("-")[-1].split(".")[0]
        treatedSeed.append(seed)
    term = Terminal()
    with term.fullscreen():
        main(treatedSeed)
        os.system("python3 resAggregator.py")
        os.system("python3 testTree.py")

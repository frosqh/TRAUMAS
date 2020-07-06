import random
import timeit

import numpy

from computations.Placements import *
from computations.Priorities import *
from executions.ExtensiveTest import realTryHard
from executions.TotalComputation import computeSchedule
from help.FileReader import readFile
from help.GraphGenerator import genGraph
from help.MailSender import sendMail
from help.Parser import defineParser
from metrics.Speedup import measureSpecificEfficiency, measureGeneralEfficiency, measureSpeedup
from tests.VerifPrecedence import verifPrec

DEBUG = False  # Define verbose in the main call (Override by --verbose option)
MAIL = False  # Should send a mail after case 1 completion (Override by --mail option)

if __name__ == '__main__':

    parser = defineParser()

    args = parser.parse_args()

    # print(args)

    DEBUG = args.verbose

    if args.seed:
        random.seed(int(args.seed))
        numpy.random.seed(int(args.seed))

    start = timeit.default_timer()
    graphname = ""
    if args.generate:
        graph = genGraph(*args.generate, args.nbproc)
        graphname = args.generate[2]
    else:
        graph = readFile(args.graphfile, verbose=DEBUG)
        graphname = args.graphfile
    end = timeit.default_timer()

    if args.nbproc:
        graph.graph['nbproc'] = int(args.nbproc)
    # print("Time elapsed to read file :", round(1000 * (end - start), 2), "ms")

    result = ""
    resultCSV = ""
    if args.generate:
        resultCSV += f"#@seed {args.seed}\n"
        resultCSV += f"#@graphSize {args.generate[0]}\n"
        resultCSV += f"#@graphDepth {args.generate[1]}\n"
        resultCSV += f"#@sdComp {args.generate[3]}\n"
        resultCSV += f"#@sdComm {round(float(args.generate[4]), 2)}\n"
        resultCSV += f"#@CCR {args.generate[5]}\n"
        resultCSV += f"#@nbproc {args.nbproc}\n"
    else:
        try:
            file = open("pre" + args.graphfile, "r")
            s = file.read()
            resultCSV += s
        except Exception:
            pass
        # resultCSV += f"#@graphUsed {args.graphfile}\n"

    if args.all:
        realstart = timeit.default_timer()
        r = realTryHard(graph, int(args.all), DEBUG, graphname)
        rs = sorted(r, key=r.get, reverse=False)
        minmk = round(r[rs[0]][0], 4)
        resultCSV += f"#@minmk {minmk}\n\n"
        resultCSV += "prio;cost;placement;desc;BIM;ins;bsa;makespan;time\n"
        realend = timeit.default_timer()
        for tryIndex in rs:
            result += f"{tryIndex.split(';')} {r[tryIndex]}\n"
            resultCSV += f"{tryIndex};{round(minmk / r[tryIndex][0], 4)};{r[tryIndex][1]}\n"
        # result += "\nTotal time elapsed : " + str(round(realend - realstart, 2)) + "s.\n"
        # result += verifBSA(rs, r, DEBUG)
        file = open(args.filename, 'w')
        file.write(resultCSV)
        file.close()
    elif args.heuristic:
        start = timeit.default_timer()
        aPrio, aCostFunction, aStrategyPlacement, aDesc, aUseOfBIM, absa, aInsertion = args.heuristic
        name = aPrio + "-" + aCostFunction + "-" + aStrategyPlacement + int(aUseOfBIM) * "-BIM" + int(
            aInsertion) * "-ins" + int(absa) * "-bsa"
        print(f"Name {name}")
        finalSchedule = computeSchedule(graph, strategyPrio=aPrio, costFunction=aCostFunction,
                                        strategyPlacement=aStrategyPlacement, desc=aDesc,
                                        useOfBIM=bool(int(aUseOfBIM)), verbose=DEBUG,
                                        insertion=bool(int(aInsertion)), bsa=bool(int(absa)))
        end = timeit.default_timer()
        verifPrec(graph, finalSchedule, DEBUG)
        time = round(1000 * (end - start), 2)
        makespan = finalSchedule[getExitTask(graph)][2]
        efficiency = round(measureSpecificEfficiency(graph, finalSchedule, verbose=DEBUG), 3)
        gEfficiency = round(measureGeneralEfficiency(graph, finalSchedule, verbose=False), 3)
        speedup = round(measureSpeedup(graph, finalSchedule, verbose=False), 3)
        if DEBUG:
            printSchedule(finalSchedule)
        verifPrec(graph, finalSchedule, DEBUG)
        result = f"Time elapsed to compute schedule : {time}ms\n"
        result += f"Makespan : {makespan}\n"
        result += f"Efficiency : {efficiency}\n"
        result += f"General Efficiency : {gEfficiency}\n"
        result += f"Speedup : {speedup}\n"
        print(result)
    else:
        file = open("pre" + args.generate[2], 'w')
        file.write(resultCSV)
        file.close()

    if args.mail and not args.nothing:
        sendMail(args.all if args.all else 1, result)

# TODO Comment gérer DCP ? Il faudrait regarder comment définir le DCP (AEST/ALST) et rku/rkd ... -> Une tentative a été
#  réalisée, mais rien de bien concret atm

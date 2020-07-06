import timeit
from typing import Dict, Tuple, List

from computations.Priorities import getExitTask
from executions.TotalComputation import computeSchedule
from tests.VerifPrecedence import verifPrec


# noinspection PyBroadException
def tryEverything(g, verbose, graphname):
    """ Try every heuristic possible according to given array


    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :param graphname: Name of the graph used, for error tracking purpose
    :type graphname: str
    :return: Results of each heuristics and runtime in ms {heuristic : [makespan, runtime]}
    :rtype: dict[str, list[float]]
    """
    prio = ['rku', 'random', 'BIL', 'rkd', 'cluHPS', 'rkusd', 'rkuad']
    placement = ['eft', 'BIM*', 'OLB', 'MET', 'DL', 'GDL']
    costFunction = ['mean', 'median', 'maxmax', 'minmax', 'minmin', 'maxmin']
    desc = ['DLS/DC', None, 'DCP']
    useOfBIM = [False, True]
    insertion = [False, True]
    BSA = [False, True]
    res: Dict[str, List[float]] = {}
    cnt = 0

    for ip, p in enumerate(prio):
        for ipl, pl in enumerate(placement):
            for ic, c in enumerate(costFunction):
                if p != 'BIL' or c == 'mean' or pl in ['DL', 'GDL']:
                    for idd, d in enumerate(desc):
                        for iu, u in enumerate(useOfBIM):
                            for ii, i in enumerate(insertion):
                                for ib, b in enumerate(BSA):
                                    cnt += 1
                                    name = ";".join(map(str, [ip, ic, ipl, idd, iu, ii, ib]))

                                    # dispName = "-".join(map(str, [p, pl, c, d, u, i, b]))
                                    # print("Heuristic n°", cnt, "-", dispName)
                                    # print("Heuristic n°", cnt, "-", name)

                                    startScheduling = timeit.default_timer()
                                    try:
                                        schedule = computeSchedule(g, strategyPrio=p, costFunction=c,
                                                                   strategyPlacement=pl,
                                                                   useOfBIM=u, desc=d,
                                                                   insertion=i, bsa=b, verbose=verbose)
                                        verifPrec(g, schedule, verbose)
                                        endScheduling = timeit.default_timer()
                                        # print("Ended in :", 1000*(endScheduling - startScheduling), "ms")
                                        # print("Ended in :", round(1000 * (endScheduling - startScheduling),2), "ms")
                                        timeS = round(1000 * (endScheduling - startScheduling), 2)
                                        # print(f"timeS : {timeS}")
                                        if verbose:
                                            print(f"Time : {timeS}ms")
                                        res[name] = [round(schedule[getExitTask(g)][2], 6), timeS]
                                    except Exception as _:

                                        print("Error for : " + name + " on file " + graphname)
                                        file = open("error.log", 'a')
                                        file.write(f"Error for {name} on file {graphname}\n")
                                        file.close()
                                        raise _
                                        return res
    return res


def realTryHard(g, n, verbose=False, graphname=""):
    """ Try every heuristics a given number of time, to measure a meaningful runtime

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param n: Number of batches to realize
    :type n: int
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :param graphname: Name of the graph used, for error tracking purpose
    :type graphname: str
    :return: Results of each heuristics and runtime in ms {heuristic : [makespan, runtime]}
    :rtype: dict[str, list[float]]
    """
    tot = None
    for i in range(n):
        # print("Starting batch ", i)
        res = tryEverything(g, verbose, graphname)
        if tot is None:
            tot = res
        else:
            for j in res:
                tot[j][1] += res[j][1]
    for j in tot:
        tot[j][1] /= n
        tot[j][1] = round(tot[j][1], 3)
    return tot

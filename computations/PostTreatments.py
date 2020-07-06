from computations.CommCost import commCost
from computations.EarliestTimes import computeDFT, computeEFT
from computations.Priorities import getExitTask


def applyBSA(g, schedule: dict, verbose=False):
    """ Apply BSA to an already-computed schedule

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param schedule: Schedule computed, to improve using BSA
    :type schedule: dict[int, (int, float, float)]
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :return: A *possibly* improved schedule in format {task : [proc, est, eft],..}
    :rtype: dict[int, (int, float, float)]
    """
    q = g.graph['nbproc']
    procList = sorted(schedule.values(), key=lambda x: x[2], reverse=False)  # Reverse = true -> 10 d'abord
    procList = list(map(lambda x: x[0], procList))
    procList = list(dict.fromkeys(procList))
    initMakespan = schedule[getExitTask(g)][2]
    for p in range(q):
        if p not in procList:
            procList.append(p)
    for p in procList:  # TODO Check which one of those two is the most effective ...
        # for p in range(q):
        tasks = []
        for t in schedule:
            if schedule[t][0] == p:
                tasks.append(t)
        for t in tasks:
            allowedProc = []
            eft = schedule[t][2]
            est = schedule[t][1]
            scheduleBis = dict.copy(schedule)
            scheduleBis.pop(t)
            dft, unused = computeDFT(g, t, p, scheduleBis, verbose, estimate=False)
            if est > dft:
                for py in range(q):
                    if py == p:
                        continue
                    esty, efty = computeEFT(g, t, py, scheduleBis, verbose, insertion=True, estimate=False)
                    if efty < eft:
                        swap = True
                        for s in g.successors(t):
                            swap = swap and schedule[s][1] >= efty + commCost(g, t, s, py, schedule[s][0],
                                                                              verbose=False)
                        if swap:
                            allowedProc.append([py, esty, efty])
                            schedule = scheduleBis
                            schedule[t] = [py, esty, efty]
    endMakespan = schedule[getExitTask(g)][2]
    if endMakespan > initMakespan:
        raise Exception("BSA increases makespan ...")
    return schedule


def verifBSA(rs, r, verbose=False):
    """ Check over the schedule if using BSA really improve the performance

    :param rs: Sorted heuristics by (makespan, computation time)
    :type rs: str[]
    :param r: Full results of the extensive testing
    :type r: dict[int, (int, float, float)]
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :return: Analysis of BSA-related improvement in performance
    :rtype: str
    """
    totModif = 0
    cntModif = 0
    cntTot = 0
    totTps = 0
    result = ""
    for k in rs:
        if k.split(';')[-1] != "True":
            cntTot += 1
            rK = r[k]
            rB = r[k[:-len("False")] + "True"]
            totTps += (rK[1] - rB[1]) / (rK[1]) * 100
            if rK[0] != rB[0]:
                modif = (rK[0] - rB[0]) / (rK[0]) * 100
                cntModif += 1
                totModif += modif
                if verbose:
                    print("Result :", "\n", "-----------------------------", "\n", "Without BSA :", rK[0], '\n',
                          'With BSA :',
                          rB[0], '\n', 'Improvement of', modif, "%")
    result += "Mean improvement of " + str(round(totModif / (1 if cntModif == 0 else cntModif), 2)) + "% over " + str(
        cntModif) + " heuristics concerned.\n"
    result += "Mean improvement of " + str(round(totModif / cntTot, 2)) + "% over all " + str(
        cntTot) + " heuristics.\n"
    result += "Mean slowdown of " + str(-round(totTps / cntTot, 2)) + "% over " + str(cntTot) + " heuristics.\n"
    return result

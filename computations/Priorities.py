import math
from collections import defaultdict

from networkx import topological_sort

from computations.CommCost import *
from computations.CompCost import *
from computations.LBMatrix import *


def getCP(g, costFunction="mean", verbose=False):
    """ Compute Critical-Path of given graph

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param costFunction: Function used to compute computation cost ('mean', 'median', 'max', 'min')
    :type costFunction: str
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :return: Critical Path of **g**
    :rtype: str
    """
    computeRankU(g, costFunction=costFunction)
    computeRankD(g, costFunction=costFunction, add=True)
    entryTask = getEntryTask(g)
    exitTask = getExitTask(g)
    cpLength = g.graph['prio'][entryTask - 1]
    CP = [entryTask]
    currentNode = entryTask
    while currentNode != exitTask:
        ti = None
        for ti in g.successors(currentNode):
            if g.graph['prio'][ti - 1] == cpLength:
                break
        CP.append(ti)
        currentNode = ti
    if verbose:
        print("CP =", CP)
    return CP


def getExitTask(g, verbose=False):
    """ Compute if necessary the exit task of the graph, else just return it

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :return: Exit task of **g**
    :rtype: int
    """
    if 'exit' in g.graph:  # 5~10% performance improvement
        return g.graph['exit']
    for node in g.nodes:
        if len(list(g.successors(node))) == 0:
            if verbose:
                print("Exit task :", node)
            g.graph['exit'] = node
            return node
    return None


def getEntryTask(g, verbose=False):
    """ Compute if necessary the entry task of the graph, else just return it

        :param g: DAG to schedule
        :type g: networkx.DiGraph
        :param verbose: Print non-necessary information ?
        :type verbose: bool
        :return: Entry task of **g**
        :rtype: int
        """
    if 'entry' in g.graph:
        return g.graph['entry']
    for node in g.nodes:
        if (len(list(g.predecessors(node)))) == 0:
            if verbose:
                print("Entry task :", node)
            g.graph['entry'] = node
            return node
    return None


def computeRankU(g, costFunction="mean", verbose=False):
    """ Compute rku for every node of **g** and store it in g.graph['prio']

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param costFunction: Function used to compute meanCompCost and meanCommCost
    :type costFunction: str
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    """
    computeCompCost(g, costFunction, verbose)
    computeLB(g, costFunction, verbose)
    currentNode = getExitTask(g, verbose)
    entry = getEntryTask(g, verbose)
    rku = [-1] * len(g.nodes)
    toTreat = []
    while currentNode is not None:
        currentNodeRku = g.graph['meancompcost'][currentNode - 1]
        succs = list(g.successors(currentNode))
        if len(succs) > 0:
            currentNodeRku += max(map(lambda x: meanCommCost(g, currentNode, x) + rku[x - 1], succs))
        if verbose:
            print("Rku of", currentNode, currentNodeRku)
        rku[currentNode - 1] = currentNodeRku
        for p in g.predecessors(currentNode):
            isOk = True
            for s in g.successors(p):
                if rku[s - 1] == -1:
                    isOk = False
            if isOk:
                toTreat.append(p)
        if currentNode != entry:
            currentNode = toTreat[0]
            toTreat = list(dict.fromkeys(toTreat[1::]))  # To remove duplicates
        else:
            currentNode = None
    g.graph['prio'] = rku
    if verbose:
        print("rku : ", list(map(lambda x: round(x, 2), g.graph['prio'])))


def computeRankD(g, costFunction="mean", verbose=False, add=False, sub=False):
    """ Compute rkd for every node of **g** and store it in g.graph['prio']

        :param g: DAG to schedule
        :type g: networkx.DiGraph
        :param costFunction: Function used to compute meanCompCost and meanCommCost
        :type costFunction: str
        :param verbose: Print non-necessary information ?
        :type verbose: bool
        :param add: Add rkd to current prio ?
        :type add: bool
        :param sub: Subtract rkd to current prio ?
        :type sub: bool
        """
    computeCompCost(g, costFunction, verbose)
    computeLB(g, costFunction, verbose)
    currentNode = getEntryTask(g, verbose)
    exitTask = getExitTask(g, verbose)
    rkd = [-1] * len(g.nodes)
    toTreat = []
    while currentNode is not None:
        currentNodeRkd = 0
        preds = list(g.predecessors(currentNode))
        if len(preds) > 0:
            currentNodeRkd += max(
                list(map(lambda x: meanCommCost(g, x, currentNode) + rkd[x - 1] + g.graph['meancompcost'][x - 1],
                         preds)))
        if add:
            g.graph['prio'][currentNode - 1] += currentNodeRkd
        elif sub:
            g.graph['prio'][currentNode - 1] -= currentNodeRkd
        rkd[currentNode - 1] = currentNodeRkd
        for p in g.successors(currentNode):
            isOk = True
            for s in g.predecessors(p):
                if rkd[s - 1] == -1:
                    isOk = False
            if isOk:
                toTreat.append(p)
        if currentNode != exitTask:
            currentNode = toTreat[0]
            toTreat = list(dict.fromkeys(toTreat[1::]))
        else:
            currentNode = None
    if not add and not sub:
        g.graph['prio'] = rkd
        if verbose:
            print("rkd :", list(map(lambda x: round(x, 2), g.graph['prio'])))


def computeBIL(g, verbose=False):
    """ Compute BIL for every node and every proc of **g** and store it in g.graph['prio']

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    """
    currentNode = getExitTask(g, verbose)
    entry = getEntryTask(g, verbose)
    q = g.graph['nbproc']
    n = len(g.nodes)
    bil: list[list[float]] = []
    toTreat = []
    for i in range(n):
        bil.append([])
    while currentNode is not None:
        for proc in range(q):
            currentNodeBil = g.graph['costmatrix'][currentNode - 1][proc]
            succs = list(g.successors(currentNode))
            maxS = 0
            for s in succs:
                minP = math.inf
                for p in range(q):
                    succVal = bil[s - 1][p] + commCost(g, currentNode, s, proc, p, verbose=verbose)
                    if succVal < minP:
                        minP = succVal
                if minP > maxS:
                    maxS = minP
            currentNodeBil += maxS
            bil[currentNode - 1].append(currentNodeBil)

        for p in g.predecessors(currentNode):
            isOk = True
            for s in g.successors(p):
                if not bil[s - 1]:
                    isOk = False
            if isOk:
                toTreat.append(p)
        if currentNode != entry:
            currentNode = toTreat[0]
            toTreat = list(dict.fromkeys(toTreat[1::]))
        else:
            currentNode = None
    g.graph['prio'] = bil
    if verbose:
        print("Bil : ", g.graph['prio'])


def identifyCP(g, strategyPrio, verbose):
    """ Identify the CP of **g** using **strategyPrio**

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param strategyPrio: Prioritization strategy, affect the process of CP selection
    :type strategyPrio: str
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :return: The identified CP
    :rtype: list[int]
    """
    CP = []
    if strategyPrio == "rkuad":
        tk = getEntryTask(g)
        CPlen = round(g.graph['prio'][tk - 1], 3)
        while tk != getExitTask(g):
            tt = None
            CP.append(tk)
            for t in g.successors(tk):
                if round(g.graph['prio'][t - 1], 3) == CPlen:
                    tt = t
            tk = tt
        CP.append(getExitTask(g))
    return CP


def computeLevels(g, verbose=False):
    """ Compute level/depth for each node of **g** *id est*

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :return: Dict containing nodes for each level
    :rtype: dict[int, list[int]]
    """
    nodes = list(topological_sort(g))
    lvl = {nodes.pop(0): 0}
    while nodes:
        currentTask = nodes.pop(0)
        maxL = 0
        for i in g.predecessors(currentTask):
            if lvl[i] > maxL:
                maxL = lvl[i]
        lvl[currentTask] = maxL + 1
    res = defaultdict(list)
    for key, val in sorted(lvl.items()):
        res[val].append(key)
    if verbose:
        print(res)
    return res


def computeLC(g, lvl, verbose=False):
    """ Compute LC, *id est* Link Cost, for each node of **g**, and store it in g.graph['prio']

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param lvl: List of nodes per level of **g**
    :type lvl: dict[int, list[int]]
    :param verbose:
    :return: List of nodes sorted by LC
    :rtype: list[int]
    """
    LC = {}
    for level in sorted(lvl):
        for task in lvl[level]:
            if task != getExitTask(g, verbose):
                ULC = max(meanCommCost(g, task, succ) for succ in g.successors(task))
            else:
                ULC = 0
            if task != getEntryTask(g, verbose):
                DLC = max(meanCommCost(g, pred, task) for pred in g.predecessors(task))
                mLC = max(LC[pred] for pred in g.predecessors(task))
            else:
                DLC = mLC = 0

            LC[task] = mLC + ULC + DLC
    g.graph['prio'] = [LC[k] for k in sorted(LC)]
    nodes = []
    for level in sorted(lvl):
        for x in sorted(lvl[level], key=lambda y: LC[y]):
            nodes.append(x)
    return nodes

# def computeAEST(g, verbose, useOfMean=True, schedule = {}):
#     print(schedule)
#     currentNode = getEntryTask(g, verbose)
#     exit = getExitTask(g, verbose)
#     q = g.graph['nbproc']
#     n = len(g.nodes)
#     AEST: list[list[float]] = []
#     toTreat = []
#     DCPL = 0
#     for i in range(n):
#         AEST.append([])
#     while currentNode is not None:
#         for proc in range(q):
#             preds = list(g.predecessors(currentNode))
#             maxP = 0
#             for p in preds:
#                 if not p in schedule:
#                     minP = math.inf
#                     for proc2 in range(q):
#                         predVal = AEST[p - 1][proc2] + (
#                             g.graph['meancompcost'][p - 1] if useOfMean else g.graph['costmatrix'][p - 1][
#                                 proc2]) + commCost(g, p, currentNode, proc2, proc)
#                         #print(currentNode, p, predVal, proc, proc2)
#                         if predVal < minP:
#                             minP = predVal
#
#                 else:
#                     #print("Use of schedule for", currentNode, p)
#                     proc2 = schedule[p][0]
#                     minP = AEST[p-1][proc2] + g.graph['costmatrix'][p-1][proc2] + commCost(g, p, currentNode, proc2
#                                                                                             , proc)
#                     #print(minP,"for",currentNode,"on proc",proc)
#                 if minP > maxP:
#                     maxP = minP
#             currentNodeAEST = maxP
#             AEST[currentNode - 1].append(currentNodeAEST)
#             DCPLCandidate = AEST[currentNode - 1][proc] + (
#                 g.graph['meancompcost'][currentNode - 1] if useOfMean
#                 else g.graph['costmatrix'][currentNode - 1][proc])
#             DCPL = max(DCPLCandidate, DCPL)
#         toTreat += list(g.successors(currentNode))
#         if currentNode != exit:
#             currentNode = toTreat[0]
#             toTreat = list(dict.fromkeys(toTreat[1::]))
#         else:
#             currentNode = None
#     g.graph['prio'] = AEST
#     if verbose:
#         print("AEST :", g.graph['prio'])
#     return DCPL


# def computeALST(g, DCPL, verbose, useOfMean=True, schedule = {}):
#     currentNode = getExitTask(g, verbose)
#     entry = getEntryTask(g, verbose)
#     q = g.graph['nbproc']
#     n = len(g.nodes)
#     ALST: list[list[float]] = []
#     AEST = g.graph['prio']
#     toTreat = []
#     for i in range(n):
#         ALST.append([])
#     while currentNode is not None:
#         for proc in range(q):
#             succs = list(g.successors(currentNode))
#             w = (
#                 g.graph['meancompcost'][currentNode - 1] if useOfMean
#                 else g.graph['costmatrix'][currentNode - 1][proc])
#             minS = DCPL - w
#             for s in succs:
#                 if not s in schedule:
#                     maxS = 0
#                     for proc2 in range(q):
#                         predVal = ALST[s - 1][proc2] - commCost(g, currentNode, s, proc, proc2) - w
#                         if predVal > maxS:
#                             maxS = predVal
#                 else:
#                     proc2 = schedule[s][0]
#                     maxS = ALST[s-1][proc2] - commCost(g, currentNode, proc, proc2) - w
#                 if maxS < minS:
#                     minS = maxS
#             currentNodeALST = minS
#             ALST[currentNode - 1].append(currentNodeALST)
#         toTreat += list(g.predecessors(currentNode))
#         if currentNode != entry:
#             currentNode = toTreat[0]
#             toTreat = list(dict.fromkeys(toTreat[1::]))
#         else:
#             currentNode = None
#     for i in range(len(AEST)):
#         for j in range(len(AEST[i])):
#             AEST[i][j] -= ALST[i][j]
#     if verbose:
#         print("ALST :", ALST)
#         print("prio :", g.graph['prio'])

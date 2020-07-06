import math
from typing import Dict, Tuple

from computations.BIMStarValue import computeBIMStar
from computations.CompCost import computeCompCost
from computations.DynamicLevel import DL, GDL
from computations.EarliestTimes import *
from computations.LBMatrix import computeLB
from computations.Lookahead import getLookAheadFun
from computations.Priorities import identifyCP
from help.Printer import printSchedule


def updateReadyTasks(g, readyTasks, nodes, scheduledNode, deletion=True, verbose=False):
    """ Update the list of ready tasks after scheduling of a node

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param readyTasks: List of ready tasks
    :type readyTasks: list[int]
    :param nodes: Ordered list of nodes
    :type nodes: list[int]
    :param scheduledNode: Node scheduled
    :type scheduledNode: int
    :param deletion: Should we delete readyTask from nodes ?
    :type deletion: bool
    :param verbose: Print non-necessary information ?
    :type verbose: bool

    :rtype: None
    """
    for n in g.successors(scheduledNode):
        ready = True
        for p in g.predecessors(n):
            if p in readyTasks or p in nodes:
                ready = False
        if ready:
            if n not in readyTasks:
                readyTasks.append(n)
            if deletion and n in nodes:
                nodes.remove(n)
    if verbose:
        print("Ready task list after update :", readyTasks)


def computeCurrentNodeBIM(g, readyTasks, schedule, verbose=False, insertion=True):
    """ Determine node to schedule using the BIM policy

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param readyTasks: List of ready tasks
    :type readyTasks: list[int]
    :param schedule: Schedule at this point
    :type schedule: dict[int, (int, float, float)]
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :param insertion: Use of insertion policy ?
    :type insertion: bool
    :return: Node to schedule
    :rtype: int
    """
    q = g.graph['nbproc']
    k = len(readyTasks)
    currentNode = 0
    prio = g.graph['prio']
    n = len(prio)
    bim = []
    for i in range(n):
        bim.append([])

    m = math.inf
    for t in readyTasks:
        for p in range(q):
            est, tmp = computeEFT(g=g, node=t, proc=p, schedule=schedule, verbose=verbose, insertion=insertion)
            if isinstance(prio[t - 1], list):
                bim[t - 1].append(prio[t - 1][p] + est)
            else:
                bim[t - 1].append(prio[t - 1] + est)
        sortedBIM = sorted(bim[t - 1])
        if k > len(sortedBIM):
            kmBIM = sortedBIM[-1]
        else:
            kmBIM = sortedBIM[k - 1]
        if kmBIM < m:
            m = kmBIM
            currentNode = t
    return currentNode


def findBestProcEFT(g, currentNode, schedule, desc, verbose, insertion, useEST, nodes):
    """ Find the best proc to schedule **currentNode** according to a EFT policy and schedule **currentNode** to this
    proc

    :param nodes: List of nodes sorted
    :type nodes: list[int]
    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param currentNode: Node to schedule
    :type currentNode: int
    :param schedule: Schedule at this point
    :type schedule: dict[int, (int, float, float)]
    :param desc: Lookahead strategy
    :type desc: str
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :param insertion: Use of insertion policy ?
    :type insertion: bool
    :param useEST: Use EST to compare instead of EFT ?
    :type useEST: bool
    """
    if nodes is None:
        nodes = []
    q = g.graph['nbproc']
    um = m = math.inf
    umm = mm = math.inf
    pm = 0
    uest = ueft = 0
    for proc in range(q):
        est, eft = computeEFT(g=g, node=currentNode, proc=proc, schedule=schedule, verbose=verbose,
                              insertion=insertion)
        if useEST:
            uest = getLookAheadFun(desc)(g, currentNode, proc, nodes, "EST", schedule, est)
        else:
            ueft = getLookAheadFun(desc)(g, currentNode, proc, nodes, "EFT", schedule, eft)
        if verbose:
            print("Attempt on scheduling node ", currentNode, "on proc", proc + 1, " -> est =", est, " and eft =",
                  eft)
        if (not useEST and ueft < um) or (useEST and uest < umm):
            um = ueft
            umm = uest
            m = eft
            mm = est
            pm = proc
    if verbose:
        print("Choice of proc :", pm + 1)
    schedule[currentNode] = (pm, mm, m)


def placeEFTBIM(g, nodes, desc=None, verbose=False, insertion=True):
    """ Use EFT policy along with a BIM selection of node to schedule node on processors

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param nodes: Ordered list of nodes
    :type nodes: list[int]
    :param desc: Lookahead strategy
    :type desc: str
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :param insertion: Use of insertion policy ?
    :type insertion: bool
    :return: A corresponding schedule in format {task : [proc, est, eft],..}
    :rtype: dict[int, (int, float, float)]
    """
    schedule = {}
    n = len(nodes)
    readyTasks = [nodes[0]]
    nodes = nodes[1::]
    bim = []
    for i in range(n):
        bim.append([])
    k = len(readyTasks)
    while k > 0:
        currentNode = computeCurrentNodeBIM(g, readyTasks, schedule, verbose=verbose, insertion=insertion)
        readyTasks.remove(currentNode)
        findBestProcEFT(g, currentNode, schedule, desc, verbose, insertion, False, nodes)
        updateReadyTasks(g, readyTasks, nodes, currentNode)
        k = len(readyTasks)
    return schedule


def placeEFT(g, nodes, desc=None, verbose=False, insertion=True):
    """ Use EFT policy (minimize Earliest Finish Time) to schedule node on processors

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param nodes: Ordered list of nodes
    :type nodes: list[int]
    :param desc: Lookahead strategy
    :type desc: str
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :param insertion: Use of insertion policy ?
    :type insertion: bool
    :return: A corresponding schedule in format {task : [proc, est, eft],..}
    :rtype: dict[int, (int, float, float)]
    """
    if verbose:
        print("Nodes :", nodes)
    schedule = {}
    while len(nodes) > 0:
        currentNode = nodes[0]
        nodes = nodes[1::]
        findBestProcEFT(g, currentNode, schedule, desc, verbose, insertion, False, nodes)
    if verbose:
        schedulebis = {}
        for s in schedule:
            schedulebis[s] = [schedule[s][0] + 1, schedule[s][1], schedule[s][2]]
        print(schedulebis)
    return schedule


def placeMET(g, nodes, desc=None, verbose=False, insertion=True):
    """ Use MET (each task to best proc) policy to schedule node on processors

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param nodes: Ordered list of nodes
    :type nodes: list[int]
    :param desc: Lookahead strategy
    :type desc: str
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :param insertion: Use of insertion policy ?
    :type insertion: bool
    :return: A corresponding schedule in format {task : [proc, est, eft],..}
    :rtype: dict[int, (int, float, float)]
    """
    schedule: Dict[int, Tuple[int, float, float]] = {}
    q = g.graph['nbproc']
    while len(nodes) > 0:
        m = math.inf
        mm = 0
        mmm = 0
        pm = 0
        currentNode = nodes[0]
        nodes = nodes[1::]
        for proc in range(q):
            diff = g.graph['costmatrix'][currentNode - 1][proc]
            diff = getLookAheadFun(desc)(g, currentNode, proc, nodes, "MET", schedule, diff)
            est, eft = computeEFT(g=g, node=currentNode, proc=proc, schedule=schedule, verbose=verbose,
                                  insertion=insertion)
            if diff < m or (diff == m and eft < mmm):
                m = g.graph['costmatrix'][currentNode - 1][proc]
                mm = est
                mmm = eft
                pm = proc
        if verbose:
            print("Choice of proc :", pm + 1)
        schedule[currentNode] = (pm, mm, mmm)
    if verbose:
        schedulebis = {}
        for s in schedule:
            schedulebis[s] = [schedule[s][0] + 1, schedule[s][1], schedule[s][2]]
        print(schedulebis)
    return schedule


def placeOLB(g, nodes, desc=None, verbose=False, insertion=True):
    """ Use OLB (balancing work load) policy to schedule node on processors

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param nodes: Ordered list of nodes
    :type nodes: list[int]
    :param desc: Lookahead strategy
    :type desc: str
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :param insertion: Use of insertion policy ?
    :type insertion: bool
    :return: A corresponding schedule in format {task : [proc, est, eft],..}
    :rtype: dict[int, (int, float, float)]
        """
    schedule = {}
    while len(nodes) > 0:
        currentNode = nodes[0]
        nodes = nodes[1::]
        findBestProcEFT(g, currentNode, schedule, desc, verbose, insertion, True, nodes)
    if verbose:
        schedulebis = {}
        for s in schedule:
            schedulebis[s] = [schedule[s][0] + 1, schedule[s][1], schedule[s][2]]
        print(schedulebis)
    return schedule


def findBestProcBIMStar(g, currentNode, schedule, k, desc, verbose, insertion, nodes):
    """ Find the best proc to schedule **currentNode** according to the BIM* policy and schedule **currentNode** to this
    proc

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param currentNode: Node to schedule
    :type currentNode: int
    :param schedule: Schedule at this point
    :type schedule: dict[int, (int, float, float)]
    :param k: Number of ready tasks at this point
    :type k: int
    :param desc: Lookahead strategy
    :type desc: str
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :param insertion: Use of insertion policy ?
    :type insertion: bool
    :param nodes: List of nodes sorted
    :type nodes: list[int]
    """
    q = g.graph['nbproc']
    m = math.inf
    mm = 0
    pm = 0
    mmm = 0
    for proc in range(q):
        bims, est, eft = computeBIMStar(g, currentNode, proc, schedule, k, verbose, insertion)
        bims = getLookAheadFun(desc)(g, currentNode, proc, nodes, "BIM*", schedule, bims)
        if bims <= m:
            if bims < m or eft < mmm:
                m = bims
                mm = est
                mmm = eft
                pm = proc
    if verbose:
        print("Choice of proc :", pm + 1)
    schedule[currentNode] = (pm, mm, mmm)


def placeBIMStar(g, nodes, desc, verbose, insertion):
    """ Use BIM* policy to schedule node on processors

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param nodes: Ordered list of nodes
    :type nodes: list[int]
    :param desc: Lookahead strategy
    :type desc: str
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :param insertion: Use of insertion policy ?
    :type insertion: bool
    :return: A corresponding schedule in format {task : [proc, est, eft],..}
    :rtype: dict[int, (int, float, float)]
    """
    schedule = {}
    readyTasks = [nodes[0]]
    while len(nodes) > 0:
        k = len(readyTasks)
        currentNode = nodes[0]
        nodes = nodes[1::]
        findBestProcBIMStar(g, currentNode, schedule, k, desc, verbose, insertion, nodes)
        readyTasks.remove(currentNode)
        updateReadyTasks(g, readyTasks, nodes, currentNode, deletion=False)
    if verbose:
        schedulebis = {}
        for s in schedule:
            schedulebis[s] = [schedule[s][0] + 1, schedule[s][1], schedule[s][2]]
        print(schedulebis)
    return schedule


def placeBIMStarBIM(g, nodes, desc, verbose, insertion):
    """ Use of BIM* policy along with a BIM selection of node to schedule node on processors

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param nodes: Ordered list of nodes
    :type nodes: list[int]
    :param desc: Lookahead strategy
    :type desc: str
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :param insertion: Use of insertion policy ?
    :type insertion: bool
    :return: A corresponding schedule in format {task : [proc, est, eft],..}
    :rtype: dict[int, (int, float, float)]
    """
    schedule = {}
    bim = []
    for _ in nodes:
        bim.append([])
    readyTasks = [nodes[0]]
    nodes = nodes[1::]
    k = len(readyTasks)
    while k > 0:
        currentNode = computeCurrentNodeBIM(g, readyTasks, schedule, verbose=verbose, insertion=insertion)
        if verbose:
            print("Current node :", currentNode)
        k = len(readyTasks)
        readyTasks.remove(currentNode)
        findBestProcBIMStar(g, currentNode, schedule, k, desc, verbose, insertion, nodes)
        updateReadyTasks(g, readyTasks, nodes, currentNode)
        k = len(readyTasks)
    if verbose:
        schedulebis = {}
        for s in schedule:
            schedulebis[s] = [schedule[s][0] + 1, schedule[s][1], schedule[s][2]]
        print(schedulebis)
    return schedule


def placeDL(g, nodes, desc, verbose, insertion, costFunction="mean"):
    """ Use DL policy to schedule node on processors

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param nodes: Ordered list of nodes
    :type nodes: list[int]
    :param desc: Lookahead strategy
    :type desc: str
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :param insertion: Use of insertion policy ?
    :type insertion: bool
    :param costFunction: Function used to simplify comp/comm cost
    :type costFunction: str
    :return: A corresponding schedule in format {task : [proc, est, eft],..}
    :rtype: dict[int, (int, float, float)]
    """
    computeCompCost(g, costFunction, verbose)
    computeLB(g, costFunction, verbose)
    schedule = {}
    q = g.graph['nbproc']
    readyTasks = [nodes[0]]
    while nodes:
        i = None
        m = -math.inf
        pm = None
        for n in readyTasks:
            for p in range(q):
                dl = DL(g, n, p, schedule, desc, verbose, insertion, nodes, False)
                if dl > m:
                    m = dl
                    i = n
                    pm = p
        placeNode(g, i, pm, schedule, nodes, readyTasks, verbose, insertion)
    if verbose:
        printSchedule(schedule)
    return schedule


def placeDLBIM(g, nodes, desc, verbose, insertion, costFunction="mean"):
    """Use DL policy along with a BIM selection of nodes to schedule node on processors

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param nodes: Ordered list of nodes
    :type nodes: list[int]
    :param desc: Lookahead strategy
    :type desc: str
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :param insertion: Use of insertion policy ?
    :type insertion: bool
    :param costFunction: Function used to simplify comp/comm cost
    :type costFunction: str
    :return: A corresponding schedule in format {task : [proc, est, eft],..}
    :rtype: dict[int, (int, float, float)]
    """
    computeCompCost(g, costFunction, verbose)
    computeLB(g, costFunction, verbose)
    schedule = {}
    q = g.graph['nbproc']
    readyTasks = [nodes[0]]
    while nodes:
        m = -math.inf
        pm = None
        currentNode = computeCurrentNodeBIM(g, readyTasks, schedule, verbose, insertion)
        for p in range(q):
            dl = DL(g, currentNode, p, schedule, desc, verbose, insertion, nodes, False)
            if dl > m:
                m = dl
                pm = p
        placeNode(g, currentNode, pm, schedule, nodes, readyTasks, verbose, insertion)
    if verbose:
        printSchedule(schedule)
    return schedule


def placeNode(g, currentNode, proc, schedule, nodes, readyTasks, verbose, insertion):
    """ Place node in schedule, and update ready tasks list

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param currentNode: Node to schedule
    :type currentNode: int
    :param proc: Processor to schedule **currentNode** on
    :type proc: int
    :param schedule: Schedule at this point
    :type schedule: dict[int, (int, float, float)]
    :param nodes: Ordered list of nodes
    :type nodes: list[int]
    :param readyTasks: List of ready tasks
    :type readyTasks: list[int]
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :param insertion: Use of insertion policy ?
    :type insertion: bool
    :rtype: None
    """
    if verbose:
        print("Choice of proc :", proc + 1)
    est, eft = computeEFT(g, currentNode, proc, schedule, verbose, insertion)
    schedule[currentNode] = (proc, est, eft)
    nodes.remove(currentNode)
    readyTasks.remove(currentNode)
    updateReadyTasks(g, readyTasks, nodes, currentNode, deletion=False, verbose=verbose)


def placeGDLBIM(g, nodes, desc, verbose, insertion, costFunction="mean"):
    """ Use GDL policy along with a BIM selection  to schedule node on processors

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param nodes: Ordered list of nodes
    :type nodes: list[int]
    :param desc: Lookahead strategy
    :type desc: str
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :param insertion: Use of insertion policy ?
    :type insertion: bool
    :param costFunction: Function used to simplify comp/comm cost
    :type costFunction: str
    :return: A corresponding schedule in format {task : [proc, est, eft],..}
    :rtype: dict[int, (int, float, float)]
    """
    computeCompCost(g, costFunction, verbose)
    computeLB(g, costFunction, verbose)
    schedule = {}
    readyTasks = [nodes[0]]
    while nodes:
        i = None
        m = -math.inf
        pm = None
        for n in readyTasks:
            dl, p = GDL(g, n, schedule, desc, verbose, insertion)
            if dl > m:
                m = dl
                i = n
                pm = p
        placeNode(g, i, pm, schedule, nodes, readyTasks, verbose, insertion)
    if verbose:
        printSchedule(schedule)
    return schedule


def placeGDL(g, nodes, desc, verbose, insertion, costFunction="mean"):
    """Use GDL policy to schedule node on processors

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param nodes: Ordered list of nodes
    :type nodes: list[int]
    :param desc: Lookahead strategy
    :type desc: str
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :param insertion: Use of insertion policy ?
    :type insertion: bool
    :param costFunction: Function used to simplify comp/comm cost
    :type costFunction: str
    :return: A corresponding schedule in format {task : [proc, est, eft],..}
    :rtype: dict[int, (int, float, float)]
    """
    computeCompCost(g, costFunction, verbose)
    computeLB(g, costFunction, verbose)
    schedule = {}
    readyTasks = [nodes[0]]
    while nodes:
        currentNode = computeCurrentNodeBIM(g, readyTasks, schedule, verbose, insertion)
        dl, p = GDL(g, currentNode, schedule, desc, verbose, insertion, nodes)
        placeNode(g, currentNode, p, schedule, nodes, readyTasks, verbose, insertion)
    if verbose:
        printSchedule(schedule)
    return schedule


# def placeByDCP(g, nodes, verbose, insertion, ):
#    schedule = {}
#    exitTask = getExitTask(g)
#    q = g.graph['nbproc']
#    while nodes:
#        currentNode = nodes[0]
#        nodes = nodes[1:]
#        nextNode = None if currentNode == exitTask else [s for s in nodes if s in g.successors(currentNode)][0]
#        minSum = math.inf
#        minSched = None
#        for proc in range(q):
#            estI, eftI = computeEFT(g, currentNode, proc, schedule, verbose, insertion)
#            schedule[currentNode] = [proc, estI, eftI]
#            estN, eftN = computeEFT(g, nextNode, proc, schedule, verbose, insertion, estimate=True)
#            if eftI + eftN < minSum:
#                minSum = eftI + eftN
#                minSched = [proc, estI, eftI]
#        schedule[currentNode] = minSched
#    if verbose:
#        print(schedule)
#    return schedule


# def placeByDPS(g, nodes, strategyPrio, verbose, insertion):
#    schedule = {}
#    while len(nodes) > 0:
#        nodes = 0
#        currentNode = nodes[0]
#        nodes = nodes[1::]
#        findBestProcEFT(g, currentNode, schedule, verbose, insertion)
#    if verbose:
#        schedulebis = {}
#        for s in schedule:
#            schedulebis[s] = [schedule[s][0] + 1, schedule[s][1], schedule[s][2]]
#        print(schedulebis)
#    return schedule


def aux(g, CP, serialOrder, tx):
    """ Construct the serial order of nodes using the CP

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param CP: Critical Path of **g**
    :type CP: list[int]
    :param serialOrder: Serial Order to complete
    :type serialOrder: list[int]
    :param tx: Node to treat
    :type tx: int
    """
    if all(x in serialOrder for x in g.predecessors(tx)):
        serialOrder.append(tx)
        if tx in CP:
            CP.pop(0)
            if CP:
                aux(g, CP, serialOrder, CP[0])
    else:
        for t in g.predecessors(tx):
            if t not in serialOrder:
                aux(g, CP, serialOrder, t)
        aux(g, CP, serialOrder, tx)


def placeSerial(g, strategyPrio, verbose):
    """ Use serial order to schedule node on processors

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param strategyPrio: Priority-computations strategy
    :type strategyPrio: str
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :return: A corresponding schedule in format {task : [proc, est, eft],..}
    :rtype: dict[int, (int, float, float)]
    """
    CP = identifyCP(g, strategyPrio, verbose)
    if not CP:
        return None
    if verbose:
        print("CP :", CP)
    serialOrder = [CP[0]]
    CP.pop(0)
    tx = CP[0]
    aux(g, CP, serialOrder, tx)
    for t in g.nodes:
        if t not in serialOrder:
            serialOrder.append(t)
    pivot = None
    makespan = math.inf
    for p in range(g.graph['nbproc']):
        ms = sum(g.graph['costmatrix'][x - 1][p] for x in serialOrder)
        if ms < makespan:
            pivot = p
            makespan = ms
    if verbose:
        print("Pivot :", pivot)
    schedule: Dict[int, Tuple[int, float, float]] = {}
    for t in serialOrder:
        est, eft = computeEFT(g, t, pivot, schedule, verbose, False)
        schedule[t] = (pivot, est, eft)
    return schedule

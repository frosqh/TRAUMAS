from computations.CommCost import *


def computeEFT(g, node, proc, schedule, verbose=False, insertion=False, estimate=False):
    """ Compute Earliest Finish Time for a given node on a given proc according to a given schedule

    :param g: DAG used
    :type g: networkx.DiGraph
    :param node: Node to try scheduling
    :type node: int
    :param proc: Proc to schedule **node** on
    :type proc: int
    :param schedule: Tasks already scheduled to this point
    :type schedule: dict[int, (int, float, float)]
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :param insertion: Use of insertion-based policy ?
    :type insertion: bool
    :param estimate: Do we know the scheduling of all predecessors ? #TODO Test this
    :type estimate: bool
    :return: EST and EFT for given node
    :rtype: (float,float)
    """
    if node is None:
        return 0, 0
    dft, onproc = computeDFT(g, node, proc, schedule, verbose, estimate)
    scheduled = False
    est = 0
    w = g.graph['costmatrix'][node - 1][proc]
    if insertion:
        for i in range(len(onproc)-1):
            if onproc[i + 1][1] <= dft and onproc[i][0] - dft >= w and onproc:
                scheduled = True
                est = dft
                break
    if not scheduled:
        if len(onproc) > 0:
            est = max(max(map(lambda x: x[1], onproc)), dft)
        else:
            est = dft
    return est, est + w


def computeDFT(g, node, proc, schedule, verbose=False, estimate=False):
    """ Compute Data Finish Time for a given node on a given proc according to a given schedule (id est time of
    arrival of every communications from predecessors)

    :param g: DAG used
    :type g: networkx.DiGraph
    :param node: Node to try scheduling
    :type node: int
    :param proc: Proc to schedule **node** on
    :type proc: int
    :param schedule: Tasks already scheduled to this point
    :type schedule: dict[int, (int, float, float)]
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :param estimate: Do we know the scheduling of all predecessors ? #TODO Test this
    :type estimate: bool
    :return: DFT and list of tasks on proc **proc**
    :rtype: (float,list[list[int]])
    """
    if node is None:
        return 0, 0
    onproc = []
    DFT = 0
    for pred in g.predecessors(node):
        if pred in schedule or not estimate:
            AFT = schedule[pred][2] + commCost(g, pred, node, schedule[pred][0], proc)
            if AFT > DFT:
                DFT = AFT
    for c in schedule:
        if schedule[c][0] == proc:
            onproc.append((schedule[c][1], schedule[c][2]))
    onproc = sorted(onproc, key=lambda x: x[0], reverse=True)
    if verbose:
        print("DFT of task", node, ":", DFT, ". On proc :", onproc)
    return DFT, onproc

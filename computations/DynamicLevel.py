import math

from computations.EarliestTimes import computeEFT
from computations.Lookahead import getLookAheadFun


def DL(g, i, m, schedule, desc=None, verbose=False, insertion=False, nodes=None, isGDL=False, estimate=False):
    """ Compute the Dynamic Level of a given node on a given schedule

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param i: Task to schedule
    :type i: int
    :param m: Proc to schedule **i** on
    :type m: int
    :param schedule: Schedule at this point
    :type schedule: dict[int, (int, float, float)]
    :param desc: Lookahead strategy
    :type desc: str
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :param insertion: Use of insertion policy ?
    :type insertion: bool
    :param nodes: List of nodes sorted
    :type nodes: list[int]
    :param isGDL: Using GDL or DL ?
    :type isGDL: bool
    :return: DL(i, m, schedule)
    :rtype: float
    """
    if nodes is None:
        nodes = []
    rku = g.graph['prio'][i - 1]
    if isinstance(rku, list):  # In case of more precise priority, use rku[m] instead of rku*
        rku = rku[m]
    est = computeEFT(g, i, m, schedule, verbose=verbose, insertion=insertion, estimate=estimate)[0]
    wi = g.graph['meancompcost'][i - 1]
    wim = g.graph['costmatrix'][i - 1][m]
    dl = rku - est + wi - wim
    return getLookAheadFun(desc)(g, i, m, nodes, "DL", schedule, dl)


def C(g, i, m, schedule, verbose=False, insertion=False):
    """ Compute the C term of GDL *id est* the cost in not scheduling a node on its preferred processor

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param i: Node to schedule
    :type i: int
    :param m: Preferred processor of **i**
    :type m: int
    :param schedule: Schedule at this point
    :type schedule: dict[int, (int, float, float)]
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :param insertion: Use of insertion policy ?
    :type insertion: bool
    :return: C(i, m)
    :rtype: float
    """
    dl = DL(g, i, m, schedule, verbose=verbose, insertion=insertion)
    if g.graph['nbproc'] > 1:
        return dl - max(
            [DL(g, i, n, schedule, verbose=verbose, insertion=insertion) for n in range(g.graph['nbproc']) if n != m])
    return dl


def GDL(g, i, schedule, desc, verbose=False, insertion=False, nodes=None):
    """ Compute Generalized Dynamic Level of a given node on a given schedule

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param i: Task to schedule
    :type i: int
    :param schedule: Schedule at this point
    :type schedule: dict[int, (int, float, float)]
    :param desc: Lookahead strategy
    :type desc: str
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :param insertion: Use of insertion policy ?
    :type insertion: bool
    :return: GDL(i, schedule)
    :rtype: float
    """
    # GDL de base, peut-être capable de généraliser le résultat ici
    # en utilisant PLAC(ti,pm*) - maxPLAC(ti,pn) + PLAC(ti,pm*) de manière générale, et pas juste pour DL ...
    pm = None
    m = -math.inf
    for p in range(g.graph['nbproc']):
        dl = DL(g, i, p, schedule, desc=desc, verbose=verbose, insertion=insertion, nodes=nodes, isGDL=True)
        if dl > m:
            m = dl
            pm = p
    return m + C(g, i, pm, schedule, verbose=False, insertion=False), pm

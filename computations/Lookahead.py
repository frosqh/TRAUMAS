import math

from computations.BIMStarValue import computeBIMStar
from computations.CommCost import commCost, meanCommCost
from computations.EarliestTimes import computeEFT
from exceptions.StrategyLookAheadException import StrategyLookAheadException


def F(g, i, j, m):
    """ Compute the F term of DLS *id est* how quickly succ(i) can be completed on any other processor than PE(i)

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param i: Task to schedule
    :type i: int
    :param j: Descendant to which **i** passes the most data
    :type j: int
    :param m: Processor on which is scheduled **i**
    :type m: int
    :return: F(i, j, m)
    :rtype: float
    """
    q = g.graph['nbproc']
    f = math.inf
    if m is None:
        f = meanCommCost(g, i, j) + g.graph['meancompcost'][j - 1]
    else:
        for p in range(q):
            fp = commCost(g, i, j, m, p) + g.graph['costmatrix'][j - 1][p]
            if fp < f:
                f = fp
    return f


def DC(g, i, m):
    """ Compute the DC term of DLS *id est* a Descendant Consideration term

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param i: Task to schedule
    :type i: int
    :param m: Proc to schedule **i** on
    :type m: int
    :return: DC(i,m)
    :rtype: float
    """
    ma = 0
    j = None
    for s in g.successors(i):
        if g.edges[i, s]['weight'] > ma:
            ma = g.edges[i, s]['weight']
            j = s
    if j is None:
        return 0
    return g.graph['meancompcost'][j - 1] - F(g, i, j, m)


def DLSDC(g, i, m, nodes, placeStrat, schedule, placeValue):
    """ Compute and add the Descendant Consideration term to the current placement value

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param i: Task to schedule
    :type i: int
    :param m: Current scheduling proc for **i**
    :type m: int
    :param placeValue: Current placement value
    :type placeValue: float
    :return: Final placement value
    :rtype: float
    """
    return placeValue + DC(g, i, m)


def DCP(g, i, m, nodes, placeStrat, schedule, placeValue):
    """ Compute the DCP lookahead strategy

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param i: Task to schedule
    :type i: int
    :param m: Current scheduling proc for **i**
    :type m: int
    :param placeValue: Current placement value
    :type placeValue: float
    :return: Final placement value
    :rtype: float
    """
    secondValue = 0
    if not nodes:
        return placeValue
    nextNode = [x for x in nodes if x in g.successors(i)]
    if not nextNode:
        return placeValue
    nextNode = nextNode[0]
    if placeStrat == "EFT":
        secondValue = computeEFT(g, nextNode, m, schedule, verbose=False, insertion=True, estimate=True)[1]
    elif placeStrat == "BIM*":
        secondValue = computeBIMStar(g, nextNode, m, schedule, 0, verbose=False, insertion=True, estimate=True)[0]
    elif placeStrat == "EST":
        secondValue = computeEFT(g, nextNode, m, schedule, verbose=False, insertion=True, estimate=True)[0]
    elif placeStrat == "MET":
        secondValue = g.graph['costmatrix'][i][m]
    elif placeStrat == "DL":
        from computations.DynamicLevel import DL
        secondValue = DL(g, nextNode, m, schedule, desc="", verbose=False, insertion=True, nodes=[], isGDL=False,
                         estimate=True)
    else:
        raise Exception(f"{placeStrat} not implemented yet")
    return placeValue + secondValue

    # return 0


def NOP(*args):
    """ Return the placement value passed in parameters, doing nothing

    :param args: Set of params, should end by the current placement value
    :type args: List[Any, ..., float]
    :return: Current placement value
    :rtype: float
    """
    return args[-1]


def getLookAheadFun(name):
    """ Return the function associated with the name stored in **name**

    :param name: Lookahead strategy to apply
    :type name: str
    :return: The function to run to compute the actual placement value
    :rtype: (networkx.DiGraph, int, int, list[int], str, dict[int, (int, float, float)], float) -> float
    """
    if not name:
        return NOP
    elif name == "DLS/DC":
        return DLSDC
    elif name == "DCP":
        return DCP
    else:
        raise StrategyLookAheadException(name)

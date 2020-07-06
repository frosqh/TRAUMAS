from numpy import mean, median

from computations.Priorities import computeRankU, computeRankD, computeLB, computeLevels, computeLC, computeBIL


def execRKU(g, costFunction="mean", verbose=False):
    """ Use rku policy to compute priority

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param costFunction: Function used to simplify comp/comm cost ('mean', 'median', 'maxmax', 'minmin',\
    'minmax', 'maxmin')
    :type costFunction: str
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :return: List of nodes sorted according to rku
    :rtype: list[int]
    """
    computeRankU(g, costFunction=costFunction, verbose=verbose)
    nodes = g.nodes
    nodes = sorted(nodes, key=lambda x: g.graph['prio'][x - 1], reverse=True)  # Ties broken randomly
    return nodes


# def execDCP(g, costFunction="mean", verbose=False):
#     computeCompCost(g, costFunction, verbose)
#     computeLB(g, costFunction, verbose)
#     DCPL = computeAEST(g, verbose)
#     if verbose:
#         print("DCPL =", DCPL)
#     computeALST(g, DCPL, verbose)
#     CP = [i + 1 for i in range(len(g.graph['prio'])) if g.graph['prio'][i][0] == 0]
#     print(CP)
#     return CP


def execRKD(g, costFunction="mean", verbose=False):
    """ Use rkd policy to compute priority

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param costFunction: Function used to simplify comp/comm cost ('mean', 'median', 'maxmax', 'minmin',\
    'minmax', 'maxmin')
    :type costFunction: str
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :return: List of nodes sorted according to rku
    :rtype: list[int]
    """
    computeRankD(g, costFunction=costFunction, verbose=verbose)
    nodes = g.nodes
    nodes = sorted(nodes, key=lambda x: g.graph['prio'][x - 1], reverse=False)  # Ties broken randomly
    return nodes


def execRKUSD(g, costFunction="mean", verbose=False):
    """ Use rku-rkd policy to compute priority

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param costFunction: Function used to simplify comp/comm cost ('mean', 'median', 'maxmax', 'minmin',\
    'minmax', 'maxmin')
    :type costFunction: str
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :return: List of nodes sorted according to rku
    :rtype: list[int]
    """
    computeRankU(g, costFunction=costFunction, verbose=verbose)
    computeRankD(g, costFunction=costFunction, verbose=verbose, sub=True)
    nodes = g.nodes
    nodes = sorted(nodes, key=lambda x: g.graph['prio'][x - 1], reverse=True)  # Ties broken randomly
    return nodes


def execRKUAD(g, costFunction="mean", verbose=False):
    """ Use rku+rkd policy to compute priority

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param costFunction: Function used to simplify comp/comm cost ('mean', 'median', 'maxmax', 'minmin',\
    'minmax', 'maxmin')
    :type costFunction: str
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :return: List of nodes sorted according to rku
    :rtype: list[int]
    """
    computeRankU(g, costFunction=costFunction, verbose=verbose)
    nodes = g.nodes
    nodes = sorted(nodes, key=lambda x: g.graph['prio'][x - 1], reverse=True)  # Ties broken randomly
    computeRankD(g, costFunction=costFunction, verbose=verbose, add=True)
    return nodes


def execCluHPS(g, costFunction="mean", verbose=False):
    """ Use HPS policy to compute priority and organise nodes

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param costFunction: Function used to simplify comp/comm cost
    :type costFunction: str
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :return: List of nodes sorted according to LC (Link Cost)
    :rtype: list[int]
    """
    computeLB(g, costFunction, verbose)
    lvl = computeLevels(g)
    nodes = computeLC(g, lvl, verbose=verbose)
    return nodes


def execBIL(g, verbose=False):
    """Use BIL policy to compute priority

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :return: List of nodes sorted according to BIL
    :rtype: list[int]
    """
    computeBIL(g, verbose=verbose)
    nodes = g.nodes
    nodes = sorted(nodes, key=lambda x: min(g.graph['prio'][x - 1]), reverse=True)
    return nodes

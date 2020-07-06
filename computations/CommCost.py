def commCost(g, i, j, m, n, verbose=False) -> float:
    """Compute exact communication cost using startup time, data quantity, and transfer rate

    :param g: DAG used
    :type g: networkx.DiGraph
    :param i: Starting node of the communication
    :type i: int
    :param j: Ending node of the communication
    :type j: int
    :param m: Processor on which **i** is scheduled
    :type m: int
    :param n: Processor on which **j** is scheduled
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :return: The communication cost between (**i**, **m**) and (**j**, **n**)
    :rtype: float
    """
    if m == n:
        cijmn = 0
    else:
        cijmn = g.graph['L'][m] + g.edges[i, j]['weight'] / g.graph['B'][m][n]
    if verbose and False:
        print("c", i, ",", j, ",", m, ",", n, " = ", cijmn, sep="")
    return cijmn


def meanCommCost(g, i, j, verbose=False):
    """Compute communication cost using mean value for startup time and transfer rate

    :param g: DAG used
    :type g: networkx.DiGraph
    :param i: Starting node of the communication
    :type i: int
    :param j: Ending node of the communication
    :type j: int
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :return: The mean communication cost between **i** and **j**
    :rtype: float
    """
    cij = g.graph['meanL'] + g.edges[i, j]['weight'] / g.graph['meanB']
    if verbose:
        print("c", i, ",", j, " = ", cij, sep="")
    return cij

from math import inf


def sequentialScheduleLength(g, verbose=False):  # Should we use mean proc or best proc ? Best is used here
    """ Compute sequential schedule on processor minimizing total scheduling time

    :param g: Used DAG
    :type g: networkx.DiGraph
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :return: Sequential makespan
    :rtype: int
    """
    m = inf
    bestproc = None
    for i in range(g.graph['nbproc']):
        partSum = 0
        for j in g.nodes:
            partSum += g.graph['costmatrix'][j-1][i]
        if partSum < m:
            m = partSum
            bestproc = i + 1
    if verbose:
        print("Sequential makespan :", m, "on proc ", bestproc)
    return m

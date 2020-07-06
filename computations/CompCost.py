from statistics import median

from exceptions.StrategyCostFException import StrategyCostFException


def computeCompCost(g, costFunction='mean', verbose=False):
    """Compute computation cost according to costFunction

    :param g: DAG used
    :type g: networkx.DiGraph
    :param costFunction: Function used to compute computation cost ('mean', 'median', 'max', 'min')
    :type costFunction: str
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :rtype: None
    """
    g.graph['meancompcost'] = []
    q = g.graph['nbproc']
    for vertex in g.nodes:
        s = []
        t = 0
        for proc in range(q):
            # print("NEW")
            # print(vertex)
            # print(len(g.graph['costmatrix']))
            s.append(g.graph['costmatrix'][vertex - 1][proc])
        if costFunction == 'mean':
            t = sum(s) / q
        elif costFunction == 'median':
            t = median(s)
        elif costFunction[:3] == 'max':
            t = max(s)
        elif costFunction[:3] == 'min':
            t = min(s)
        else:
            raise StrategyCostFException(costFunction)
        g.graph['meancompcost'].append(t)
    if verbose:
        print(costFunction, "CompCost : ", g.graph['meancompcost'])

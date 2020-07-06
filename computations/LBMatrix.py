from statistics import median


def computeLB(g, costFunction='mean', verbose=False):
    """Compute communication cost according to costFunction

    :param g: DAG used
    :type g: networkx.DiGraph
    :param costFunction: Function used to compute communication cost ('mean', 'median', 'max', 'min')
    :type costFunction: str
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :rtype: None
    """
    q = g.graph['nbproc']
    meanBV = []
    meanB = meanL = 0
    for p in range(q):
        meanBV += g.graph['B'][p]
    if costFunction == 'mean':
        meanB = sum(meanBV) / (q*q)
        meanL = sum(g.graph['L']) / q
    elif costFunction == 'median':
        meanB = median(meanBV)
        meanL = median(g.graph['L'])
    elif costFunction[3:] == 'min':
        meanB = min(meanBV)
        meanL = min(g.graph['L'])
    elif costFunction[3:] == 'max':
        meanB = max(meanBV)
        meanL = max(g.graph['L'])
    else:
        print(f"{costFunction} is not a valid cost Function")
        exit()
    g.graph['meanB'] = meanB
    g.graph['meanL'] = meanL
    if verbose:
        print("MeanB : ", g.graph['meanB'])
        print("MeanL : ", g.graph['meanL'])

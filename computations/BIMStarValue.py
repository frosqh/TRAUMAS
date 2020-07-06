from computations.EarliestTimes import computeEFT


def computeBIMStar(g, currentNode, proc, schedule, k, verbose, insertion, estimate=False):
    """ Compute the BIM* value of a node

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param currentNode: Current node to be evaluated
    :type currentNode: int
    :param proc: Proc to schedule **currentNode** on
    :type proc: int
    :param schedule: Schedule at this point
    :type schedule: dict[int, (int, float, float)]
    :param k: Number of ready tasks at this point
    :type k: int
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :param insertion: Use of insertion policy ?
    :type insertion: bool
    :return: The BIM* value of **currentNode**, along with its EST and EFT on **proc**
    :rtype: (float, float, float)
    """
    q = g.graph['nbproc']
    bil = g.graph['prio']
    w = g.graph['costmatrix']
    est, eft = computeEFT(g=g, node=currentNode, proc=proc, schedule=schedule, verbose=verbose,
                          insertion=insertion, estimate=estimate)
    if isinstance(bil[currentNode - 1], list):
        bims = est + bil[currentNode - 1][proc] + w[currentNode - 1][proc] * max(k / q - 1, 0)
    else:
        bims = est + bil[currentNode - 1] + w[currentNode - 1][proc] * max(k / q - 1, 0)
    if verbose:
        print("Attempt on scheduling node ", currentNode, "on proc", proc + 1, " -> bims =", bims)
    return bims, est, eft
import networkx as nx

from computations.Placements import placeEFTBIM, placeEFT, placeBIMStarBIM, placeBIMStar, placeOLB, placeMET, \
    placeDLBIM, placeDL, placeGDLBIM, placeGDL, placeSerial
from computations.PostTreatments import applyBSA
from computations.Priorities import getEntryTask
from exceptions.StrategyPlacementException import StrategyPlacementException
from exceptions.StrategyPrioException import StrategyPrioException
from executions.Executions import execRKU, execBIL, execRKD, execRKUSD, execRKUAD, execCluHPS


def computeWithList(g, strategyPrio="rku", strategyPlacement="eft", costFunction="mean", desc=None, useOfBIM=False,
                    insertion=True, bsa=False, verbose=False):
    """Compute a schedule using list-based heuristic

    :param g: DAG to schedule
    :type g: nx.DiGraph
    :param strategyPrio: Priority-computations strategy ('rku', 'random', 'BIL', 'rkd', 'rkusd', 'rkuad', 'cluHPS')
    :type strategyPrio: str
    :param strategyPlacement: Placement-strategy ('eft', 'BIM*', 'OLB', 'MET', 'DL', 'GDL')
    :type strategyPlacement: str
    :param costFunction: Function used to simplify comp/comm cost ('mean', 'median', 'maxmax', 'minmin',\
    'minmax', 'maxmin')
    :type costFunction: str
    :param desc: Lookahead strategy ('DLS/DC', None)
    :type desc: str
    :param useOfBIM: Use of BIM strategy (k-th smallest) ?
    :type useOfBIM: bool
    :param insertion: Use of insertion-based policy ?
    :type insertion: bool
    :param bsa: Use of BSA post-treatment ?
    :type bsa: bool
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :raises StrategyPrioException: If strategyPrio is unknown
    :raises StrategyPlacementException: If strategyPlacement is unknown
    :return: A corresponding schedule in format {task : [proc, est, eft],..}
    :rtype: dict[int, (int, float, float)]
    """

    if strategyPrio == "rku":
        nodes = execRKU(g, costFunction=costFunction, verbose=verbose)
    elif strategyPrio == "random":  # Topological sort
        nodes = list(nx.topological_sort(g))
        g.graph['prio'] = list(range(len(nodes)))
    elif strategyPrio == "BIL":
        nodes = execBIL(g, verbose=verbose)
    elif strategyPrio == "rkd":
        nodes = execRKD(g, costFunction=costFunction, verbose=verbose)
    elif strategyPrio == "rkusd":
        nodes = execRKUSD(g, costFunction=costFunction, verbose=verbose)
    elif strategyPrio == "rkuad":
        nodes = execRKUAD(g, costFunction=costFunction, verbose=verbose)
    elif strategyPrio == "cluHPS":
        nodes = execCluHPS(g, costFunction, verbose)
    else:
        raise (StrategyPrioException(strategyPrio))

    nodes.remove(getEntryTask(g, verbose))
    nodes = [getEntryTask(g, verbose)] + nodes

    if strategyPlacement == "eft":
        if useOfBIM:
            schedule = placeEFTBIM(g, nodes, desc=desc, verbose=verbose, insertion=insertion)
        else:
            schedule = placeEFT(g, nodes, desc=desc, verbose=verbose, insertion=insertion)
    elif strategyPlacement == "BIM*":
        if useOfBIM:
            schedule = placeBIMStarBIM(g, nodes, desc=desc, verbose=verbose, insertion=insertion)
        else:
            schedule = placeBIMStar(g, nodes, desc=desc, verbose=verbose, insertion=insertion)
    elif strategyPlacement == "OLB":  # Should we use BIM* here too ?
        schedule = placeOLB(g, nodes, desc=desc, verbose=verbose, insertion=insertion)
    elif strategyPlacement == "MET":  # Should we use BIM* here too ?
        schedule = placeMET(g, nodes, desc=desc, verbose=verbose, insertion=insertion)
    elif strategyPlacement == "DL":
        if useOfBIM:
            schedule = placeDLBIM(g, nodes, desc=desc, costFunction=costFunction, verbose=verbose, insertion=insertion)
        else:
            schedule = placeDL(g, nodes, desc=desc, costFunction=costFunction, verbose=verbose, insertion=insertion)
    elif strategyPlacement == "GDL":
        if useOfBIM:
            schedule = placeGDLBIM(g, nodes, desc=desc, costFunction=costFunction, verbose=verbose, insertion=insertion)
        else:
            schedule = placeGDL(g, nodes, desc=desc, costFunction=costFunction, verbose=verbose, insertion=insertion)
    # elif strategyPlacement == "DCP":
    #    schedule = placeByDCP(g, nodes, verbose=verbose, insertion=insertion)
    elif strategyPlacement == "serial":
        schedule = placeSerial(g, strategyPrio, verbose)
    else:
        raise (StrategyPlacementException(strategyPlacement))
    if bsa:
        schedule = applyBSA(g, schedule, verbose)
    return schedule


def computeSchedule(g, category="list", strategyPrio="rku", strategyPlacement="eft", costFunction="mean", desc=None,
                    useOfBIM=False, insertion=True, bsa=False, verbose=False):
    """ Compute schedule

    :param g: DAG to schedule
    :type g: nx.DiGraph
    :param category: Type of scheduling algorithm to use ('list', 'clustering')
    :type category: str
    :param strategyPrio: Priority-computations strategy ('rku', 'random', 'BIL')
    :type strategyPrio: str
    :param strategyPlacement: Placement-strategy ('eft', 'BIM*', 'OLB', 'MET')
    :type strategyPlacement: str
    :param costFunction: Function used to simplify comp/comm cost ('mean', 'median', 'maxmax', 'minmin',\
    'minmax', 'maxmin')
    :type costFunction: str
    :param desc: Lookahead strategy ('DLS/DC', None)
    :type desc: str
    :param useOfBIM: Use of BIM strategy (k-th smallest) ?
    :type useOfBIM: bool
    :param insertion: Use of insertion-based policy ?
    :type insertion: bool
    :param bsa: Use of BSA post-treatment ?
    :type bsa: bool
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :return: A corresponding schedule in format {task : [proc, est, eft],..}
    :rtype: dict[int, (int, float, float)]
    """
    if category == "list":
        return computeWithList(g, strategyPrio=strategyPrio, strategyPlacement=strategyPlacement,
                               costFunction=costFunction, useOfBIM=useOfBIM, verbose=verbose, bsa=bsa, desc=desc,
                               insertion=insertion)

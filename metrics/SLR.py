import os
from os import listdir

from computations.Priorities import getExitTask, getCP
from help.FileReader import readFile


def computeSLR(g, schedule, verbose=False):
    """ Compute the SLR of the computed schedule, *id est* ration of obtained makespan over makespan of CP.

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param schedule: Schedule obtained
    :type schedule: dict[int, (int, float, float)]
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :return: SLR, the smaller the better
    :rtype: float
    """
    minCP = getCP(g, costFunction="minmin")
    minMakespan = sum(map(lambda n: min(g.graph['costmatrix'][n - 1]), minCP))
    return schedule[getExitTask(g)][2] / minMakespan
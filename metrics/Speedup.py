from computations.Priorities import getExitTask
from metrics.Sequential import sequentialScheduleLength


def measureSpeedup(g, schedule, verbose=False):
    """ Compute speedup of computed schedule, *id est* sequential makespan over makespan ratio

    :param g: DAG to schedule:
    :type g: networkx.DiGraph
    :param schedule: Schedule obtained
    :type schedule: dict[int, (int, float, float)]
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :return: Computed speedup, higher the better
    :rtype: float
    """
    seqMakespan = sequentialScheduleLength(g, verbose)
    return seqMakespan / schedule[getExitTask(g)][2]


def measureGeneralEfficiency(g, schedule, verbose=False):
    """ Compute general efficiency of computed schedule, *id est* sequential makespan over (makespan :math:`\\times`
    total number of procs) ratio

    :param g: DAG to schedule:
    :type g: networkx.DiGraph
    :param schedule: Schedule obtained
    :type schedule: dict[int, (int, float, float)]
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    :return: Computed general efficiency, higher the better
    :rtype: float
    """
    print(g.graph)
    seqMakespan = sequentialScheduleLength(g, verbose)
    return seqMakespan / (g.graph['nbproc'] * schedule[getExitTask(g)][2])


def measureSpecificEfficiency(g, schedule, verbose=False):
    """ Compute specific efficiency of computed schedule, *id est* sequential makespan over (makespan :math:`\\times`
        number of used procs) ratio

        :param g: DAG to schedule:
        :type g: networkx.DiGraph
        :param schedule: Schedule obtained
        :type schedule: dict[int, (int, float, float)]
        :param verbose: Print non-necessary information ?
        :type verbose: bool
        :return: Computed specific efficiency, higher the better
        :rtype: float
        """
    seqMakespan = sequentialScheduleLength(g, verbose)
    procUsed = []
    for i in schedule:
        procUsed += [schedule[i][0]]
    procUsed = list(dict.fromkeys(procUsed))
    if verbose:
        print("Number of processors REALLY used :", len(procUsed))
    return seqMakespan / (len(procUsed) * schedule[getExitTask(g)][2])

from networkx import relabel_nodes, write_gml
from numpy import random

from help.FileReader import readFile


def listEntryNodes(g):
    """ Compute list of current entry nodes for **g**

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :return: List of entry nodes
    :rtype: list[int]
    """
    listEntry = []
    for i in g.nodes:
        if not list(g.predecessors(i)):
            listEntry.append(i)
    return listEntry


def listExitNodes(g):
    """ Compute list of current exit nodes for **g**

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :return: List of exit nodes
    :rtype: list[int]
    """
    listExit = []
    for i in g.nodes:
        if not list(g.successors(i)):
            listExit.append(i)
    return listExit


def igraphToNetworkX(inputFile, output, sdComp, sdComm, CCR, nbproc):
    """ Transform an igraph file, from recursiveGenLength.py, to an networkx one.
    To be simple, just adding computations and communications cost, as well as root and sink nodes.

    :param inputFile: Igraph file, to transform
    :type inputFile: str
    :param output: Output file
    :type output: str
    :param sdComp: Standard Deviation of computations cost
    :type sdComp: float
    :param sdComm: Standard Deviation of communications cost
    :type sdComm: float
    :param CCR: Communications to Computations Ratio
    :type CCR: float
    :param nbproc: Number of processor for the graph generation
    :type nbproc: int
    :return: Converted graph
    :rtype: networkx.DiGraph
    """
    g = readFile(inputFile, converter=True)
    d = {}
    n = len(g.nodes)
    costmatrix = []
    for _ in range(n):
        costmatrix.append([x for x in random.gamma(1. / (sdComp ** 2), (sdComp ** 2), nbproc)])

    nbEdges = len(g.edges)
    edgesCost = random.gamma(CCR ** 2 / (sdComm ** 2), (sdComm ** 2) / CCR, nbEdges)

    for index, e in enumerate(g.edges):
        g.edges[e]['weight'] = edgesCost[index]

    g.graph['costmatrix'] = costmatrix
    g.graph['B'] = [[1] * nbproc] * nbproc
    g.graph['L'] = [0] * nbproc
    g.graph['nbproc'] = nbproc

    diff = 2

    listEntry = listEntryNodes(g)
    if len(listEntry) > 1:
        g.add_node(-1, label="-1")
        for e in listEntry:
            g.add_edge(-1, e, weight=0)
        g.graph['costmatrix'] = [[0] * nbproc] + g.graph['costmatrix']
    else:
        diff -= 1

    listExit = listExitNodes(g)
    if len(listExit) > 1:
        g.add_node(n, label=str(n))
        for e in listExit:
            g.add_edge(e, n, weight=0)
        g.graph['costmatrix'] = g.graph['costmatrix'] + [[0] * nbproc]

    for i in g.nodes:
        d[i] = i + diff
    g2 = relabel_nodes(g, d)
    toReturn = g2.copy()
    g2.graph['costmatrix'] = str(g2.graph['costmatrix'])
    g2.graph['B'] = str(g2.graph['B'])
    g2.graph['L'] = str(g2.graph['L'])
    write_gml(g2, output, lambda x: str(x))
    return toReturn


if __name__ == '__main__':
    # noinspection PyArgumentList
    igraphToNetworkX("../templateBis.gml", "templateTre.gml")

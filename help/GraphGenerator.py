import os

from help.Converter import igraphToNetworkX
from help.recursiveGenLength import executionL


def genGraph(length, depth, filename, sdComp, sdComm, CCR, nbproc):
    """ Generate a graph using recursiveGenLength.py

    :param length: Length of the graph (number of nodes)
    :type length: int
    :param depth: Depth of the graph (number of levels)
    :type depth: int
    :param filename: Output filename
    :type filename: str
    :param sdComp: Standard Deviation of computations costs
    :type sdComp: float
    :param sdComm: Standard Deviation of communications costs
    :type sdComm: float
    :param CCR: Communications to Computations Ratio
    :type CCR: float
    :param nbproc: Number of processors used when generating the graph
    :type nbproc: int
    :return: Generated and converted graph
    :rtype: networkx.DiGraph
    """
    filename, ext = filename.split(".")
    igraphFile = filename+"-igraph."+ext
    networkxFile = filename+"."+ext
    executionL(int(length), int(depth), igraphFile)
    graph = igraphToNetworkX(igraphFile, networkxFile, float(sdComp), float(sdComm), float(CCR), int(nbproc))
    os.remove(igraphFile)
    return graph

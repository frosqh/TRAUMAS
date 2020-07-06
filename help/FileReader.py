import networkx as nx


# noinspection PyBroadException
def readFile(inputFile, converter=False, verbose=False):
    """Read a .gml file and create the corresponding Digraph.

    :param inputFile: File to parse
    :type inputFile: str
    :param converter: Use id as label ?
    :type converter: bool
    :param verbose: Print non-necessary information ?
    :type verbose: bool

    :returns: Created digraph
    :rtype: networkx.DiGraph
    """
    if converter:
        g = nx.read_gml(inputFile, label='id')
    else:
        g = nx.read_gml(inputFile)
        try:
            g.graph['costmatrix'] = eval(g.graph['costmatrix'])
        except Exception:
            g.graph['costmatrix'] = [[1] * g.graph['nbproc']] * g.number_of_nodes
        try:
            g.graph['B'] = eval(g.graph['B'])
        except Exception:
            g.graph['B'] = [[1] * g.graph['nbproc']] * g.graph['nbproc']
        try:
            g.graph['L'] = eval(g.graph['L'])
        except Exception:
            g.graph['L'] = [0] * g.graph['nbproc']
        for a in g.edges:
            if 'weight' not in g.edges[a]:
                g.edges[a]['weight'] = 0
    if verbose:
        print("Nodes :", g.number_of_nodes())
        print("Edges :", g.number_of_edges())
        print("NbProc :", g.graph['nbproc'])
        print("costmatrix :", g.graph['costmatrix'])
        print("B : ", g.graph['B'])
        print("L : ", g.graph['L'])
    d = {}
    for n in g.nodes:
        d[n] = int(n)
    return nx.relabel_nodes(g, d)

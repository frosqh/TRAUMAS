from computations.CommCost import commCost
from computations.EarliestTimes import computeDFT


def verifPrec(g, schedule, verbose):
    """ Verify precedence constraint and job length of a given schedule

    :param g: DAG to schedule
    :type g: networkx.DiGraph
    :param schedule: Schedule to check
    :type schedule: dict[int, (int, float, float)]
    :param verbose: Print non-necessary information ?
    :type verbose: bool
    """
    lastA = [0] * g.graph['nbproc']
    for t in schedule:
        tproc, test, teft = schedule[t]
        dft, onproc = computeDFT(g, t, tproc, schedule, verbose, False)
        if test < dft:
            print(f"WHOOPS, started too soon for task {t} on proc {tproc} : should not start before {dft}")
            exit()
        # noinspection PyTypeChecker
        lastA[tproc] = teft
        for prec in g.predecessors(t):
            pproc, pest, peft = schedule[prec]
            if test < peft + commCost(g, prec, t, pproc, tproc, verbose):
                print("Whoops, pause not long enough for task :", str(t) + ". Est :", test,
                      "while actual finish time :", peft + commCost(g, prec, t, pproc, tproc, verbose),
                      "for prec", prec)
                exit()
            if test + g.graph['costmatrix'][t - 1][tproc] > teft:
                print("Whoops, job too long for task :", str(t) + ". Job size on proc", tproc + 1, ":",
                      g.graph['costmatrix'][t - 1][tproc])

                exit()
    for n in g.nodes:
        if n not in schedule:
            print("WHOOPS, node not scheduled")
            exit()

# coding: utf-8

import argparse as ap
import os.path
import sys

fileName = f'{os.path.split(sys.argv[0])[1]}'

script_description = f'use {fileName} --help for more information'


def defineParser():
    """ Define the script parser

    :return: Parser to use
    :rtype: argparse.ArgumentParser
    """
    # init()
    # noinspection PyTypeChecker
    parser = ap.ArgumentParser(description="Run heuristics on generated graph", formatter_class=ap.RawTextHelpFormatter)
    parser.add_argument("-v", "--verbose", help="print non-necessary information", action="store_true")
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    parser.add_argument("filename", help="output file")
    parser.add_argument("-m", "--mail", help="send results by mail", action="store_true")
    parser.add_argument("-mf", "--mailfilename", help="file containing mail information", default="mailinfo")

    graphSource = parser.add_mutually_exclusive_group(required=True)
    graphSource.add_argument("-g", "--generate", help="generate graph to use.\nthe mean of computation cost is "
                                                      "supposed to be 1, so CCR and standard deviation are sufficient "
                                                      "to generate the graph.", nargs=6,
                             metavar=('SIZE', 'DEPTH', 'GENERATEDFILENAME', 'SDCOMP', 'SDCOMM', 'CCR'))
    graphSource.add_argument("-G", "--graphfile", help="use .gml file")

    testCase = parser.add_mutually_exclusive_group(required=True)
    testCase.add_argument("-H", "--heuristic", help="define heuristic to test.\n"
                                                    "for example, -H rku mean eft DLS/DC 0 0 1.\n"
                                                    "an overview of possible combinations can be found in "
                                                    "man.pdf.", nargs=7,
                          metavar=('PRIO', 'COST', 'PLACEMENT', 'DESC', 'BIM', 'BSA', 'INS'))
    testCase.add_argument("-a", "--all", help="try all heuristics N times", metavar='N')
    testCase.add_argument("-n", "--nothing", help="generate the graph then exit", action="store_true")

    parser.add_argument("-p", "--nbproc", help="number of processors available", required=False)
    parser.add_argument("-s", "--seed", help="seed for the random generation")
    return parser

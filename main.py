from opyenxes.data_in.XUniversalParser import XUniversalParser

from dfg import DFG

with open('data/Sepsis_Cases.xes') as log_file:
    # parse the log
    log = XUniversalParser().parse(log_file)[0]
    pdfg = DFG(log)

    # pdfg.filtering(0.5)
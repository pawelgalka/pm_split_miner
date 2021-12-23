from opyenxes.data_in.XUniversalParser import XUniversalParser

from dfg import DFG

with open('data/Sepsis_Cases.xes') as log_file:
    log = XUniversalParser().parse(log_file)[0]
    pdfg = DFG(log)
    pdfg_after_filtering = pdfg.filtering(eta=50)
    pdfg_after_discovering = pdfg_after_filtering.discover_splits()
    # pdfg_final = pdfg_after_discovering.join_splits()
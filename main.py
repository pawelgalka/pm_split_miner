from IPython.display import Image, display
from opyenxes.data_in.XUniversalParser import XUniversalParser

from dfg import DFG
from graph import MyGraph

log_name = 'data/Sepsis_Cases.xes'
output_png_name = log_name.split("/")[1].split(".")[0]
with open(log_name) as log_file:
    log = XUniversalParser().parse(log_file)[0]
    pdfg = DFG(log)
    pdfg_after_filtering = pdfg.filtering(eta=40)
    pdfg_after_discovering = pdfg_after_filtering.discover_splits()
    bpmn = pdfg_after_discovering.discover_joins()
    graph = MyGraph.from_bpmn(bpmn)
    try:
        graph.draw(f'./output/{output_png_name}.png', prog='dot')
        display(Image(f'./output/{output_png_name}.png'))
    except:
        pass
import argparse

from IPython.display import Image, display
from opyenxes.data_in.XUniversalParser import XUniversalParser

from dfg import DFG
from graph import MyGraph


parser = argparse.ArgumentParser(
    description="This script is doing Split Mining of given XES file")
parser.add_argument('--eta', type=int, default=40, required=False,
                    help="Value of filtering threshold from DFG to PDFG")
parser.add_argument('--epsilon', type=float, default=0.5, required=False,
                    help="Value of percentile during discovery of concurrent and infrequent tasks")
parser.add_argument('--log_name', type=str, required=True,
                    help="Log name in data folder")
params = parser.parse_args()

log_name = f'data/{params.log_name}.xes'
output_png_name = log_name.split("/")[1].split(".")[0]
with open(log_name) as log_file:
    log = XUniversalParser().parse(log_file)[0]
    pdfg = DFG(log, epsilon=params.epsilon)
    pdfg_after_filtering = pdfg.filtering(eta=params.eta)
    pdfg_after_discovering = pdfg_after_filtering.discover_splits()
    bpmn = pdfg_after_discovering.discover_joins()
    graph = MyGraph.from_bpmn(bpmn)
    try:
        graph.draw(f'./output/{output_png_name}.png', prog='dot')
        display(Image(f'./output/{output_png_name}.png'))
    except:
        pass
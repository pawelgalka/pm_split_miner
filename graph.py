import pygraphviz


class MyGraph(pygraphviz.AGraph):

    def __init__(self, *args):
        super(MyGraph, self).__init__(strict=False, directed=True, *args)
        self.graph_attr['rankdir'] = 'LR'
        self.node_attr['shape'] = 'Mrecord'
        self.graph_attr['splines'] = 'ortho'
        self.graph_attr['nodesep'] = '0.8'
        self.edge_attr.update(penwidth='2')

    @staticmethod
    def from_bpmn(bpmn):
        graph = MyGraph()
        graph.add_event("Start")
        graph.add_end_event("End")

        for edge in bpmn.edges:
            graph.add_edge_block_aware(edge.start, edge.end)
        return graph

    def add_event(self, name):
        super(MyGraph, self).add_node(name, shape="circle", label="")

    def add_end_event(self, name):
        super(MyGraph, self).add_node(name, shape="circle", label="", penwidth='3')

    def add_edge_block_aware(self, src, trg):
        if src.startswith('and'):
            super(MyGraph, self).add_node(src, shape="diamond",
                                          width=".7", height=".7",
                                          fixedsize="true",
                                          fontsize="40", label="+")
        if trg.startswith('and'):
            super(MyGraph, self).add_node(trg, shape="diamond",
                                          width=".7", height=".7",
                                          fixedsize="true",
                                          fontsize="40", label="+")
        if src.startswith('xor'):
            super(MyGraph, self).add_node(src, shape="diamond",
                                          width=".7", height=".7",
                                          fixedsize="true",
                                          fontsize="40", label="×")
        if trg.startswith('xor'):
            super(MyGraph, self).add_node(trg, shape="diamond",
                                          width=".7", height=".7",
                                          fixedsize="true",
                                          fontsize="40", label="×")
        if src.startswith('or'):
            super(MyGraph, self).add_node(src, shape="diamond",
                                          width=".7", height=".7",
                                          fixedsize="true",
                                          fontsize="40", label="o")
        if trg.startswith('or'):
            super(MyGraph, self).add_node(trg, shape="diamond",
                                          width=".7", height=".7",
                                          fixedsize="true",
                                          fontsize="40", label="o")
        super(MyGraph, self).add_edge(src, trg)
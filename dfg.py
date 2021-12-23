import itertools

from edge import GraphEdge


class DFG:

    def __init__(self, log):
        self.log = log
        self.traces = self.prepare_traces()
        self.nodes = self.prepare_nodes()
        self.end_node = [n for n in self.nodes if n == 'End'][0]
        self.start_node = [n for n in self.nodes if n == 'Start'][0]
        self.edges = self.prepare_edges()
        self.self_loops, self.self_loops_starts = self.find_self_loops()
        self.short_loops = self.find_short_loops()
        self.remove_self_and_short_loops()
        self.concurrent_tasks, self.infrequent_tasks = self.find_concurrent_and_infrequent_tasks(0.5)
        self.remove_concurrent_and_infrequent_tasks()

    def prepare_traces(self):
        traces = []
        for trace in self.log:
            traces.append(
                ['Start'] + [log_entry.get_attributes()['concept:name'].get_value() for log_entry in trace] + ['End'])
        print("DFG TRACES", traces)
        return traces

    def prepare_nodes(self):
        nodes = []
        for trace in self.traces:
            for evt in trace:
                if evt not in nodes:
                    nodes.append(evt)
        print("DFG NODES", nodes)
        return nodes

    def prepare_edges(self):
        edges = []
        for trace in self.traces:
            for (start, end) in zip(trace[0::], trace[1::]):
                edge = GraphEdge(start, end)
                if edge not in edges:
                    edge.increase_frequency()
                    edges.append(edge)
                else:
                    edges[edges.index(edge)].increase_frequency()
        edges.sort()
        print("DFG EDGES", len(edges), edges)
        return edges

    def find_self_loops(self):
        self_loops = [edge for edge in self.edges if edge.start == edge.end]
        self_loops_keys = [edge.start for edge in self.edges if edge.start == edge.end]
        print("DFG SELF LOOPS", self_loops)
        print("DFG SELF LOOPS STARTS", self_loops_keys)
        return self_loops, self_loops_keys

    def find_short_loops(self):
        short_loops = []
        for trace in self.traces:
            for a, b, c in zip(trace[0::], trace[1::], trace[2::]):
                if a == c and a != b:
                    self.edges[self.edges.index(GraphEdge(a, b))].short_loop_count[b] += 1
                    self.edges[self.edges.index(GraphEdge(b, a))].short_loop_count[a] += 1
        for (edge1, edge2) in itertools.product(self.edges, self.edges):
            if edge1.start not in self.self_loops_starts and edge2.start not in self.self_loops_starts and \
                    edge1.short_loop_count[edge2.start] + edge2.short_loop_count[edge1.start] != 0:
                short_loops.append(edge1)
                short_loops.append(edge2)
        print("DFG SHORT LOOPS", list(set(short_loops)))
        return short_loops

    def remove_self_and_short_loops(self):
        self.edges = [edge for edge in self.edges if edge not in self.self_loops and edge not in self.short_loops]
        print("DFG EDGES AFTER REMOVAL OF SELF AND SHORT LOOPS", len(self.edges), self.edges)

    def find_concurrent_and_infrequent_tasks(self, epsilon):
        concurrent_tasks = []
        infrequent_tasks = []
        for (edge1, edge2) in itertools.product(self.edges, self.edges):
            if edge1.check_if_inverse_of_other(edge2) and edge1 != edge2 and edge1.count > 0 and edge2.count > 0 and \
                    edge1.short_loop_count[edge2] + edge2.short_loop_count[edge1] == 0:
                edge_threshold = abs(edge1.count - edge2.count) / (edge1.count + edge2.count)
                if edge_threshold < epsilon:
                    concurrent_tasks.append(edge1)
                    concurrent_tasks.append(edge2)
                else:
                    infrequent_tasks.append((edge1, edge2)[edge2.count < edge1.count])
        concurrent_tasks = list(set(concurrent_tasks))
        infrequent_tasks = list(set(infrequent_tasks))
        print("DFG CONCURRENT TASKS", len(concurrent_tasks), concurrent_tasks)
        print("DFG INFREQUENT TASKS", len(infrequent_tasks), infrequent_tasks)
        return concurrent_tasks, infrequent_tasks

    def remove_concurrent_and_infrequent_tasks(self):
        self.edges = [edge for edge in self.edges if
                      edge not in self.concurrent_tasks and edge not in self.infrequent_tasks]
        print("DFG EDGES AFTER REMOVAL OF CONCURRENT AND INFREQUENT", len(self.edges), self.edges)

    def filtering(self, eta):
        pass
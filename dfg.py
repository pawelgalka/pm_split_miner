import itertools
from typing import Set

import numpy as np

from artificial_log import prepare_artificial_traces
from bpmn import BPMN
from edge import GraphEdge
from join_miner import JoinMiner


class DFG:

    def __init__(self, log):
        self.log = log
        # self.traces = self.prepare_traces()
        self.traces = prepare_artificial_traces()
        self.xor_count = 0
        self.or_count = 0
        self.and_count = 0
        self.bpmn = None
        self.nodes = self.prepare_nodes()
        self.end_node = [n for n in self.nodes if n == 'End'][0]
        self.start_node = [n for n in self.nodes if n == 'Start'][0]
        self.edges = self.prepare_edges()
        self.filtered_edges = None
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
        most_frequent_edges = list(filter(None,
                                          set([self.find_most_frequent_edge(self.find_incoming_edges(task, self.edges))
                                               for task in self.nodes] + [self.find_most_frequent_edge(
                                              self.find_outgoing_edges(task, self.edges)) for task in self.nodes])))
        print("DFG MOST FREQUENT EDGES", len(most_frequent_edges), most_frequent_edges)
        filtering_threshold = self.get_percentile_frequency(most_frequent_edges, eta)
        print("DFG FILTERING THRESHOLD", filtering_threshold)
        most_frequent_edges += [edge for edge in self.edges if edge.count > filtering_threshold]
        most_frequent_edges = list(set(most_frequent_edges))
        print("DFG MOST FREQUENT EDGES WITH EDGES ABOVE THRESHOLD", len(most_frequent_edges), most_frequent_edges)
        filtered_edges = []
        while len(most_frequent_edges) > 0:
            most_frequent_edge_current = self.find_most_frequent_edge(most_frequent_edges)
            if most_frequent_edge_current.count >= filtering_threshold or len(
                    self.find_outgoing_edges(most_frequent_edge_current.start, self.edges)) == 0 or len(
                self.find_incoming_edges(most_frequent_edge_current.end, self.edges)) == 0:
                filtered_edges.append(most_frequent_edge_current)
            most_frequent_edges.remove(most_frequent_edge_current)
        print("DFG FILTERED EDGES", len(filtered_edges), filtered_edges)
        self.filtered_edges = filtered_edges
        return self

    def get_successor_tasks(self, node):
        return [edge.end for edge in self.find_outgoing_edges(node, self.edges)]

    def discover_splits(self):
        self.bpmn = BPMN(self.start_node, self.end_node, self.nodes, [], [], [], [])
        task_done = []
        split_tasks = [task for task in self.nodes if len(self.find_outgoing_edges(task, self.filtered_edges)) > 1]
        if len(split_tasks) == 0:
            self.bpmn.edges = self.filtered_edges
            print("BPMN AFTER TASK", self.bpmn)
            return self

        for task in split_tasks:
            successor_tasks = set(self.get_successor_tasks(task))
            cover_set = {}
            future_set = {}
            print("TASK", task, "SUCCESSORS", successor_tasks)
            for successor in successor_tasks:
                cover_set_successor = set()
                cover_set_successor.add(successor)
                future_set_successor = set()
                for successor2 in successor_tasks:
                    if successor != successor2 and GraphEdge(successor, successor2) in self.concurrent_tasks:
                        future_set_successor.add(successor2)
                cover_set[successor] = cover_set_successor
                future_set[successor] = future_set_successor
            edges_without_successors = [edge for edge in self.filtered_edges if
                                        edge not in self.find_outgoing_edges(task,
                                                                             self.filtered_edges) and edge.start not in split_tasks]
            print("FUTURE SET", future_set)
            print("COVER SET", cover_set)
            print("EDGES WITHOUT SUCCESSORS", len(edges_without_successors), edges_without_successors)
            self.bpmn.edges = list(set(self.bpmn.edges + edges_without_successors))
            while len(successor_tasks) > 1:
                successor_tasks, cover_set, future_set = self.discover_xor_split(successor_tasks, cover_set,
                                                                                 future_set)
                successor_tasks, cover_set, future_set = self.discover_and_split(successor_tasks, cover_set, future_set)
            self.bpmn.edges.append(GraphEdge(task, successor_tasks.pop(), 1))
            print("BPMN AFTER TASK", task, self.bpmn)
            task_done.append(task)
        return self

    def discover_xor_split(self, successor_tasks: Set, cover_set, future_set):
        flag = True
        while flag:
            set_X = set()
            for successor in successor_tasks:
                cover_set_u: Set = cover_set[successor]
                future_set_u = future_set[successor]
                future_set_k1 = future_set[successor]
                for successor2 in successor_tasks:
                    future_set_k2 = future_set[successor2]
                    if future_set_k1 == future_set_k2 and successor != successor2:
                        set_X.add(successor2)
                        cover_set_u = cover_set_u.union(cover_set[successor2])
                if len(set_X) > 0:
                    set_X.add(successor)
                    break
            if len(set_X) > 0:
                self.xor_count += 1
                xor = f"xor{self.xor_count}"
                print("ADDING XOR")
                self.add_gateway_to_bpmn(cover_set, cover_set_u, future_set, future_set_u, xor, set_X, successor_tasks)
            if len(set_X) == 0:
                flag = False
        return successor_tasks, cover_set, future_set

    def add_gateway_to_bpmn(self, cover_set, cover_set_u, future_set, future_set_u, gate, set_X, successor_tasks):
        self.bpmn.xor_gateways.append(gate)
        self.bpmn.edges += [GraphEdge(gate, x, count=1) for x in set_X]
        for x in set_X:
            cover_set[x] = None
            future_set[x] = None
        cover_set[gate] = cover_set_u
        future_set[gate] = future_set_u
        successor_tasks.add(gate)
        successor_tasks.difference_update(set_X)

    def discover_and_split(self, successor_tasks, cover_set, future_set):
        set_a = set()
        for successor in successor_tasks:
            set_a.clear()
            cover_set_u: Set = cover_set[successor]
            future_set_i: Set = future_set[successor]
            cover_future_set = cover_set_u.union(future_set_i)
            for successor2 in successor_tasks:
                cover_future_set2 = cover_set[successor2].union(future_set[successor2])
                if cover_future_set == cover_future_set2 and successor != successor2:
                    set_a.add(successor2)
                    cover_set_u = cover_set_u.union(cover_set[successor2])
                    future_set_i = future_set_i.intersection(future_set[successor2])
            if len(set_a) > 0:
                set_a.add(successor)
                break
        if len(set_a) > 0:
            self.and_count += 1
            and_g = f"and{self.and_count}"
            print("ADDING AND")
            self.add_gateway_to_bpmn(cover_set, cover_set_u, future_set, future_set_i, and_g, set_a, successor_tasks)
        return successor_tasks, cover_set, future_set

    def discover_joins(self):
        if len(self.bpmn.xor_gateways + self.bpmn.and_gateways + self.bpmn.or_gateways) > 0:
            rpst_solver = JoinMiner()
            edges = rpst_solver.call(self.bpmn.format())
            edge_dict = self.prepare_edges_to_bpmn(edges)
            self.bpmn.edges = [(GraphEdge(edge_dict[start], edge_dict[end], 1)) for (start, end) in edges]
        print("FINAL BPMN", self.bpmn)
        return self.bpmn

    def prepare_edges_to_bpmn(self, edges):
        edges_keys = set([part[0] for part in edges] + [part[1] for part in edges])
        edge_dict = {}
        for part in edges_keys:
            new_part = part
            if not part[-1].isdigit():
                if part.startswith('xor'):
                    if any([part.endswith(i) for i in self.bpmn.T]):
                        self.xor_count += 1
                        new_part = 'xor' + str(self.xor_count)
                    self.bpmn.xor_gateways.append(new_part)
                if part.startswith('or'):
                    if any([part.endswith(i) for i in self.bpmn.T]):
                        self.or_count += 1
                        new_part = 'or' + str(self.or_count)
                    self.bpmn.or_gateways.append(new_part)
                if part.startswith('and'):
                    if any([part.endswith(i) for i in self.bpmn.T]):
                        self.and_count += 1
                        new_part = 'and' + str(self.and_count)
                    self.bpmn.and_gateways.append(new_part)
            edge_dict[part] = new_part
        return edge_dict

    @staticmethod
    def find_incoming_edges(node, edges):
        return [edge for edge in edges if edge.end == node]

    @staticmethod
    def find_outgoing_edges(node, edges):
        return [edge for edge in edges if edge.start == node]

    @staticmethod
    def find_most_frequent_edge(edges):
        return max(edges, key=lambda x: x.count) if len(edges) > 0 else None

    @staticmethod
    def get_percentile_frequency(edges, eta):
        return np.percentile(np.array([edge.count for edge in edges]), eta)
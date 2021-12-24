class BPMN:
    def __init__(self, i, o, T, and_gateways, xor_gateways, or_gateways, edges):
        self.i = i
        self.o = o
        self.T = T
        self.and_gateways = and_gateways
        self.xor_gateways = xor_gateways
        self.or_gateways = or_gateways
        self.edges = edges

    def format(self):
        result = {}
        for edge in self.edges:
            source = edge.start
            target = edge.end
            if source not in result:
                result[source] = [target]
            else:
                if target not in result[source]:
                    result[source].append(target)
        return result

    def __repr__(self):
        return f"i:{self.i}, o:{self.o}, T:{self.T}, AND:{self.and_gateways}, XOR:{self.xor_gateways}, OR:{self.or_gateways}, Edges:{len(self.edges)},{self.edges})"
from collections import defaultdict


class GraphEdge:
    def __init__(self, start, end, count=0):
        self.is_loop = start == end
        self.short_loop_count = defaultdict(lambda: 0)
        self.start = start
        self.end = end
        self.count = count

    def __key(self):
        return self.start, self.end

    def check_if_inverse_of_other(self, other):
        return self.start == other.end and self.end == other.start

    def __lt__(self, other):
        return self.count > other.count

    def __gt__(self, other):
        return self.count < other.count

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return type(self) is type(other) and self.start == other.start and self.end == other.end

    def __repr__(self):
        return f"{self.start} --> {self.end} ({self.count}, {self.is_loop})"

    def increase_frequency(self):
        self.count += 1

    def decrease_frequency(self):
        self.count -= 1
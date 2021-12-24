from subprocess import Popen, PIPE, STDOUT


class JoinMiner:

    def call(self, dfg):
        return self._format_stdout(self._call_java(dfg))

    def _call_java(self, argument: str):
        p = Popen(['java', '-jar', './data/JoinMiner.jar', str(argument), "0"],
                  stdout=PIPE, stderr=STDOUT)
        return [item.decode('utf-8').rstrip() for item in p.stdout]

    def _format_stdout(self, stdout):
        stdout = stdout[0].replace("JOIN_join_", "").replace('AND', 'and').replace('XOR', 'xor').replace('OR', 'or')
        stdout = stdout.split(", ")
        edges = set()
        for edge in stdout:
            edges.add(tuple(edge.split('->')))
        return edges
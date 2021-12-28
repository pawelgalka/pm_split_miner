def prepare_artificial_traces():
    fake_log = [
        ["a", "b", "c", "g", "e", "h"],
        ["a", "b", "c", "g", "e", "h"],
        ["a", "b", "c", "g", "e", "h"],
        ["a", "b", "c", "g", "e", "h"],
        ["a", "b", "c", "g", "e", "h"],
        ["a", "b", "c", "g", "e", "h"],
        ["a", "b", "c", "g", "e", "h"],
        ["a", "b", "c", "g", "e", "h"],
        ["a", "b", "c", "g", "e", "h"],
        ["a", "b", "c", "g", "e", "h"],
        ["a", "b", "c", "f", "g", "h"],
        ["a", "b", "c", "f", "g", "h"],
        ["a", "b", "c", "f", "g", "h"],
        ["a", "b", "c", "f", "g", "h"],
        ["a", "b", "c", "f", "g", "h"],
        ["a", "b", "c", "f", "g", "h"],
        ["a", "b", "c", "f", "g", "h"],
        ["a", "b", "c", "f", "g", "h"],
        ["a", "b", "c", "f", "g", "h"],
        ["a", "b", "c", "f", "g", "h"],
        ["a", "b", "d", "g", "e", "h"],
        ["a", "b", "d", "g", "e", "h"],
        ["a", "b", "d", "g", "e", "h"],
        ["a", "b", "d", "g", "e", "h"],
        ["a", "b", "d", "g", "e", "h"],
        ["a", "b", "d", "g", "e", "h"],
        ["a", "b", "d", "g", "e", "h"],
        ["a", "b", "d", "g", "e", "h"],
        ["a", "b", "d", "g", "e", "h"],
        ["a", "b", "d", "g", "e", "h"],
        ["a", "b", "d", "e", "g", "h"],
        ["a", "b", "d", "e", "g", "h"],
        ["a", "b", "d", "e", "g", "h"],
        ["a", "b", "d", "e", "g", "h"],
        ["a", "b", "d", "e", "g", "h"],
        ["a", "b", "d", "e", "g", "h"],
        ["a", "b", "d", "e", "g", "h"],
        ["a", "b", "d", "e", "g", "h"],
        ["a", "b", "d", "e", "g", "h"],
        ["a", "b", "d", "e", "g", "h"],
        ["a", "b", "e", "c", "g", "h"],
        ["a", "b", "e", "c", "g", "h"],
        ["a", "b", "e", "c", "g", "h"],
        ["a", "b", "e", "c", "g", "h"],
        ["a", "b", "e", "c", "g", "h"],
        ["a", "b", "e", "c", "g", "h"],
        ["a", "b", "e", "c", "g", "h"],
        ["a", "b", "e", "c", "g", "h"],
        ["a", "b", "e", "c", "g", "h"],
        ["a", "b", "e", "c", "g", "h"],
        ["a", "b", "e", "d", "g", "h"],
        ["a", "b", "e", "d", "g", "h"],
        ["a", "b", "e", "d", "g", "h"],
        ["a", "b", "e", "d", "g", "h"],
        ["a", "b", "e", "d", "g", "h"],
        ["a", "b", "e", "d", "g", "h"],
        ["a", "b", "e", "d", "g", "h"],
        ["a", "b", "e", "d", "g", "h"],
        ["a", "b", "e", "d", "g", "h"],
        ["a", "b", "e", "d", "g", "h"],
        ["a", "c", "b", "e", "g", "h"],
        ["a", "c", "b", "e", "g", "h"],
        ["a", "c", "b", "e", "g", "h"],
        ["a", "c", "b", "e", "g", "h"],
        ["a", "c", "b", "e", "g", "h"],
        ["a", "c", "b", "e", "g", "h"],
        ["a", "c", "b", "e", "g", "h"],
        ["a", "c", "b", "e", "g", "h"],
        ["a", "c", "b", "e", "g", "h"],
        ["a", "c", "b", "e", "g", "h"],
        ["a", "c", "b", "f", "g", "h"],
        ["a", "c", "b", "f", "g", "h"],
        ["a", "c", "b", "f", "g", "h"],
        ["a", "c", "b", "f", "g", "h"],
        ["a", "c", "b", "f", "g", "h"],
        ["a", "c", "b", "f", "g", "h"],
        ["a", "c", "b", "f", "g", "h"],
        ["a", "c", "b", "f", "g", "h"],
        ["a", "c", "b", "f", "g", "h"],
        ["a", "c", "b", "f", "g", "h"],
        ["a", "d", "b", "e", "g", "h"],
        ["a", "d", "b", "e", "g", "h"],
        ["a", "d", "b", "e", "g", "h"],
        ["a", "d", "b", "e", "g", "h"],
        ["a", "d", "b", "e", "g", "h"],
        ["a", "d", "b", "e", "g", "h"],
        ["a", "d", "b", "e", "g", "h"],
        ["a", "d", "b", "e", "g", "h"],
        ["a", "d", "b", "e", "g", "h"],
        ["a", "d", "b", "e", "g", "h"],
        ["a", "d", "b", "f", "g", "h"],
        ["a", "d", "b", "f", "g", "h"],
        ["a", "d", "b", "f", "g", "h"],
        ["a", "d", "b", "f", "g", "h"],
        ["a", "d", "b", "f", "g", "h"],
        ["a", "d", "b", "f", "g", "h"],
        ["a", "d", "b", "f", "g", "h"],
        ["a", "d", "b", "f", "g", "h"],
        ["a", "d", "b", "f", "g", "h"],
        ["a", "d", "b", "f", "g", "h"]
    ]
    traces = []
    for trace in fake_log:
        traces.append(
            ['Start'] + trace + ['End'])
    print("DFG TRACES", traces)
    return traces
package pl.edu.agh;

import java.util.Collection;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Optional;
import java.util.Queue;
import java.util.Set;
import java.util.Stack;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import org.jbpt.algo.tree.rpst.IRPSTNode;
import org.jbpt.algo.tree.rpst.RPST;
import org.jbpt.graph.DirectedEdge;
import org.jbpt.graph.MultiDirectedGraph;
import org.jbpt.hypergraph.abs.IVertex;
import org.jbpt.hypergraph.abs.Vertex;

public class JoinMiner {
    private final Graph graph;
    private final RPST<DirectedEdge, Vertex> rpst;

    public JoinMiner(RPST<DirectedEdge, Vertex> rpst, Graph graph) {
        this.rpst = rpst;
        this.graph = graph;
    }

    public void discoverJoins() {
        Queue<IRPSTNode<DirectedEdge, Vertex>> bottomUpRpstNodeQueue = this.buildBottomUpQueue();

        while (!bottomUpRpstNodeQueue.isEmpty()) {
            IRPSTNode<DirectedEdge, Vertex> firstNode = bottomUpRpstNodeQueue.poll();
            Set<BpmnVertex> setOfTasksComposingFirstNode = this.getBpmnNodesFromRpstNode(firstNode);
            Set<DirectedEdge> setOfEdgesComposingFirstNode = new HashSet<>(firstNode.getFragment());

            for (BpmnVertex task : setOfTasksComposingFirstNode) {
                List<DirectedEdge> commonEdgesToGivenNode = this.getCommonEdgesToGivenNode(setOfEdgesComposingFirstNode,
                        task);
                if (commonEdgesToGivenNode.size() > 1 && !task.isGate()) {
                    String joinGateName = "join_" + task.getName();
                    BpmnVertex joinGate = new BpmnVertex(joinGateName, true, BpmnNodeType.UNDEFINED);
                    this.addJoinGateToBpmnGraph(commonEdgesToGivenNode, task, joinGate);
                    if (this.checkIfContainsBackEdge(joinGate)) {
                        joinGate.setNodeType(BpmnNodeType.XORJOIN);
                        joinGate.setName("XORJOIN_" + joinGateName);
                    } else {
                        Function<BpmnNodeType, BpmnNodeType> convertGateToGeneralKind = this::convertGateToGeneralKind;
                        if (this.checkIfHomogenous(firstNode, convertGateToGeneralKind)) {
                            BpmnNodeType nodeType = this.getHomogenousNodeType(firstNode, convertGateToGeneralKind);
                            joinGate.setNodeType(nodeType);
                            String nodeName = nodeType.toString();
                            joinGate.setName(nodeName + "_" + joinGateName);
                        } else {
                            joinGate.setNodeType(BpmnNodeType.ORJOIN);
                            joinGate.setName("ORJOIN_" + joinGateName);
                        }
                    }
                }
            }
        }

        this.updateGraph();
    }

    private BpmnNodeType convertGateToGeneralKind(BpmnNodeType nodeType) {
        if (nodeType.equals(BpmnNodeType.XORSPLIT)) {
            return BpmnNodeType.XORJOIN;
        } else if (nodeType.equals(BpmnNodeType.ANDSPLIT)) {
            return BpmnNodeType.ANDJOIN;
        } else {
            return nodeType.equals(BpmnNodeType.ORSPLIT) ? BpmnNodeType.ORJOIN : nodeType;
        }
    }

    private BpmnNodeType getHomogenousNodeType(IRPSTNode<DirectedEdge, Vertex> rpstNode,
            Function<BpmnNodeType, BpmnNodeType> generalKindOfGateConverter) {
        return this.getGatesTypes(this.getBpmnNodesFromRpstNode(rpstNode))
                .map(generalKindOfGateConverter).findAny().orElseThrow(RuntimeException::new);
    }

    private boolean checkIfHomogenous(IRPSTNode<DirectedEdge, Vertex> rpstNode,
            Function<BpmnNodeType, BpmnNodeType> generalKindOfGateConverter) {
        Set<BpmnVertex> bpmnNodes = this.getBpmnNodesFromRpstNode(rpstNode);
        long distinctGateTypeCounter = this.getGatesTypes(bpmnNodes).map(generalKindOfGateConverter).distinct().count();
        return distinctGateTypeCounter == 1;
    }

    private Stream<BpmnNodeType> getGatesTypes(Set<BpmnVertex> bpmnNodes) {
        return bpmnNodes.stream().filter(BpmnVertex::isGate).map(BpmnVertex::getNodeType)
                .filter((nodeType) -> !nodeType.equals(BpmnNodeType.UNDEFINED));
    }

    private List<DirectedEdge> getCommonEdgesToGivenNode(Set<DirectedEdge> edgesComposingRpstNodes, BpmnVertex node) {
        List<DirectedEdge> EdgesFromRpstGraphToGivenNode = edgesComposingRpstNodes.stream()
                .filter((edge) -> edge.getTarget().equals(node)).collect(Collectors.toList());
        return this.graph.getEdges().stream()
                .filter((directedEdge) -> directedEdge.getTarget().equals(this.getBpmnEquivalentNode(node)))
                .filter((directedEdge) -> this.isEdgeInList(EdgesFromRpstGraphToGivenNode, directedEdge))
                .collect(Collectors.toList());
    }

    private boolean isEdgeInList(List<DirectedEdge> bpmnGraphEdgesToGivenNodes, DirectedEdge edgeToCheck) {
        return bpmnGraphEdgesToGivenNodes.stream().anyMatch((edge) -> edge.getTarget().getName().equals(
                edgeToCheck.getTarget().getName())
                && edge.getSource().getName().equals(edgeToCheck.getSource().getName()));
    }

    private boolean checkIfContainsBackEdge(BpmnVertex joinGate) {
        Collection<DirectedEdge> bpmnEdges = this.graph.getEdges();
        List<DirectedEdge> edgesToGate = bpmnEdges.stream().filter((edge) -> edge.getTarget().equals(joinGate))
                .collect(Collectors.toList());
        Iterator<DirectedEdge> directedEdgeIterator = edgesToGate.iterator();

        BpmnVertex source;
        BpmnVertex gate;
        do {
            if (!directedEdgeIterator.hasNext()) {
                return false;
            }
            DirectedEdge edgeToGate = directedEdgeIterator.next();
            source = (BpmnVertex) edgeToGate.getSource();
            gate = (BpmnVertex) edgeToGate.getTarget();
        } while (!this.isPathBetweenNodes(gate, source) || !this.isNodeTopologicalDeeper(source, gate));

        return true;
    }

    private boolean isNodeTopologicalDeeper(BpmnVertex firstNode, BpmnVertex secondNode) {
        List<Vertex> topologicalSorted = this.topologicalSort(this.graph);
        int indexOfsecondNode = topologicalSorted.indexOf(secondNode);
        return indexOfsecondNode != -1 && topologicalSorted.subList(indexOfsecondNode, topologicalSorted.size())
                .contains(firstNode);
    }

    private List<Vertex> topologicalSort(MultiDirectedGraph graph) {
        Map<Vertex, Boolean> visited = new HashMap<>();
        graph.getVertices().forEach((vertexx) -> visited.put(vertexx, false));
        Stack<Vertex> sortStack = new Stack<>();

        for (Vertex vertex : graph.getVertices()) {
            if (!(Boolean) visited.get(vertex)) {
                this.topologicalSortHelper(vertex, visited, sortStack, graph);
            }
        }

        return new LinkedList<>(sortStack);
    }

    private void topologicalSortHelper(Vertex vertex, Map<Vertex, Boolean> visited, Stack<Vertex> sortStack,
            MultiDirectedGraph graph) {
        visited.put(vertex, true);

        for (Vertex neighbour : graph.getDirectSuccessors(vertex)) {
            this.topologicalSortHelper(neighbour, visited, sortStack, graph);
        }

        sortStack.push(vertex);
    }

    private boolean isPathBetweenNodes(BpmnVertex source, BpmnVertex target) {
        Map<IVertex, Boolean> visited = new HashMap<>();
        MultiDirectedGraph multiDirectedGraph = this.graph;
        Collection<Vertex> vertices = multiDirectedGraph.getVertices();
        vertices.forEach((vertex) -> visited.put(vertex, false));
        LinkedList<Vertex> queue = new LinkedList<>();
        visited.put(source, true);
        queue.add(source);

        while (!queue.isEmpty()) {
            Vertex currentNode = queue.poll();

            for (Vertex neighbour : multiDirectedGraph.getDirectSuccessors(currentNode)) {
                if (neighbour.equals(target)) {
                    return true;
                }
                visited.put(neighbour, true);
                queue.add(neighbour);
            }
        }

        return false;
    }

    private void addJoinGateToBpmnGraph(List<DirectedEdge> commonEdges, BpmnVertex node, BpmnVertex joinGate) {
        MultiDirectedGraph graph = this.graph;
        BpmnVertex bpmnEquivalentNode = this.getBpmnEquivalentNode(node);
        graph.addEdge(joinGate, bpmnEquivalentNode);
        commonEdges.stream().filter((bpmnEdge) -> bpmnEdge.getTarget().equals(bpmnEquivalentNode))
                .forEach((bpmnEdge) -> bpmnEdge.setTarget(joinGate));
    }

    private BpmnVertex getBpmnEquivalentNode(BpmnVertex nodeFromRpst) {
        return (BpmnVertex) this.graph.getVertices().stream()
                .filter((node) -> node.getName().equals(nodeFromRpst.getName())).findFirst()
                .orElseThrow(RuntimeException::new);
    }

    private Set<BpmnVertex> getBpmnNodesFromRpstNode(IRPSTNode<DirectedEdge, Vertex> rpstNode) {
        Set<BpmnVertex> nodes = new HashSet<>();
        Object[] rpstNodeFragments = rpstNode.getFragment().toArray();

        for (Object edge : rpstNodeFragments) {
            DirectedEdge directedEdge = (DirectedEdge) edge;
            BpmnVertex sourceNode = (BpmnVertex) directedEdge.getSource();
            BpmnVertex targetNode = (BpmnVertex) directedEdge.getTarget();
            nodes.add(sourceNode);
            nodes.add(targetNode);
        }

        return nodes;
    }

    public Queue<IRPSTNode<DirectedEdge, Vertex>> buildBottomUpQueue() {
        RPST<DirectedEdge, Vertex> rpst = this.rpst;
        Map<IRPSTNode<DirectedEdge, Vertex>, Integer> depthMap = this.getDepthMap(rpst);
        Comparator<Entry<IRPSTNode<DirectedEdge, Vertex>, Integer>> depthComparator = Entry.comparingByValue(
                Comparator.reverseOrder());
        List<IRPSTNode<DirectedEdge, Vertex>> sortedNodesByDepth = depthMap.entrySet().stream().sorted(depthComparator)
                .map(Entry::getKey).collect(Collectors.toList());

        LinkedList<IRPSTNode<DirectedEdge, Vertex>> bottomUpRpstNodeQueue;
        IRPSTNode<DirectedEdge, Vertex> node;
        for (bottomUpRpstNodeQueue = new LinkedList<>(); !sortedNodesByDepth.isEmpty(); sortedNodesByDepth.remove(
                node)) {
            node = sortedNodesByDepth.get(0);
            bottomUpRpstNodeQueue.add(node);
            Collection<IRPSTNode<DirectedEdge, Vertex>> directPredecessors = rpst.getDirectPredecessors(node);
            Optional<IRPSTNode<DirectedEdge, Vertex>> predecessor = directPredecessors.stream().findFirst();
            if (predecessor.isPresent()) {
                Collection<IRPSTNode<DirectedEdge, Vertex>> neighbours = rpst.getDirectSuccessors(predecessor.get());
                IVertex finalNode = node;
                neighbours.stream().filter((neighbour) ->
                                !neighbour.equals(finalNode) && !bottomUpRpstNodeQueue.contains(neighbour))
                        .forEach((neighbour) -> {
                            bottomUpRpstNodeQueue.add(neighbour);
                            sortedNodesByDepth.remove(neighbour);
                        });
                bottomUpRpstNodeQueue.add(predecessor.get());
                sortedNodesByDepth.remove(predecessor.get());
            }
        }

        return bottomUpRpstNodeQueue;
    }

    private Map<IRPSTNode<DirectedEdge, Vertex>, Integer> getDepthMap(RPST<DirectedEdge, Vertex> rpst) {
        Map<IRPSTNode<DirectedEdge, Vertex>, Integer> depthMap = new HashMap<>();
        int actualDepth = 0;
        IRPSTNode<DirectedEdge, Vertex> root = rpst.getRoot();
        depthMap.put(root, actualDepth);
        this.populateDepthMap(root, depthMap);
        return depthMap;
    }

    private void updateGraph() {
        Collection<Vertex> graphVertices = this.graph.getVertices();

        for (Vertex vertex : graphVertices) {
            BpmnVertex bpmnVertex = (BpmnVertex) vertex;
            Collection<DirectedEdge> incomingEdges = this.graph.getIncomingEdges(bpmnVertex);
            if (incomingEdges.size() > 1 && !bpmnVertex.isGate()) {
                String joinGateName = "join_" + bpmnVertex.getName();
                BpmnVertex joinGate = new BpmnVertex(joinGateName, true, BpmnNodeType.ORJOIN);
                this.graph.addEdge(joinGate, bpmnVertex);
                incomingEdges.forEach((bpmnEdge) -> bpmnEdge.setTarget(joinGate));
                joinGate.setName("ORJOIN_" + joinGateName);
            }
        }

    }

    private void populateDepthMap(
            IRPSTNode<DirectedEdge, Vertex> root, Map<IRPSTNode<DirectedEdge, Vertex>, Integer> depthMap) {
        Set<IRPSTNode<DirectedEdge, Vertex>> rpstNodes = this.rpst.getRPSTNodes();
        Map<IRPSTNode<DirectedEdge, Vertex>, Boolean> visited = new HashMap<>();
        rpstNodes.forEach((node) -> visited.put(node, false));
        Queue<IRPSTNode<DirectedEdge, Vertex>> bfsQueue = new LinkedList<>();
        bfsQueue.add(root);
        visited.put(root, true);
        depthMap.put(root, 0);

        while (!bfsQueue.isEmpty()) {
            IRPSTNode<DirectedEdge, Vertex> vertex = bfsQueue.peek();
            bfsQueue.poll();
            Collection<IRPSTNode<DirectedEdge, Vertex>> directSuccessors = this.rpst.getDirectSuccessors(vertex);

            for (IRPSTNode<DirectedEdge, Vertex> successor : directSuccessors) {
                if (!(Boolean) visited.get(successor)) {
                    depthMap.put(successor, depthMap.get(vertex) + 1);
                    bfsQueue.add(successor);
                    visited.put(successor, true);
                }
            }
        }

    }
}

package pl.edu.agh;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.stream.IntStream;

import org.jbpt.graph.MultiDirectedGraph;
import org.jbpt.hypergraph.abs.Vertex;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

public class Graph extends MultiDirectedGraph {

    public Graph(String jsonRepresentation) throws JSONException {
        JSONObject json = new JSONObject(jsonRepresentation);
        Map<String, Vertex> vertexMap = createVertexes(json);
        createEdges(json, this, vertexMap);
    }

    private static Map<String, Vertex> createVertexes(JSONObject jsonObject) throws JSONException {
        JSONArray keys = jsonObject.names();
        HashMap<String, Vertex> vertexMap = new HashMap<>();

        IntStream.range(0, keys.length())
                .forEach(i -> {
                    try {
                        String key = keys.getString(i);
                        addNodeToMapping(vertexMap, key);
                    } catch (JSONException ignored) {
                    }
                });

        return vertexMap;
    }

    private static void addNodeToMapping(Map<String, Vertex> vertexMap, String key) {
        boolean isNodeGate = checkIfGate(key);
        BpmnNodeType nodeType = getNodeTypeFromDescription(key);
        vertexMap.put(key, new BpmnVertex(key, isNodeGate, nodeType));
    }

    private static BpmnNodeType getNodeTypeFromDescription(String description) {
        if (checkIfGate(description)) {
            if (description.startsWith("xor")) {
                return BpmnNodeType.XORSPLIT;
            }

            if (description.startsWith("and")) {
                return BpmnNodeType.ANDSPLIT;
            }
        }

        return BpmnNodeType.EVENT;
    }

    private static boolean checkIfGate(String nodeDescription) {
        String preprocessedNode = nodeDescription.toLowerCase();
        return preprocessedNode.startsWith("xor") || preprocessedNode.startsWith("and");
    }

    private static void createEdges(JSONObject jsonObject, MultiDirectedGraph graph, Map<String, Vertex> vertexMapper)
            throws JSONException {
        JSONArray keys = jsonObject.names();

        IntStream.range(0, keys.length())
                .forEach(i -> {
                    try {
                        addEdgeToGraph(jsonObject, graph, vertexMapper, keys, i);
                    } catch (JSONException ignored) {
                    }
                });

    }

    private static void addEdgeToGraph(JSONObject jsonObject, MultiDirectedGraph graph,
            Map<String, Vertex> vertexMapper,
            JSONArray keys, int i) throws JSONException {
        String key = keys.getString(i);
        String valueString = jsonObject.getString(key).replace("[", "").replace("]", "").replace("\"", "");
        if (!valueString.equals("")) {
            List<String> list = new ArrayList<>(Arrays.asList(valueString.split(",")));

            String target;
            for (Iterator<String> listIter = list.iterator(); listIter.hasNext(); graph.addEdge(vertexMapper.get(key),
                    vertexMapper.get(target))) {
                target = listIter.next();
                if (!vertexMapper.containsKey(target)) {
                    addNodeToMapping(vertexMapper, target);
                }
            }
        }
    }
}

enum BpmnNodeType {
    EVENT,
    XORSPLIT,
    XORJOIN,
    ANDSPLIT,
    ANDJOIN,
    ORJOIN,
    UNDEFINED,
    ORSPLIT;
}

class BpmnVertex extends Vertex {
    private final boolean isGate;
    private BpmnNodeType nodeType;

    public BpmnVertex(String name, boolean isGate, BpmnNodeType nodeType) {
        super(name);
        this.isGate = isGate;
        this.nodeType = nodeType;
    }

    public boolean isGate() {
        return this.isGate;
    }

    public BpmnNodeType getNodeType() {
        return this.nodeType;
    }

    public void setNodeType(BpmnNodeType nodeType) {
        this.nodeType = nodeType;
    }
}

package pl.edu.agh;

import org.jbpt.algo.tree.rpst.RPST;
import org.json.JSONException;

public class Main {

    public static void main(String[] args) throws JSONException {
        String inputBpmn = args[0];
        System.out.println(discoverJoins(inputBpmn));
    }

    private static String discoverJoins(String inputBpmn) throws JSONException {
        Graph graph = new Graph(inputBpmn);
        JoinMiner joinMiner = new JoinMiner(new RPST<>(graph), graph);
        joinMiner.discoverJoins();
        return graph.toString();
    }
}

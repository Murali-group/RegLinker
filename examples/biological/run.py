'''
Demonstration of the use of RegLinker in a biological context.

For the purposes of this demonstration, we'll derive an edge-labeled graph
G=(V, E), representing the interactome. The labels on the edges of the graph
will indicate whether or not the edge is known to be annotated as belonging
to a pathway of interest, represented as a subgraph P of G.

Additionally, we'll designate the nodes in P that correspond to receptors as
sources for G, and the nodes in P that correspond to transcription factors as
targets.

We'll also derive a graph H from the DFA represention of a regular expression
of interest.
'''

import itertools
import sys
sys.path.append('../../')

import RegLinker as rl 
import RegLinkerIO as rlio

def main():
    # Interactome (G)
    interactome_file = open('input/interactome.tsv', 'r')

    # Pathway of interest (used for G's edge labels and sources/targets)
    pathway_edges_file = open('input/pathways/Wnt-edges.txt', 'r')
    pathway_nodes_file = open('input/pathways/Wnt-nodes.txt', 'r')

    # Regular expression of interest (H)
    dfa_edges_file = open('input/three-xs-edges.tsv', 'r')
    dfa_nodes_file = open('input/three-xs-nodes.tsv', 'r')

    # Parse the interactome 
    # Note: additional re-weighting (using random walks) was performed in the
    # RegLinker paper. The weights in this file are based on the strength
    # of evidence for the interaction. 
    G = rlio.read_graph(interactome_file, weight_col=2)

    # Parse the pathway and annotate G accordingly
    P = rlio.read_graph(pathway_edges_file)

    ps = set(P.edges())
    xs = set(G.edges()) - ps

    # Edges in the pathway are labeled 'p'
    for u, v in ps:
        G[u][v]['l'] = 'p'

    # Edges not in the pathway are labeled 'x'
    for u, v in xs:
        G[u][v]['l'] = 'x'

    # The source/target node sets of the pathway are used 
    # as the sources and target node sets of G
    S_G, T_G = rlio.read_node_types(
        pathway_nodes_file,
        source_kws=['receptor'],
        target_kws=['tf'])

    # Parse the DFA (p*xp*xp*xp*): three x's surrounded by
    # any configuration of p's
    H = rlio.read_graph(dfa_edges_file, label_col=2)
    S_H, T_H = rlio.read_node_types(dfa_nodes_file)

    # Run the RegLinker algorithm
    # Note: all paths are generated, so this may take a minute or two
    results = rl.RegLinker(G, H, S_G, T_G, S_H, T_H, label="l", weight="w")

    for r in itertools.islice(results, 5):
        print(r)


if __name__ == '__main__':
    main()

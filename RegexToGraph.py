'''
This module provides a utility functions that leverage the FAdo package to
derive and write to file a graph representation of a given regular expression. 

Note: FAdo requires Python 2, and so is incompatible with the code for
RegLinker, which requires Python 3.

Note: FAdo generates a .tablereg file during execution. This file is
unimportant, and can be ignored.
'''

import sys

import networkx as nx
from FAdo.reex import str2regexp

def regex_to_graph(regex_as_string):
    regex = str2regexp(regex_as_string)
    dfa = regex.nfaPosition().toDFA().dump()

    return make_graph_from_dfa(dfa)


def make_graph_from_dfa(dfa):
    V = dfa[1]
    E = dfa[3]
    sources = dfa[4]
    targets = dfa[5]

    G = nx.DiGraph()

    for v in V:
        # FAdo uses strings for nodes but ints for edge tails/heads
        v = int(v)
        label = get_node_label(v, sources, targets)

        G.add_node(v, label=label)

    for u, l, v in E:
        label = get_edge_label(l, dfa[2])
        G.add_edge(u, v, label=label)

    return G


def get_node_label(node, sources, targets):
    if node in sources:
        return 'source'
    if node in targets:
        return 'target'
    return 'none'


def get_edge_label(index, labels):
    return labels[index]


def write_graph_to_file(G, prefix):
    with open(prefix + '-nodes.txt', 'w') as f:
        
        # Write header
        f.write('# Node\t' + 'Type\n')

        # Write nodes
        for v in G.nodes():
            f.write(str(v) + '\t' + G.node[v]['label'] + '\n')

    with open(prefix + '-edges.txt', 'w') as f:
        # Write header
        f.write('# Tail\t' + 'Head\t' + 'Label\n')
        
        # Write edges 
        for e in G.edges():
            u, v = (e[0], e[1])
            f.write(str(u) + '\t' + str(v) + '\t' + G[u][v]['label'] + '\n')


if __name__ == '__main__':
    regex = sys.argv[1]
    prefix = sys.argv[2]
    G = regex_to_graph(regex)
    write_graph_to_file(G, prefix)

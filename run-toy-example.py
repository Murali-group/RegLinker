import RegLinker as rl
import RegLinkerIO as rlio

# Open file handles
net_file = open('input/toy/network.tsv', 'r') 
net_nodes_file = open('input/toy/net-nodes.tsv', 'r')

dfa_file = open('input/toy/dfa.tsv', 'r') 
dfa_nodes_file = open('input/toy/dfa-nodes.tsv', 'r')


# Read networks in. Here, label_col and weight_col refer to the
# 0-indexed column of the corresponding TSV file.

G = rlio.read_graph(net_file, label_col=2, weight_col=3)
S_G, T_G = rlio.read_node_types(net_nodes_file) 

H = rlio.read_graph(dfa_file, label_col=2)
S_H, T_H = rlio.read_node_types(dfa_nodes_file)

results = rl.RegLinker(G, H, S_G, T_G, S_H, T_H, label="l", weight="w")

for r in results:
    print(r)

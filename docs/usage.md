# Usage

This document describes the usage of RegLinker and RegLinkerIO
modules.

## Repository Contents

The following files are likely to be of interest to users:

- `RegLinker.py`: contains the code that implements the RegLinker
  algorithm

- `RegLinkerIO.py`: contains utility functions for reading
  inputs from and writing outputs to disk.

- `RegexToGraph.py`: a Python 2 utility (incompatible with the rest of
   the Python files in this repository!) for transforming a regular
   expression into a graph, and for writing that graph to disk.

- `run-signaling-pathway-example.py`: example demonstrating the use of
  RegLinker to identify candidate interactions for inclusion in a signaling
  pathway. Note that the example given is a demonstration of the technique
  applied, not a full reproduction of the pipeline used in the published
  manuscript; for example, an additional re-weighting procedure was applied in
  the paper).

- `run-toy-example.py`: example (described in detail below) of 
  the use of RegLinker on a small sample network and DFA.

- `input/toy/*`: contains toy examples of graphs that the module RegLinkerIO
  can interface with. These are as tab-separated edge lists of the form
  `head<tab>tail<tab>label<tab>weight`. Note that the graph representation of
  a DFA does not utilize the weight column.

- `input/signaling-pathway/*`: contains input files used in the RegLinker
  paper for signaling pathway reconstruction (the signaling pathways are
  derived from NetPath; the interactome is a directed human protein interactome
  constructed from numerous protein-protein interaction and signaling
  databases, including BioGrid, DIP, InnateDB, IntAct, MatrixDB, MINT, NetPath,
  and PhosphoSitePlus.

## RegexToGraph

This module is intended to be run as a command-line utility. As a Python 2
program, its dependencies are detailed separately in *requirements-regex.txt*.

Example invocations:

```bash
# Produces a DFA matching the string "ppn"
python RegexToGraph.py ppn two-ps-then-an-n

# Produces a DFA matching a string that has three xs surrounded by
# any number of ps
python RegexToGraph.py "p*xp*xp*xp*" three-xs-any-ps
```

## Toy Example

Suppose we have the following toy example network *G*, where an edges
are labeled with either *p* or *n*. We designate the ndoe *s* to serve
as the network's source, and *t* to serve as its target.

<img src="./network.svg">

Suppose also, as a regular language constraint, we wish to finds all
the paths in *G* that start with a a *p*-labeled edge, then use an
*x*-labeled edge, then terminate with zero of more *p*-labeled edges.
The DFA corresponding to this regular language is as follow:

In this case, the vertex *q* is the start state, and the vertex *f* is
the final state.

<img src="./dfa.svg">

As explained above, files corresponding these networks have been
stored under the `examples` folder. The following Python code will
read them in:

### IO

The file RegLinkerIO.py contains some convenient utility functions for
reading and writing results to disk.

```python
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
```

### RegLinker

The inputs to RegLinker are a set of sources, a set of targets, an edge-labeled
network, and the DFA coresponding to a regular language. RegLinker computes,
for each edge in the interaction network, a shortest path from the set of
sources to the set of targets through that edge, such that each path is
*regular language constrained*: that is, the concatentation of the labels of
the edges along the path forms a word in the specified regular language. This
is achieved through finding paths in an appropriately-defined product of the
interaction network and the DFA.  

Definitions:
- *G*: NetworkX DiGraph representing an interaction network
- *S<sub>G</sub>*: Iterable of sources for *G*
- *T<sub>G</sub>*: Iterable of targets for *G*

- *H*: DFA, represented as a NetworkX DiGraph
- *S<sub>H</sub>*: Iterable of start states for *H* 
- *T<sub>H</sub>*: Iterable of final states *H*

Each edge in *G* and each edge in *H* must be labeled using a common
dictionary attribute. Each edge in *G* must also have a common
attribute to denote an edge weight.

With these inputs in hand, RegLinker can be imported and run as
follows:

```python
import RegLinker as rl

results = rl.RegLinker(G, H, S_G, T_G, S_H, T_H, label="l", weight="w")
```

This will create a generator that yields tuples of the form:

```python
(edge, path, G_path, H_path, labeled_path, cost, rank)
```

Here:
- *edge* is the edge considered
- *path* is the path found in the product graph
- *G\_path\_* and *H\_path\_* are the paths formed by
  projecting the product *path* onto *G* and *H*
- *labeled\_path* is *path*, annotated with edge labels
- *cost* is the sum of the weights of the path
- *rank* is an ordering of the paths, from lowest to highest cost. A
  rank of zero indicates the lowest-cost path.

These tuples are produced in ascending order of rank.

Considering our example networks, it is clear that there are two paths
that fit our desired constraint. The first path (and shortest) is
*s-u-v-t*, and the second is *s-u-t*. Printing the results will yield
the following:

```
>>> for r in results: print(r)
...
((('s', 'q'), ('u', 'q')), [('s', 'q'), ('u', 'q'), ('v', 'f'), ('t', 'f')], ['s', 'u', 'v', 't'], ['q', 'q', 'f', 'f'], [('s', 'u', 'p'), ('u', 'v', 'x'), ('v', 't', 'p')], 3.0, 0)
((('u', 'q'), ('v', 'f')), [('s', 'q'), ('u', 'q'), ('v', 'f'), ('t', 'f')], ['s', 'u', 'v', 't'], ['q', 'q', 'f', 'f'], [('s', 'u', 'p'), ('u', 'v', 'x'), ('v', 't', 'p')], 3.0, 0)
((('v', 'f'), ('t', 'f')), [('s', 'q'), ('u', 'q'), ('v', 'f'), ('t', 'f')], ['s', 'u', 'v', 't'], ['q', 'q', 'f', 'f'], [('s', 'u', 'p'), ('u', 'v', 'x'), ('v', 't', 'p')], 3.0, 0)
((('u', 'q'), ('t', 'f')), [('s', 'q'), ('u', 'q'), ('t', 'f')], ['s', 'u', 't'], ['q', 'q', 'f'], [('s', 'u', 'p'), ('u', 't', 'x')], 4.0, 1)
```

The output consists of four lines, corresponding to the four edges
through which we were able to find an *s-t* path in *G* conforming to
our constraints. 

## Identifying Signaling Pathway Interactions

Please see `run-signaling-pathway-example.py` for a demonstration
of the use of RegLinker in its motivating biological context.

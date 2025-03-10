import igraph as ig
import pydot
import networkx as nx
import matplotlib.pyplot as plt
import json


tokens_def = ['9.1', '23', '5', '4', '*', '*', '+', '2', '110.3', '2', '-', '*', '-'] 

class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None



def build_the_tree(infix_tokens):
    stack = []

    for token in infix_tokens:
        if token in '+-/*^':
            new_node = TreeNode(token)
            new_node.left = stack.pop()
            new_node.right = stack.pop()
            stack.append(new_node)
        else:
            stack.append(TreeNode(token))

    return stack[0]

def visualise_tree(root):
    graph = pydot.Dot(graph_type="digraph", rankdir="TB")  # Format for top to bottom undirected binary tree 

    def add_nodes_edges(node, parent_name=None):
        if node:
            node_name = f'"{node.value}"' # This ensures the node identifiers are unique by adding a number if a repeat is found
            graph.add_node(pydot.Node(node_name, label=node.value, shape="circle"))

            if parent_name:
                graph.add_edge(pydot.Edge(parent_name, node_name))

            add_nodes_edges(node.left, node_name)
            add_nodes_edges(node.right, node_name)

    add_nodes_edges(root)
    graph.write_png("my_expression_tree.png")






# Create a Graphviz graph

# Add nodes and edges
root = build_the_tree(tokens_def)

visualise_tree(root)


#pos = nx.drawing.nx_pydot.graphviz_layout(G, prog="dot")


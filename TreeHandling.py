import igraph as ig
import pydot
import networkx as nx
import matplotlib.pyplot as plt
import json
import TermClass as tc
import ShuntingPolish as sp
from collections import defaultdict
import re


def preprocess_unary(expr: str) -> str:
    # 1) At start of the string
    expr = re.sub(r'^\s*-(?=\d|\w|\()', '(0-1)*', expr)
    # 2) Immediately after an opening parenthesis
    expr = re.sub(r'(?<=\()\s*-(?=\d|\w|\()', '(0-1)*', expr)
    return expr

class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.parent = None

    def __repr__(self):
        return f"{self.value}"


def convert_to_term(val):
    """
    Converts the input to a Term where possible
    if already a Term just returns it as is
    if starts with a - the minus is ignored 
        and the rest is converted to a Term 
        and then the Term is negated
    if its neither the program tries to oconvert it to a Term
    if there is an issue it returns None
    """
    if isinstance(val, tc.Term):
        return val
    s = str(val)
    if s.startswith('-'):
        base = convert_to_term(s[1:])
        return -base
    try:
        term = tc.Term(val)
        return term
    except Exception as e:
        # print(f"[TermParseError] Failed to convert {repr(val)} to Term: {e}")
        return None
    

def depth_first_traversal(root:TreeNode):
    """
    Note: This is an in-order depth first traversal
    """
    if root is None:
        return []

    result = depth_first_traversal(root.left)
    result.append(root.value)
    result.extend(depth_first_traversal(root.right))

    return result


def depth_first_traversal2(root:TreeNode):
    """
    Note: This is an post-order depth first traversal
    """
    if root is None:
        return []

    result = depth_first_traversal2(root.left)
    result.extend(depth_first_traversal2(root.right))
    result.append(root.value)
    return result

def simplify_tree(mynode:TreeNode):
    """
    Recursively simplifies the AST by combining like terms
    """

    if mynode is None:
        return None
    
    # Recurses over whole tree and simplifies sub trees as much as possible
    mynode.left = simplify_tree(mynode.left)
    mynode.right = simplify_tree(mynode.right)

    # Only processes the operator nodes with operand (these are always leaves)
    if isinstance(mynode.value, str) and mynode.value in '+-/*^':
        if (mynode.left and mynode.right and 
            not isinstance(mynode.left.value, str) and 
            not isinstance(mynode.right.value, str)):

            # Convert both operands to Term objects so they can be simplified
            if isinstance(mynode.left.value, tc.Term):
                left = mynode.left.value
            else:
                left = convert_to_term(mynode.left.value)

            if isinstance(mynode.right.value, tc.Term):
                right = mynode.right.value
            else:
                right = convert_to_term(mynode.right.value)
            
            
            # print(f"left: {left}")
            # print(f"right: {right}")

            # print(f"mynode: {mynode}, mynode type: {type(mynode)}")
            try:
                # Attempts to simplify
                if mynode.value == '+':
                    result = left + right
                elif mynode.value == '-':
                    result = left - right
                elif mynode.value == '/':
                    result = left / right
                elif mynode.value == '*':
                    result = left * right
                elif mynode.value == '^':
                    result = left ** right
                else:
                    return mynode # If cannot be simplified it is left as is
                # print(f"left variables: {left.variables}")
                # print(f"right variables: {right.variables}")
                # print(f"result: {result}")
                
                # Handles unlike terms that cannot be simplified
                if result == "UNLIKE":
                    new_node = TreeNode(mynode.value)
                    new_node.left = TreeNode(left)
                    new_node.right = TreeNode(right)
                    return new_node
                elif result is not None:
                    return TreeNode(result) # Otherwise replaces the operator node with the result
                
            # Handles error and prevents crash
            except Exception as e:
                print(f"Could not simplify {left} {mynode.value} {right}: {e}")
            
    return mynode

def build_the_tree(postfix_tokens):
    stack = []
    for token in postfix_tokens:
        if token in '+-/*^':
            # Before popping, verify there are enough operands.
            if len(stack) < 2:
                raise ValueError(f"Insufficient operands for operator '{token}' "
                                 f"in postfix expression: {postfix_tokens}")
            new_node = TreeNode(token)
            new_node.right = stack.pop()
            new_node.left = stack.pop()
            stack.append(new_node)
        else:
            try:
                # Attempt to create a Term object from the token.
                stack.append(TreeNode(tc.Term(token)))
            except Exception:
                stack.append(TreeNode(token))
    if len(stack) != 1:
        raise ValueError("Malformed expression: final stack has more than one element.")
    return stack[0]



def visualise_tree(root):
    """
    Makes image from the tree
    """
    graph = pydot.Dot(graph_type="digraph", rankdir="TB")  # Format for top to bottom undirected binary tree 

    def add_nodes_edges(node, parent_name=None):
        if node:
            node_name = id(node) # This ensures the node identifiers are unique by adding a number if a repeat is found
            label = str(node.value).replace('"', r'\"')  # Escape quotes
            graph.add_node(pydot.Node(node_name, label=f'"{label}"', shape="circle"))

            if parent_name:
                graph.add_edge(pydot.Edge(parent_name, node_name))

            add_nodes_edges(node.left, node_name)
            add_nodes_edges(node.right, node_name)

    add_nodes_edges(root)
    graph.write_png("my_expression_tree.png")


def flatten_add_tree(node):
    # if node is addition, recurse both sides
    if isinstance(node.value, str) and node.value == '+':
        return flatten_add_tree(node.left) + flatten_add_tree(node.right)
    # if node is a Term, return it
    elif isinstance(node.value, tc.Term):
        return [node.value]
    # else try converting node value into a Term
    else:
        term = convert_to_term(node.value)
        if term is not None:
            return [term]
        # if something else (e.g. an unsimplified operator),
        # raises error
        raise ValueError(f"Cannot flatten node {node!r}")
    
def flatten_sum(node):
    """
    Flattens a sum/difference sub tree into a list of Term objects

    Recursively breaks down the + and - operations into a flat list of Terms
    Handles subtraction by negation
    """
    if node is None:
        return []

    if node.value == '+':
        return flatten_sum(node.left) + flatten_sum(node.right)

    if node.value == '-':
        return flatten_sum(node.left) + [ -each_term for each_term in flatten_sum(node.right) ]

    if isinstance(node.value, tc.Term):
        return [node.value]

    each_term = convert_to_term(node.value)
    if each_term is not None:
        return [each_term]
    raise ValueError(f"Cannot flatten non-sum node {node!r}")

def distribute_fractions(node):
    """
    Distributes sums on a numerator in an AST 
    
    Traverses the AST and restructures division nodes to apply the denominator
    to each term in the numerator sum. Only acts on / nodes where the numerator
    is a sum/difference.

    Assumes the denominator (right child of /) is a single term.
    Uses the flatten_sum function to decompose the numerator into terms.
    """
    if node is None:
        return None

    node.left  = distribute_fractions(node.left)
    node.right = distribute_fractions(node.right)

    if node.value == '/':
        terms = flatten_sum(node.left)

        denom_term = None
        if isinstance(node.right.value, tc.Term):
            denom_term = node.right.value
        else:
            denom_term = convert_to_term(node.right.value)

        if denom_term is not None:
            new_leaves = [t / denom_term for t in terms]

            new_nodes = [TreeNode(t_leaf) for t_leaf in new_leaves]


            result = new_nodes[0]
            for nxt in new_nodes[1:]:
                plus = TreeNode('+')
                plus.left  = result
                plus.right = nxt
                result = plus

            return result

    return node

def collect_like_terms(terms):
    """
    This ensures that the like terms are collected
    """
    grouped = {}
    for t in terms:
        # Split variable dictionary into list of tuples to be sorted:
        # e.g. {'x':1,'y':2} → (('x','1'),('y','2'))
        key = tuple(sorted((var, repr(exp)) for var, exp in t.variables.items()))
        if key in grouped:
            grouped[key] = grouped[key] + t
        else:
            grouped[key] = t
    return list(grouped.values())

def render_sum(terms: list[tc.Term]) -> str:
    """
    Given a list of Term objects (some possibly with negative coeffs),
    produce a string like "9x^2 - 12x^3 + 5".
    """
    if not terms:
        return "0"
    parts = []
    for i, t in enumerate(terms):
        s = repr(t)
        if i == 0:
            # First term, print its sign if it's negative, e.g. "-5x"
            parts.append(s)
        else:
            if s.startswith('-'):
                # Negative: drop the leading '-' and prepend ' - '
                parts.append(' - ' + s[1:])
            else:
                # Positive: prepend ' + '
                parts.append(' + ' + s)
    return ''.join(parts)

def simplify_all_additions(root):
    flat_terms = flatten_sum(root)
    combined   = collect_like_terms(flat_terms)
    # Returns the combined terms back in string format
    return render_sum(combined)


def build_and_simplify(text):
    """
    Brings all functions together to build and simplify the tree from text input
    """
    # handle unary minus
    text = preprocess_unary(text)

    # shunting‑yard then postfix then build AST
    postfix = sp.get_infix(text)
    root   = build_the_tree(postfix)

    # collapse *, /, ^
    simplified = simplify_tree(root)

    # if it collapsed down to a single Term, just return it:
    if isinstance(simplified.value, tc.Term):
        return repr(simplified.value)

    #Deals with distribution if need be
    distributed = distribute_fractions(simplified)

    # Handles sum of terms
    if distributed.value == '+':
        return simplify_all_additions(distributed)
    
    

    # If none of those work just render the raw infix traversal
    return " ".join(str(v) for v in depth_first_traversal(distributed))




if __name__ == '__main__':
    # tokens_def = ['9.1x', '234x', '5x', '4x', '*', '*', '+', '2x', '110.3x', '2x', '-', '*', '-'] 
    # # Create a Graphviz graph

    # # Add nodes and edges
    # root = build_the_tree(tokens_def)

    # # visualise_tree(root)

    # print(depth_first_traversal(root))
    # print(depth_first_traversal2(root))

    # x = simplify_tree(root)
    # # print(type(x))
    # print(f"Post order: {depth_first_traversal2(x)}")
    # print(f"In order: {depth_first_traversal(x)}")

    my_expression = "3x + 2x + 4y"
    my_expression2 = "3x + 4y + 2x"
    my_expression3 = "3x + 4y + 2x"
    my_expression = "(-5x)^2"

    my_answer = build_and_simplify(my_expression)
    print(f"1: {my_answer}")

    my_expression = "(3x^2 - 4x + 2y + 4y) / (3x)"
    print(build_and_simplify(my_expression))


    #pos = nx.drawing.nx_pydot.graphviz_layout(G, prog="dot")


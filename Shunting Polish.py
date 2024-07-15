#Shunting yard algorithm/ Reverse Polish Notation
import re
import matplotlib.pyplot as plt
import json
operators = []
operands = []
output = []

with open('commands.json') as file:
    myfile = json.load(file)
    greeks = myfile["greek"]

sample = "4.5+3.2 / (9.1 -  6 )"
sample = list(filter((lambda a:a != " "), sample))
sample = "".join(sample)

class Node:
    def __init__(self, data):
        self.data = data
        self.children = []


def check_precedence(op1:str, op2:str):
    """
    Checks if the first operator has greater precedence than the second operator
    returns True if op1 has greater precedence, False if op2 has greater precedence otherwise returns None
    """
    ops = [("(",")"),("^"),("/","*"),("+","-")]
    op1_order = False
    op2_order = False
    for x in ops:
        if op1 in x:
            op1_order = ops.index(x)
        if op2 in x:
            op2_order = ops.index(x)
    if op1_order < op2_order:
        return True
    elif op2_order < op1_order:
        return False
    elif op2_order ==  op1_order:
        return None

def typesetting(text):
    """
    Working with greek letters for now

    Automatically changes certain values in the input QLineEdit to their corresponding LaTeX values

    Args:
    text : str
    """

    x = greeks.keys() #what we are expecting
    for key in x:
        key = r'\b' + key + r'\b'


    y = greeks.values() # what we are changing it to
    # a = r'(\S+)\s*/\s*(\S+)|(\S+)/(\S+)' #Ignore this it is regex for fractions still in work

    #This forces the program to search through the list several times rather than doing just 2 passes
    # Look through the text find the matches in the dictionary
    matches = re.findall(x,text)

    finds = []
    #matching each key to its relevant value it needs to be changed to in the form of a list of tuples
    for match in matches:
        i = x.index(match)
        v = y[i]
        finds.append((match, v))
    
    for find in finds:
        
        ...
    
    print(finds)


    
    print(matches)

    # if x:
    #     return text


def is_float(entry):
    try:
        float(entry)
        return True
    except ValueError:
        return False

def is_op(entry):
    if str(entry) in "+/*()-^":
        return True
    else:
        return False

def tokenize(entry):
    regex = r'[+/*()-^]|\d+.?\d+?|'
    gl = '|'.join(re.escape(value) for value in greeks.values())
    regex = regex + '|' + gl
    print(regex)
    tokens = re.findall(regex, entry)
    print(tokens)
    return tokens

def peek_the_stack():
    """
    Returns None if the stack is empty
    """
    try:
        operators[-1]
    except IndexError:
        return None


# Implementation of the actual shunting yard algorithm
print(sample)
sample = tokenize(sample)
tokens = sample
print(type(sample))
i = 0
while i < len(sample):
    token = tokens[i]
    if is_float(token):
        output.append(token)
    else:
        # operators.append(token)
        # while check_precedence(operators[-1], token):
        #operators.append(token)
        pass

    i += 1 

# print(operands)
# print(operators)
# print(check_precedence("/","+"))
# print(check_precedence("-","+"))
# print(check_precedence("^","("))
# print(is_op("+"))
# print(is_op(9))
# print(operators[-1])
print(tokens)

for token in tokens:
    x = Node(token)



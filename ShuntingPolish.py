#Shunting yard algorithm/ Reverse Polish Notation
import re
import matplotlib.pyplot as plt
import json

with open('commands.json') as file:
    myfile = json.load(file)
    global maths_funcs
    global greeks
    maths_funcs = myfile["functions"]
    greeks = myfile["greek"]

def initialise_and_clean(text_input):
    with open('commands.json') as file:
        myfile = json.load(file)
        greeks = myfile["greek"]

    sample = list(filter((lambda a:a != " "), text_input))
    sample = "".join(sample)
    return sample

# class Node:
#     def __init__(self, data):
#         self.data = data
#         self.children = []


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
    matches = re.search(x,text)

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


def tokenize(entry):
    test = "9.1 + 23 * 5*4- (110.3 -2) + alpha"
    myregex = r'(\d+\.?\d*|\.\d+|[+/*()-^]'
    gl = '|'.join(re.escape(value) for value in greeks.keys())
    myregex = myregex + '|' + gl + ')'
    tokens = re.findall(myregex, entry)
    i = 0
    while i < len(tokens) - 1:
        if not(tokens[i] in "+/*-^" or tokens[i+1] in "+/*-^()"):
            print("Before change:",tokens, "\n and token 1", tokens[i], "and token 2", tokens[i+1])
            tokens.insert(i, "*")
            print("After change:",tokens)
            i += 1
        i += 1
    return tokens


def peek_and_compare(item, stack:list, queue:list):
    ordered_operators = "+-/*^"
    if stack:
        x = stack[0]
        a = ordered_operators.index(item)
        b = ordered_operators.index(x)
        while b > a:
            x = stack[0]
            b = ordered_operators.index(x)
            queue.append(stack.pop())
        stack.append(b)



def convert_to_infix(tokens:list):
    ordered = []
    operators = []
    mystack = [] # values appended to the end of the list and popped from the end
    myqueue = [] #values appended to the end of the list and popped from the front
    flag = False
    status = None
    for x in tokens:
        token = x
        regex = r'\d+\.?\d*'
        y = re.match(regex, token)
        print(myqueue)
        print(token)
        if y:
            #print(y.group())
            status = "number"
            myqueue.append(token)
        elif token in "+-/*^":
            status = "operator"
            ordered_operators = "(+-/*^"
            if mystack:
                y = mystack[-1]
                a = ordered_operators.index(token)
                b = ordered_operators.index(y)
                while b > a:
                    y = mystack[-1]
                    print(y)
                    b = ordered_operators.index(y)
                    myqueue.append(mystack.pop())
                    print("sorting out operators")
                    print(myqueue)
            mystack.append(token)
        elif token == '(':
            status = "left_bracket"
            mystack.append(token)
        elif token == ')':
            status = "right_bracket"
            print(mystack)
            while mystack[-1] != '(' and len(mystack) != 0:
                print("sorting out brackets")
                print(myqueue)
                print(mystack)
                myqueue.append(mystack.pop())
            mystack.remove('(')
    while mystack:
        myqueue.append(mystack.pop())

        
    return myqueue


if __name__ == '__main__':
    #More advanced test
    test = "9.1 + 23 * 5*4- (110.3 -2) alpha"
    #Test with implied multiplication
    test = "9.1 + 23 * 5*4 - 2(110.3 -2)"
    # Test with just numbers
    #test = "9.1 + 23 * 5*4- (110.3 -2)"
    #Simpler test
    #test = "9.1 + 23 * 5*4"
    # Implementation of the actual shunting yard algorithm
    sample = initialise_and_clean(test)
    print(sample)
    sample = tokenize(sample)
    print(type(sample))
    print(sample)
    i = 0
    print(convert_to_infix(sample))


    # while i < len(sample):
    #     token = tokens[i]
    #     if is_float(token):
    #         output.append(token)
    #     else:
    #         # operators.append(token)
    #         # while check_precedence(operators[-1], token):
    #         #operators.append(token)
    #         pass

    #     i += 1 

    # print(operands)
    # print(operators)
    # print(check_precedence("/","+"))
    # print(check_precedence("-","+"))
    # print(check_precedence("^","("))
    # print(is_op("+"))
    # print(is_op(9))
    # print(operators[-1])
    # print(tokens)


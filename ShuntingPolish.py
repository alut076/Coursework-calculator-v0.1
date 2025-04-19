#Shunting yard algorithm/ Reverse Polish Notation
import re
import matplotlib.pyplot as plt
import json
import networkx as nx

with open('commands.json') as file:
    # Loads up the relevant files
    myfile = json.load(file)
    # Sets the greek letters and functions dictionaries as global variables so they can be accessed anywhere
    global maths_funcs
    global greeks
    maths_funcs = myfile["functions"]
    greeks = myfile["greek"]

def initialise_and_clean(text_input):
    with open('commands.json') as file:
        myfile = json.load(file)
        greeks = myfile["greek"]

    # Removes all whitespace
    sample = list(filter((lambda a:a != " "), text_input))
    sample = "".join(sample)
    return sample



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

#Attempted go at a typesetting function, was never implemented
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
    # Sets up regex to match tokens and then matches them
    gl = '|'.join(re.escape(value) for value in greeks.keys())
    pattern = r'(\d+\.?\d*|\.\d+|[-+/*()^]|' + gl + r'|[a-zA-Z])'
    tokens = re.findall(pattern, entry)
    
    # Helper to decide if a token is an operand (i.e. one that can be multiplied)
    def is_operand(token):
        # operands include numbers, letters, greek names, and closing parentheses.
        return (token.isdigit() or token.replace('.', '', 1).isdigit() or 
                token.isalpha() or token in greeks.keys() or token == ')')
    
    def is_prefix(token):
        # tokens that can appear immediately after an operand to require an implicit multiplication:
        # numbers, letters, greek names, or an opening parenthesis.
        return (token.isdigit() or token.replace('.', '', 1).isdigit() or 
                token.isalpha() or token in greeks.keys() or token == '(')
    
    # Rebuild the token list inserting an explicit '*' where implicit multiplication is intended.
    if not tokens:
        return tokens

    result = [tokens[0]]  # do not need to modify first token

    for token in tokens[1:]:
        # if the last token in result is an operand and the current token is a prefix that should be multiplied,
        # then insert an explicit multiplication operator "*".
        if is_operand(result[-1]) and is_prefix(token):
            result.append('*')
        result.append(token)
    
    return result



def convert_to_postfix(tokens: list):
    mystack = []  # operator stack
    output = []   # postfix output queue

    for token in tokens:
        # If token is a number, variable, or greek letter, add it to output
        regex = r'(\d+\.?\d*|\.\d+|' + '|'.join(re.escape(k) for k in greeks.keys()) + r'|[a-zA-Z])'
        if re.match(regex, token):
            output.append(token)
        elif token in "+-/*^":
            # While the top of stack is an operator with higher or equal precedence:
            while (mystack and mystack[-1] != '(' and 
                   check_precedence(mystack[-1], token)):
                output.append(mystack.pop())
            mystack.append(token)
        elif token == '(':
            mystack.append(token)
        elif token == ')':
            # Pop until matching '(' is found.
            while mystack and mystack[-1] != '(':
                output.append(mystack.pop())
            if mystack and mystack[-1] == '(':
                mystack.pop()  # Remove the '(' from the stack
            else:
                raise ValueError("Mismatched parentheses")
    # Pop any remaining operators
    while mystack:
        if mystack[-1] in "()":
            raise ValueError("Mismatched parentheses")
        output.append(mystack.pop())

    return output

    
def get_infix(text):
    """
    Brings all the relevant functons together to convert the text
    to a list of postfix tokens
    """
    print(f"initial text: {text}")
    cleaned = initialise_and_clean(text)
    print(f"cleaned text: {cleaned}")
    in_order_tokens = tokenize(cleaned)
    print(f"in order tokens: {in_order_tokens}")
    postfix_tokens = convert_to_postfix(in_order_tokens)
    return postfix_tokens



if __name__ == '__main__':
    #More advanced test
    # test = "9.1 + 23 * 5*4- (110.3 -2) alpha"
    # #Test with implied multiplication
    # test = "9.1 + 23 * 5*4 - 2(110.3 -2)"
    # # Test with just numbers
    # #test = "9.1 + 23 * 5*4- (110.3 -2)"
    # #Simpler test
    # #test = "9.1 + 23 * 5*4"
    # # Implementation of the actual shunting yard algorithm
    # sample = initialise_and_clean(test)
    # print(sample)
    # sample = tokenize(sample)
    # #print(type(sample))
    # print(sample)
    # i = 0
    # x = convert_to_postfix(sample)
    # print(x)
    #making_the_graph(x)

    my_expression = "3.3x(2.5) * 9.3x * 24x - 12x"
    my_expression = "(3x)^2"
    my_expression = "5x + 5x"
    print(tokenize("-3-3"))

    sample = initialise_and_clean(my_expression)
    sample = tokenize(sample)
    print(sample)



    # print(operands)
    # print(operators)
    # print(check_precedence("/","+"))
    # print(check_precedence("-","+"))
    # print(check_precedence("^","("))
    # print(is_op("+"))
    # print(is_op(9))
    # print(operators[-1])
    # print(tokens)


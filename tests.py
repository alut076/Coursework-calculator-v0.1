# This file will be solely for isolating and testing sections
# of the code that may not work
import re
import json

with open('commands.json') as file:
    myfile = json.load(file)
    global maths_funcs
    global greeks
    maths_funcs = myfile["functions"]
    greeks = myfile["greek"]


test = r"9.1 + 23 * 5*4- (110.3 -2) + \alpha"
myregex = r'(\d+\.?\d*|\.\d+|[+/*()-^]'
gl = '|'.join(repr(value) for value in greeks.values())
myregex = myregex + '|' + gl + ')'
x = re.findall(myregex, test)
print(x)

#Currently can capture the greek letters without the slashes however to convert them for
#output the best option may be to 
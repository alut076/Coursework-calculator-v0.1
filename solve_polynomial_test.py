import re
#user_input = str(input("Your equation"))
class myVar:
    def __init__(self, degree:float, variable:str, coefficient):

        self.degree = degree
        self.coefficient = coefficient
        self.variable = variable

    def __add__(self, other):
        if self.degree == other.degree:
            new_coeff = self.coefficient + other.coefficient
            result = myVar(self.degree, new_coeff)

    def __str__(self):
        return f"{self.coefficient}"





user_input = "x^2 +2x -3 = 0"
contains_equals = True if "=" in user_input else False
print(contains_equals)
if contains_equals:
    lhs, rhs = user_input.split("=")

print(lhs)
print(rhs)
#expression = r'\W'
#print(re.findall(expression,user_input))

a = myVar(2, "x", 3)

#for count, val in enumerate(user_input):
#    if val == 'x':
#        coeff = user_input[count-1]
        

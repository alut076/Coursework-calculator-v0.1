import re

'''
This is to convert terms into Term objects with their specific attributes
'''

test_cases = ["41", "x^12", "i", "x^2ab^3", "23ab^3c^4", "23.5x^ab^2"]

class Term:
    def __init__(self, term=None, variables=None, coeff=1):
        self.variables = variables if variables is not None else {}
        self.coeff = coeff
        self.term = term

        if self.term:
            myterm = term

            temp = re.match(r'-?\d+(?:\.\d+)?', myterm)
            if temp:
                self.coeff = float(temp.group(0))
                myterm = myterm[temp.span()[1]:]
            else:
                self.coeff = 1

            # print("before, remaining term:", myterm, "coeff:", self.coeff, "variables:", self.variables)

            vars = re.findall(r'\w\^\d+(?:\.\d+)?', myterm)
            varsplace = list(re.finditer(r'\w\^\d+(?:\.\d+)?', myterm))

            if vars:
                for var in vars:
                    a = re.split(r'\^', var)
                    x = a[0]
                    y = float(a[1])
                    self.variables[x] = y



            for place in reversed(varsplace):
                myterm = myterm[:place.span()[0]] + myterm[place.span()[1]:]

            for each in myterm:
                self.variables[each] = 1


            # print("after, remaining term:", myterm, "coeff:", self.coeff, "variables:", self.variables)
        

    def __add__(self, other):
        if self.variables == other.variables:
            new_coeff = self.coeff + other.coeff
            return Term(variables=self.variables, coeff=new_coeff)
        else:
            return None

    def __sub__(self, other):
        if self.variables == other.variables:
            new_coeff = self.coeff - other.coeff
            return Term(variables=self.variables, coeff=new_coeff)
        else:
            return None

    def __mul__(self, other):
        new_coeff = self.coeff * other.coeff
        new_vars = {}

        for self_var, self_pow in self.variables.items():
            if self_var in other.variables.keys():
                new_vars[self_var] = self_pow + other.variables[self_var]
            else:
                new_vars[self_var] = self_pow
        
        for other_var, other_pow in other.variables.items():
            if other_var not in self.variables.keys():
                new_vars[other_var] = other_pow
        
        return Term(variables=new_vars, coeff=new_coeff)

    def __truediv__(self, other):
        new_coeff = self.coeff / other.coeff
        new_vars = {}

        for self_var, self_pow in self.variables.items():
            if self_var in other.variables.keys():
                new_vars[self_var] = self_pow - other.variables[self_var]
            else:
                new_vars[self_var] = self_pow
        
        for other_var, other_pow in other.variables.items():
            if other_var not in self.variables.keys():
                new_vars[other_var] = -1 * other_pow
        
        return Term(variables=new_vars, coeff=new_coeff)

    def __repr__(self):
        term_string = ""

        if not self.variables:
            return str(self.coeff)
        
        for each_var, each_pow in self.variables.items():
            a = str(each_var) + "^" + str(each_pow)
            term_string += a

        if self.coeff == 1:
            return term_string
        elif self.coeff == -1:
            term_string = "-" + term_string
            return term_string
        else:
            term_string = str(self.coeff) + term_string
            return term_string
        
    
        

        








# for each_test in test_cases:
#     x = Term(each_test)


x = "3x^2y"
y = "4x^2"
z = "125x^3"
a = "3.5x^2y"
b = "12334"
c = "3531.51"

print(x, "+", a, "=", (Term(x) + Term(a)))
print(b, "/", z, "=", (Term(b) / Term(z)))
import re
'''
This is to convert terms into Term objects with their specific attributes
'''

# some test cases
test_cases = ["41", "x^12", "i", "x^2ab^3", "23ab^3c^4", "23.5x^ab^2"]

class Term:
    def __init__(self, term=None, variables=None, coeff=1):
        self.variables = variables if variables is not None else {}
        self.coeff = coeff
        self.term = term

        if self.term: # if the term is created by passing something for the term parameter
            
            # Checks for any stray operators and raises error if there are any
            if any(op in term for op in ['*', '/', '+', '(', ')']) or ('-' in term[1:]): 
                raise ValueError(f"[InvalidTerm] Malformed term: {term}")
            myterm = term # Temporary variable to hold the term value passed in

            # Regex to catch coefficient
            temp = re.match(r'-?\d+(?:\.\d+)?', myterm)
            # Converts the coefficient to a Fraction instance
            if temp:
                self.coeff = Fraction(temp.group(0))
                myterm = myterm[temp.span()[1]:]
            else:
                self.coeff = Fraction("1")

            # print("before, remaining term:", myterm, "coeff:", self.coeff, "variables:", self.variables)

            # Regex to catch variables and their powers if they have any
            vars = re.findall(r'\w\^\d+(?:\.\d+)?', myterm)
            varsplace = list(re.finditer(r'\w\^\d+(?:\.\d+)?', myterm))

            # Generates the variables dictionary attribute from the variables found
            if vars:
                for var in vars:
                    a = re.split(r'\^', var)
                    x = a[0]
                    y = Fraction(a[1])
                    self.variables[x] = y

            #Removes all variables with specified exponents so those with no specified exponent can be handled
            for place in reversed(varsplace):
                myterm = myterm[:place.span()[0]] + myterm[place.span()[1]:]

            # Handles remaining variables without specified exponents
            for each in myterm:
                self.variables[each] = Fraction("1")
            
            # print("after, remaining term:", myterm, "coeff:", self.coeff, "variables:", self.variables)
        

    def __add__(self, other):
        """
        Add 2 Term instances
        Checks if they are like
        For like terms Adds the coefficients and keeps the variables
        Otherwise returns "UNLIKE"
        """
        if self.variables == other.variables:
            new_coeff = self.coeff + other.coeff
            return Term(variables=self.variables, coeff=new_coeff)
        else:
            return "UNLIKE"

    def __sub__(self, other):
        """
        Subtracts 2 Term instances
        Checks if they are like
        For like terms Subtracts the coefficients and keeps the variables
        Otherwise returns "UNLIKE"
        """
        # print(self.variables)
        # print(other.variables)
        # print(self.variables == other.variables)
        if self.variables == other.variables:
            new_coeff = self.coeff - other.coeff
            return Term(variables=self.variables, coeff=new_coeff)
        else:
            return "UNLIKE"

    def __mul__(self, other):
        """
        Multiplies 2 Term instances
        Multiplies the coefficients
        Adds variable powers
        """
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
        """
        Divides 2 Term instances
        Divides the coefficients
        Subtracts variable powers
        does this by multiplying the second Term's variable powers by -1 and then adding them
        """
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

        for var in list(new_vars.keys()):
            if new_vars[var] == Fraction("0"):
                del new_vars[var]
        
        return Term(variables=new_vars, coeff=new_coeff)
        

    def __repr__(self):
        """
        Gets string representation of the Term
        """
        term_string = ""

        # If there are no variables gets the coefficient as is
        if not self.variables:
            return str(self.coeff)
        
        # Handles the variable and powers
        # If the variable has a power of 1 the power is not added on just the variable
        # Otherwise the variable and power are separated by a ^
        for each_var, each_pow in self.variables.items():
            print(f"each_pow: {each_pow}")
            if repr(each_pow) == '1':
                a = str(each_var)
            else:
                a = str(each_var) + "^" + str(each_pow)
            term_string += a

        # If the coefficient is 1 it is ignored
        # If hte coefficient is -1 the coefficient is ignored 
        # and a - added to the front
        # Otherwise handled normally
        if self.coeff == Fraction("1"):
            return term_string
        elif self.coeff == Fraction("-1"):
            term_string = "-" + term_string
            return term_string
        else:
            term_string = str(self.coeff) + term_string
            return term_string
        
    def __pow__(self,other):
        # If the power does not have any variables
        # The coefficient is raised to the power
        # And the variables are multiplied by the power
        # Variable powers have not been accounted for yet
        if isinstance(other,Term) and other.variables == {}:
            new_coeff = self.coeff ** other.coeff
            new_vars = {}
            for var, pow in self.variables.items():
                new_vars[var] = pow * other.coeff
            return Term(variables=new_vars,coeff=new_coeff)
        else:
            return "INVALID"
        
    def __neg__(self):
    # gets negative value of coefficient and keeps variables the same
        return Term(variables=self.variables.copy(),
                    coeff=self.coeff * Fraction("-1"))
        

#Euclidean Algorithm for finding HCF

# recursive approach
def hcf_recur(a,b):
    if b > a:
        a, b = b, a
    if b != 0:
        return hcf_recur(b,a%b)
    return a

def hcf_iter(a,b):
    while b != 0:
        if b > a:
            a, b = b, a
        a, b = b, a % b
    return a

def list_hcf(my_list:list):
    my_list1 = my_list[:]
    while len(my_list1) > 1:
        i = my_list1[-1]
        j = my_list1[-2]
        x = hcf_iter(i,j)
        my_list1.pop()
        my_list1.pop()
        my_list1.append(x)
    return my_list1[0]

def factor_2_vars(term1:Term,term2:Term):
    """
    Finds common variable factors of 2 Term instances
    """
    factors = {}
    for each_key in list(term1.variables.keys()):
        if each_key in list(term2.variables.keys()):
            if term1.variables[each_key] < term2.variables[each_key]:
                factors[each_key] = term1.variables[each_key]
            else:
                factors[each_key] = term2.variables[each_key]
    return factors
        

def factor_vars(terms:list):
    """
    Factors variable factors for list of Terms
    """
    factors = terms[:]
    while len(factors) > 1:
        x = factors.pop()
        y = factors.pop()
        z = factor_2_vars(x,y)
        factors.append(Term(variables=z,coeff=1))
    return factors[0]


def full_factor(terms:list):
    """
    Finds both the coefficient factor and variable factors of a list of Terms
    And then returns the factor as a Term
    """
    var_factors = factor_vars(terms=terms).variables
    temp_list = []
    # print(terms)
    for each in terms:
        temp_list.append(each.coeff)
        # print(f"The term is {each}")
    coeff_factors = list_hcf(temp_list)
    # print(f"The list of coefficients is {temp_list}")
    # print(f"the coefficient factor is {coeff_factors}")
    # print(f"The variable factor is {var_factors}")
    return Term(variables=var_factors,coeff=coeff_factors)
   

class Fraction:
    def __init__(self,val:str=None,num=None,den=None, isIrrational=False):
        # print("A")
        self.isIrrational = isIrrational
        # if the instance is not irrational
        if self.isIrrational == False:
            if val:
                x = re.split(r'\.', val) # Splits the term based off of the decimal
                # print(x)
                if len(x) == 2: # if there is one decimal place
                    self.den = 10 ** (len(x[1])) # multiples by 10 to the power of number of digits after the decimal
                    if x[0] != '0': # If the stuff before the decimal is not just a 0 it is included in the numerator
                        self.num = x[0] + x[1]
                    else: # Otherwise it is not
                        self.num = x[1]
                else:
                    self.num = x[0]
                    self.den = '1'
            elif num is not None and den is not None:
                self.num = num
                self.den = den
            else:
                raise Exception("You have not entered valid parameters")
            # print("B")
            # print(f"self.num: {self.num}")
            # print(f"self.den: {self.den}")
            
            # Following code to simplify the numerator and denominator of the Fraction
            # This means that a new Fraction instance can be called if need for simplifying
            self.num = int(self.num)
            self.den = int(self.den)

            if self.num == 0:
                self.den = 1
            else:
                factor = hcf_iter(abs(self.num), abs(self.den))
                self.num //= factor
                self.den //= factor

        # if a value is specified self.val is the val parameter
        if val:
            self.val = val

        if val:
            try:
                self.val = float(self.val) # self.val is set to the float entered in as a parameter
            except:
                pass
        else:
            self.val = float(self.num/self.den) # Otherwise it is the decimal from dividing the numerator by the denominator

    def __add__(self, other):
        """
        Adds two Fractions
        If they are not irrational puts them over a common denominator and adds the numerators
        If they are irrational just adds the values
        """
        if self.isIrrational == False and other.isIrrational == False:
            new_den = int((self.den * other.den) // hcf_iter(self.den,other.den))
            num_1 = self.num * (new_den // self.den)
            num_2 = other.num * (new_den // other.den)
            num3 = num_1 + num_2
            return Fraction(num=num3,den=new_den)
        else:
            newval = self.val + other.val
            return Fraction(val=newval, isIrrational=True)

    def __sub__(self, other):
        """
        Subtracts two Fractions
        If they are not irrational puts them over a common denominator and subtracts the numerators
        If they are irrational just subtracts the values
        """
        if self.isIrrational == False and other.isIrrational == False:
            new_den = int((self.den * other.den) // hcf_iter(self.den,other.den))
            num_1 = self.num * (new_den // self.den)
            num_2 = other.num * (new_den // other.den)
            num3 = num_1 - num_2
            return Fraction(num=num3,den=new_den)
        else:
            newval = self.val - other.val
            return Fraction(val=newval, isIrrational=True)
        

    def __mul__(self,other):
        """
        Multiplies two Fractions
        If they are not irrational multiplies numerators and multiplies denominators
        If they are irrational just multiplies the values
        """
        if self.isIrrational == False and other.isIrrational == False:
            new_num = int(self.num * other.num)
            new_den = int(self.den * other.den)
            return Fraction(num=new_num,den=new_den)
        else:
            newval = self.val * other.val
            return Fraction(val=newval, isIrrational=True)

    def __truediv__(self,other):
        """
        Divides two Fractions
        If they are not irrational multiplies first numerator with second denominator for new numerator,
        and multiplies first denominator with second numerator for new denominator
        If they are irrational just divides the values
        """
        if self.isIrrational == False and other.isIrrational == False:
            if int(other.num) == 0:
                raise ZeroDivisionError("Attempted to divide by zero")
            new_num = int(self.num * other.den)
            new_den = int(self.den * other.num)
            return Fraction(num=new_num,den=new_den)
        else:
            newval = self.val / other.val
            return Fraction(val=newval, isIrrational=True)


    def __eq__(self, other):
        """
        Checks if two Fractions are equivalent
        If they are not irrational after simplifying checks if numerators are equal and denominators are equal
        If they are irrational just checks if values are equivalent
        """
        if not isinstance(other, Fraction):
            return False
        if self.isIrrational == False and other.isIrrational == False:
            a = Fraction(num=self.num,den=self.den)
            b = Fraction(num=other.num,den=other.den)
            if a.num == b.num and a.den == b.den:
                return True
            else:
                return False
        else:
            if self.val == other.val:
                return True
            else:
                return False

    def __repr__(self):
        """
        Represents Fractions as strings
        If they are not irrational and denominator is 1 just puts string as numerator
        If they are not irrational and denominator is not 1 does numerator / denominator
        If they are irrational just returns the value as a string
        """
        if self.isIrrational == False:
            if int(self.den) == 1:
                return f"{self.num}"
            else:
                return f"{self.num}/{self.den}"
        else:
            return f"{self.val}"

    def __pow__(self, other):
        """
        If the other Fraction instance has a non 1 denominator, everything is treated in decimals
        Otherwise the numerator is raised to the power and the denominator is raised to the power
        """
        if hasattr(other,"den"):
            if other.den == 1 and self.isIrrational == False and other.isIrrational == False:
                new_num = self.num ** other.num
                new_den = self.den ** other.num
                return Fraction(num=new_num, den=new_den)
        
        new_val = self.val ** other.val
        return Fraction(new_val, isIrrational=True)

    def __rmul__(self, other):
        # Ensure that if 'other' is not a Fraction, we convert it.
        if not isinstance(other, Fraction):
            other = Fraction(str(other))
        return self.__mul__(other)
        











if __name__ == '__main__':
        
    # test_list = [2768476515,7928031415,759729205,5183020840,3083405135]


    # print(list_hcf(test_list))


    # for each_test in test_cases:
    # #     x = Term(each_test)
    # x = "35x^2y"
    # y = "45x^2"
    # z = "125x^3"
    # a = "3.5x^2y"
    # b = "12334"
    # c = "3531.51"
    # d = "12334x"
    # e = "3531.51x"

    # print(f"{x}: {Term(x)}")
    # print(f"{y}: {Term(y)}")


    # print(f"Term b, {b}: {Term(b)}")
    # print(f"Term c, {c}: {Term(c)}")

    # print(f"Fraction b, {b}: {Fraction(b)}")
    # print(f"Fraction c, {c}: {Fraction(c)}")

    # print(f"{c} - {b} = {Fraction(c) - Fraction(b)}")

    # print(f"{a} + {b} = {Term(a) + Term(b)}")

    # print(f"{c} - {b} = {Term(c) - Term(b)}")

    # print(f"{e} - {d} = {Term(e) - Term(d)}")

    # print(f"{z} * {a} = {Term(z) * Term(a)}")

    # print(f"{y} / {z} = {Term(y) / Term(z)}")

    # print(f"{y} * {b} = {Term(y) * Term(b)}")


    # print(x, "+", a, "=", (Term(x) + Term(a)))
    # print(b, "/", z, "=", (Term(b) / Term(z)))

    # print(factor_2_vars(Term(x),Term(y)))

    # my_list = [Term(x),Term(y),Term(z)]
    # print(full_factor(my_list))

    # print(Term("x^2").coeff)

    # x = Fraction(num=1, den=3)
    # y = Fraction("12")
    # a = Fraction("2")
    # b = Fraction("0.5")
    # c = a ** b
    # print(f"c:{c}")
    # d = c ** c
    # z = y ** x
    # print(f"d:{d}")

    x = Term("x^2")
    y = x ** Term("2")
    # z = x ** Term(coeff=Fraction(num=1,den=3), variables={})
    print(hcf_iter(1,1))
    print(y)
    print(f"a^2/a : {Term("a^2") / Term("a")}")
    print(f"a/a : {Term("a") / Term("a")}")
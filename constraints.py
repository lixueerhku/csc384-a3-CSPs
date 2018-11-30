from csp import Constraint, Variable
import util

class TableConstraint(Constraint):
    '''General type of constraint that can be use to implement any type of
       constraint. But might require a lot of space to do so.

       A table constraint explicitly stores the set of satisfying
       tuples of assignments.'''

    def __init__(self, name, scope, satisfyingAssignments):
        '''Init by specifying a name and a set variables the constraint is over.
           Along with a list of satisfying assignments.
           Each satisfying assignment is itself a list, of length equal to
           the number of variables in the constraints scope.
           If sa is a single satisfying assignment, e.g, sa=satisfyingAssignments[0]
           then sa[i] is the value that will be assigned to the variable scope[i].


           Example, say you want to specify a constraint alldiff(A,B,C,D) for
           three variables A, B, C each with domain [1,2,3,4]
           Then you would create this constraint using the call
           c = TableConstraint('example', [A,B,C,D],
                               [[1, 2, 3, 4], [1, 2, 4, 3], [1, 3, 2, 4],
                                [1, 3, 4, 2], [1, 4, 2, 3], [1, 4, 3, 2],
                                [2, 1, 3, 4], [2, 1, 4, 3], [2, 3, 1, 4],
                                [2, 3, 4, 1], [2, 4, 1, 3], [2, 4, 3, 1],
                                [3, 1, 2, 4], [3, 1, 4, 2], [3, 2, 1, 4],
                                [3, 2, 4, 1], [3, 4, 1, 2], [3, 4, 2, 1],
                                [4, 1, 2, 3], [4, 1, 3, 2], [4, 2, 1, 3],
                                [4, 2, 3, 1], [4, 3, 1, 2], [4, 3, 2, 1]])
          as these are the only assignments to A,B,C respectively that
          satisfy alldiff(A,B,C,D)
        '''

        Constraint.__init__(self,name, scope)
        self._name = "TableCnstr_" + name
        self.satAssignments = satisfyingAssignments

    def check(self):
        '''check if current variable assignments are in the satisfying set'''
        assignments = []
        for v in self.scope():
            if v.isAssigned():
                assignments.append(v.getValue())
            else:
                return True
        return assignments in self.satAssignments

    def hasSupport(self, var,val):
        '''check if var=val has an extension to an assignment of all variables in
           constraint's scope that satisfies the constraint. Important only to
           examine values in the variable's current domain as possible extensions'''
        if var not in self.scope():
            return True   #var=val has support on any constraint it does not participate in
        vindex = self.scope().index(var)
        found = False
        for assignment in self.satAssignments:
            if assignment[vindex] != val:
                continue   #this assignment can't work it doesn't make var=val
            found = True   #Otherwise it has potential. Assume found until shown otherwise
            for i, v in enumerate(self.scope()):
                if i != vindex and not v.inCurDomain(assignment[i]):
                    found = False  #Bummer...this assignment didn't work it assigns
                    break          #a value to v that is not in v's curDomain
                                   #note we skip checking if val in in var's curDomain
            if found:     #if found still true the assigment worked. We can stop
                break
        return found     #either way found has the right truth value


class QueensConstraint(Constraint):
    '''Queens constraint between queen in row i and row j'''
    def __init__(self, name, qi, qj, i, j):
        scope = [qi, qj]
        Constraint.__init__(self,name, scope)
        self._name = "QueenCnstr_" + name
        self.i = i
        self.j = j

    def check(self):
        qi = self.scope()[0]
        qj = self.scope()[1]
        if not qi.isAssigned() or not qj.isAssigned():
            return True
        return self.queensCheck(qi.getValue(),qj.getValue())

    def queensCheck(self, vali, valj):
        diag = abs(vali - valj) == abs(self.i - self.j)
        return not diag and vali != valj
    def hasSupport(self, var, val):
        '''check if var=val has an extension to an assignment of the
           other variable in the constraint that satisfies the constraint'''
        #hasSupport for this constraint is easier as we only have one
        #other variable in the constraint.
        if var not in self.scope():
            return True   #var=val has support on any constraint it does not participate in
        otherVar = self.scope()[0]
        if otherVar == var:
            otherVar = self.scope()[1]
        for otherVal in otherVar.curDomain():
            if self.queensCheck(val, otherVal):
                return True
        return False

class QueensTableConstraint(TableConstraint):
    '''Queens constraint between queen in row i and row j, but
       using a table constraint instead. That is, you
       have to create and add the satisfying tuples.

       Since we inherit from TableConstraint, we can
       call TableConstraint.__init__(self,...)
       to set up the constraint.

       Then we get hasSupport and check automatically from
       TableConstraint
    '''
    #your implementation for Question 1 goes
    #inside of this class body. You must not change
    #the existing function signatures.
    def __init__(self, name, qi, qj, i, j):
        self._name = "Queen_" + name
        TableConstraint.__init__(self, name, [qi, qj], self.satisfyingAssignments(qi, qj, i, j))
    
    # Generate the satisfying tuples, assuming i != j
    def satisfyingAssignments(self, qi, qj, i, j):
        satisfyingAssignments = []
        for col_i in qi.domain():
            for col_j in qj.domain():
                # qi and qj are not on the same column and not diagonal
                if(col_i != col_j and abs(i - j) != abs(col_i - col_j)):
                    satisfyingAssignments.append([col_i, col_j])
        return satisfyingAssignments



class NeqConstraint(Constraint):
    '''Neq constraint between two variables'''
    def __init__(self, name, scope):
        if len(scope) != 2:
            print "Error Neq Constraints are only between two variables"
        Constraint.__init__(self,name, scope)
        self._name = "NeqCnstr_" + name

    def check(self):
        v0 = self.scope()[0]
        v1 = self.scope()[1]
        if not v0.isAssigned() or not v1.isAssigned():
            return True
        return v0.getValue() != v1.getValue()

    def hasSupport(self, var, val):
        '''check if var=val has an extension to an assignment of the
           other variable in the constraint that satisfies the constraint'''
        #hasSupport for this constraint is easier as we only have one
        #other variable in the constraint.
        if var not in self.scope():
            return True   #var=val has support on any constraint it does not participate in
        otherVar = self.scope()[0]
        if otherVar == var:
            otherVar = self.scope()[1]
        for otherVal in otherVar.curDomain():
            if val != otherVal:
                return True
        return False

class AllDiffConstraint(Constraint):
    '''All diff constraint between a set of variables'''
    def __init__(self, name, scope):
        Constraint.__init__(self,name, scope)
        self._name = "AllDiff_" + name

    def check(self):
        assignments = []
        for v in self.scope():
            if v.isAssigned():
                assignments.append(v.getValue())
            else:
                return True
        return len(set(assignments)) == len(assignments)

    def hasSupport(self, var, val):
        '''check if var=val has an extension to an assignment of the
           other variable in the constraint that satisfies the constraint'''
        if var not in self.scope():
            return True   #var=val has support on any constraint it does not participate in

        #since the contraint has many variables use the helper function 'findvals'
        #for that we need two test functions
        #1. for testing complete assignments to the constraint's scope
        #   return True if and only if the complete assignment satisfies the constraint
        #2. for testing partial assignments to see if they could possibly work.
        #   return False if the partial assignment cannot be extended to a satisfying complete
        #   assignment
        #
        #Function #2 is only needed for efficiency (sometimes don't have one)
        #  if it isn't supplied findvals will use a function that never returns False
        #
        #For alldiff, we do have both functions! And they are the same!
        #We just check if the assignments are all to different values. If not return False
        def valsNotEqual(l):
            '''tests a list of assignments which are pairs (var,val)
               to see if they can satisfy the all diff'''
            vals = [val for (var, val) in l]
            return len(set(vals)) == len(vals)
        varsToAssign = self.scope()
        varsToAssign.remove(var)
        x = findvals(varsToAssign, [(var, val)], valsNotEqual, valsNotEqual)
        return x


def findvals(remainingVars, assignment, finalTestfn, partialTestfn=lambda x: True):
    '''Helper function for finding an assignment to the variables of a constraint
       that together with var=val satisfy the constraint. That is, this
       function looks for a supporing tuple.

       findvals uses recursion to build up a complete assignment, one value
       from every variable's current domain, along with var=val.

       It tries all ways of constructing such an assignment (using
       a recursive depth-first search).

       If partialTestfn is supplied, it will use this function to test
       all partial assignments---if the function returns False
       it will terminate trying to grow that assignment.

       It will test all full assignments to "allVars" using finalTestfn
       returning once it finds a full assignment that passes this test.

       returns True if it finds a suitable full assignment, False if none
       exist. (yes we are using an algorithm that is exactly like backtracking!)'''

    # print "==>findvars([",
    # for v in remainingVars: print v.name(), " ",
    # print "], [",
    # for x,y in assignment: print "({}={}) ".format(x.name(),y),
    # print ""

    #sort the variables call the internal version with the variables sorted
    remainingVars.sort(reverse=True, key=lambda v: v.curDomainSize())
    return findvals_(remainingVars, assignment, finalTestfn, partialTestfn)

def findvals_(remainingVars, assignment, finalTestfn, partialTestfn):
    '''findvals_ internal function with remainingVars sorted by the size of
       their current domain'''
    if len(remainingVars) == 0:
        return finalTestfn(assignment)
    var = remainingVars.pop()
    for val in var.curDomain():
        assignment.append((var, val))
        if partialTestfn(assignment):
            if findvals_(remainingVars, assignment, finalTestfn, partialTestfn):
                return True
        assignment.pop()   #(var,val) didn't work since we didn't do the return
    remainingVars.append(var)
    return False


class NValuesConstraint(Constraint):
    '''NValues constraint over a set of variables.
       Among the variables in the constraint's scope the number that
       have been assigned values in the set of 'required_values' is in the range
       [lower_bound, upper_bound]
       (lower_bound <= #of variables and  #variables <= upper_bound)

       For example, if we have 4 variables V1, V2, V3, V4, each with
       domain [1, 2, 3, 4], then the call
       NValuesConstraint('test_nvalues', [V1, V2, V3, V4], [3,2], 2,
       3) will only be satisfied by assignments such that at least 2
       the V1, V2, V3, V4 are assigned the value 3 or 2, and at most 3
       of them have been assigned the value 3 or 2

    '''

    #Question 5 you have to complete the implementation of
    #check() and hasSupport. You can change __init__ if you want
    #but do not change its parameters.

    def __init__(self, name, scope, required_values, lower_bound, upper_bound):
        Constraint.__init__(self,name, scope)
        self._name = "NValues_" + name
        self._required = required_values
        self._lb = lower_bound
        self._ub = upper_bound

    def check(self):
        #Check if current variable assignments are in the satisfying set
        sum = 0
        for v in self.scope():
            #Count the number of the variables that have been assigned the required values
            if v.isAssigned():
                if v.getValue() in self._required:
                    sum += 1
            else:
                return True
        return self._lb <= sum <= self._ub


    def hasSupport(self, var, val):
        '''check if var=val has an extension to an assignment of the
           other variable in the constraint that satisfies the constraint

           HINT: check the implementation of AllDiffConstraint.hasSupport
                 a similar approach is applicable here (but of course
                 there are other ways as well)
        '''
        if var not in self.scope():
            return True  #var=val has support on any constraint it does not participate in
        
        def satisfying_lb_ub(l):
            sum = 0
            for (variable, value) in l:
                if value in self._required:
                    sum += 1
            return self._lb <= sum <= self._ub
        
        def satisfying_ub(l):
            sum = 0
            for (variable, value) in l:
                if value in self._required:
                    sum += 1
            return sum <= self._ub

        
        varsToAssign = self.scope()
        varsToAssign.remove(var)
        x = findvals(varsToAssign, [(var, val)], satisfying_lb_ub, satisfying_ub)
        return x

#Make sure all flights are assigned once
class coverAllFlight(Constraint):
    def __init__(self, name, scope, values):
        Constraint.__init__(self,name, scope)
        self._name = "coverAllFlight_" + name
        self._scope = scope
        self._values = values#values are all flights

      

    def check(self):
        flights = dict()
        for var in self.scope():
            if var.isAssigned():
                flight = var.getValue()
                if flight != 0:
                    if flight in flights:
                        flights[flight] += 1
                    else:
                        flights[flight] = 1
            else:
                return True
        if len(flights) < len(set(self._values)):#Not cover all flights
            return False
        for flight in flights:
            if flights[flight] > 1:#Assign more than once
                return False
        return True

    def hasSupport(self, var, val):
        '''check if var=val has an extension to an assignment of the
           other variable in the constraint that satisfies the constraint
        '''
        if var not in self.scope():
            return True  #var=val has support on any constraint it does not participate in
        
        def cover_all_flights(l):
            diff_flight = dict()
            for (var, val) in l:
                if val != 0:
                    if val in diff_flight:
                        diff_flight[val] += 1
                    else:
                        diff_flight[val] = 1
            if len(diff_flight) < len(set(self._values)):
                return False
            for key in diff_flight:
                if diff_flight[key] > 1:#Assign more than once
                    return False
            return True

        def could_cover_all(l):
            return len(set(self._scope)) >= len(set(self._values)) 

        
        varsToAssign = self.scope()
        varsToAssign.remove(var)
        x = findvals(varsToAssign, [(var, val)], cover_all_flights, could_cover_all)
        return x
"""
#New constraints for Q6: 
#Check whether the initial flight is valid
class validInitialFlight(Constraint):
    def __init__(self, name, scope, valid_values):#validInitialFlight([var1],[val1,val2,val3])
        Constraint.__init__(self,name, scope)
        self._name = "validInitialFlight_" + name
        self._scope = scope
        self._valid_values = valid_values
      

    def check(self):
        for var in self.scope():
            if var.isAssigned():
                if var.getValue() in self._valid_values:
                    return True
            else:
                return False
        return False


    def hasSupport(self, var, val):
        '''check if var=val has an extension to an assignment of the
           other variable in the constraint that satisfies the constraint
        '''
        if var not in self.scope():
            return True  #var=val has support on any constraint it does not participate in
        
        def satisfying_initial(l):
            for (variable, value) in l:
                if value in self._valid_values:
                    return True
            return False

        
        varsToAssign = self.scope()
        varsToAssign.remove(var)
        x = findvals(varsToAssign, [(var, val)], satisfying_initial, satisfying_initial)
        return x
"""     
"""
#Check maintenance
class satisfyMaintenance(Constraint):
    def __init__(self, name, scope, mtFlights, frequency):
        Constraint.__init__(self,name, scope)
        self._name = "satisfyMaintenance_" + name
        self._scope = scope
        self._mtFlights = mtFlights#maintenance depots at end of these flights
        self._frequency = frequency

      

    def check(self):
        count = 0
        frequency = self._frequency
        mtFlights = self._mtFlights
        for var in self.scope():
            if var.isAssigned():
                flight = var.getValue()
                if flight == 0:#0 indicates the end of the flight sequency
                    break
                if flight in mtFlights:
                    count = 0
                else:
                    count += 1
                if count == frequency:#Execeed the certain minimum frequency
                    return False
            else: 
                return True
        return True



    def hasSupport(self, var, val):
        '''check if var=val has an extension to an assignment of the
           other variable in the constraint that satisfies the constraint
        '''
        if var not in self.scope():
            return True  #var=val has support on any constraint it does not participate in

        def satisfy_current_assign(l):
            count = 0
            frequency = self._frequency
            mtFlights = self._mtFlights
            for (var, val) in l:
                if val == 0:
                    break
                if val in mtFlights:
                    count = 0
                else:
                    count += 1
                if count == frequency:
                    return False
            return True
        
        def partialAssign(l):
            return True

        
        varsToAssign = self.scope()
        varsToAssign.remove(var)
        x = findvals(varsToAssign, [(var, val)], satisfy_current_assign, partialAssign)
        return x
"""
"""
#Make sure flights that can follow each other
class flightCanConnect(Constraint):
    def __init__(self, name, scope, flight_can_connect):
        Constraint.__init__(self,name, scope)
        self._name = "connect_flight_" + name
        self._scope = scope
        self._flight_can_connect = flight_can_connect
    

    def check(self):
        count = 0
        scope = self._scope
        flight_can_connect = self._flight_can_connect
        for i in range(len(scope)-1):
            if scope[i].isAssigned():
                if scope[i+1].isAssigned():
                    start = scope[i].getValue()
                    end = scope[i+1].getValue()
                    connect_flight = (start, end)
                    if start == 0 and end != 0:
                        return False
                    elif connect_flight not in flight_can_connect and end != 0:
                        return False
                else:
                    return True
            else: 
                return True
        return True



    def hasSupport(self, var, val):
        '''check if var=val has an extension to an assignment of the
           other variable in the constraint that satisfies the constraint
        '''
        if var not in self.scope():
            return True  #var=val has support on any constraint it does not participate in

        def satisfy_current_assign(l):
            count = 0
            flight_can_connect = self._flight_can_connect
            
            for i in range(len(l)-1):
                (var1, val1) = l[i]
                (var2, val2) = l[i+1]
                if val1 == 0 and val2 != 0:
                    return False
                elif (val1, val2) not in flight_can_connect and val2 != 0:
                    return False
            return True

        
        def partialAssign(l):
            return True

        
        varsToAssign = self.scope()
        varsToAssign.remove(var)
        x = findvals(varsToAssign, [(var, val)], satisfy_current_assign, partialAssign)
        return x
"""

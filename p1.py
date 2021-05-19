import json
import sys

from graphviz import Source


squares = {}


def formGraph(finalNfa, re):

    string = """digraph G {
                fontsize = 30
                rankdir = LR
                edge [dir=forward]
             """
    # add re as a title:
    string += 'labelloc="t"'
    string += 'label="' + re + '"'
    states = []
    for t in finalNfa.transitions:
        if t.stateTo not in states:
            states.append(t.stateTo)
        if t.stateFrom not in states:
            states.append(t.stateFrom)

    states.sort()

    string += ("start [label=start, shape=none]"+'\n')
    string += ("start ->" 'S'+str(states[0])+'\n')

    string += ('S'+str(states[-1]) + '[shape=doublecircle]'+'\n')
    sqCount = 0
    changed = False
    for i in range(len(finalNfa.transitions)):
        changed = False
        if finalNfa.transitions[i].symbol == '_':
            sqString = str(squares[sqCount])
            # "Square"+str(sqCount+1)
            finalNfa.transitions[i].symbol = sqString
            # sqString -> error in render due to [ , ] , - , spcae , ..
            sqCount += 1
            changed = True
        string += ('S'+str(finalNfa.transitions[i].stateFrom) + "->" + 'S'+str(
            finalNfa.transitions[i].stateTo) + "[label="+str(finalNfa.transitions[i].symbol)+"]"+'\n')
        if changed:
            finalNfa.transitions[i].symbol = "["+sqString+"]"
    string += '}'
    s = Source(string, filename="NFA.gv", format="png")
    s.view()


class Transition:
    ###
    # Transition class for holding the states transitions
    ###
    stateFrom = None
    stateTo = None
    symbol = None

    def __init__(self, stateFrom, stateTo, symbol):
        self.stateFrom = stateFrom
        self.stateTo = stateTo
        self.symbol = symbol


class NFA:
    ###
    # NFA class; small assumption that we always have 1 finalState as even if there
    # is more than finalstate they all can go with ε to our final state:
    # Proof: all will have the same DFA -> implies that they are the same 😄
    ###
    states = []
    transitions = []
    finalState = 0

    def __init__(self, arg):
        self.states = 0
        self.transitions = []
        self.finalState = 0
        if type(arg) is int:
            self.setStateSize(arg)
        else:  # arg is char
            self.setStateSize(2)
            self.finalState = 1
            self.transitions.append(Transition(0, 1, arg))

    def setStateSize(self, size):
        self.states = size

    def show(self):
        sqCount = 0
        for t in self.transitions:
            changed = False
            if t.symbol == '_':
                changed = True
                t.symbol = squares[sqCount]
                sqCount += 1
            print("(" + str(t.stateFrom) + ", " +
                  t.symbol + ", " + str(t.stateTo) + ")")
            if changed:
                t.symbol = '_'

    # outputing for json file
    def jsonOutput(self):
        data = {}
        data['startingState'] = 'S0'
        sqCount = 0
        for t in self.transitions:
            if 'S'+str(t.stateFrom) not in data.keys():
                data['S'+str(t.stateFrom)] = {}
                data['S'+str(t.stateFrom)]['isTerminatingState'] = False
            if t.symbol == 'ε':
                t.symbol = 'Epsilon'  # i don't know why ε is written as unicode in json -> \u03b5 😠
            if t.symbol not in data['S'+str(t.stateFrom)].keys():
                data['S'+str(t.stateFrom)][t.symbol] = []
            if t.symbol == '_':
                t.symbol = squares[sqCount]
                sqCount += 1
            data['S'+str(t.stateFrom)][t.symbol].append('S'+str(t.stateTo))
            # terminating state
        data['S'+str(t.stateTo)] = {}
        data['S'+str(t.stateTo)]['isTerminatingState'] = True
        with open('nfa.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)


def star(nfa):
    ##  zero or more (*)   ##

    result = NFA(nfa.states+2)
    result.transitions.append(Transition(0, 1, 'ε'))
    # copy existing transition from nfa
    for t in nfa.transitions:
        result.transitions.append(Transition(
            t.stateFrom + 1, t.stateTo + 1, t.symbol))

    # append empty Transition from final nfa state to new final state
    result.transitions.append(Transition(
        nfa.states, nfa.states + 1, 'ε'))

    # Loop back from last state of nfa to initial state of result
    result.transitions.append(Transition(nfa.states, 1, 'ε'))

    # append empty Transition from new initial state to new final state
    result.transitions.append(Transition(0, nfa.states + 1, 'ε'))

    result.finalState = nfa.states + 1
    return result


def concate(nfa1, nfa2):
    ##  concatenation (.)   ##

    # remove second nfa initial state
    nfa2.states -= 1

    # append empty Transition from final nfa1 state
    # nfa1.transitions.append(Transition(
    #     nfa1.states-1, nfa1.states, 'ε'))

    # copy NFA second's transitions to first, and handles connecting them:
    for t in nfa2.transitions:
        nfa1.transitions.append(Transition(
            t.stateFrom + nfa1.states-1, t.stateTo + nfa1.states-1, t.symbol))

    # take second and combine to first after erasing inital second's state
    nfa1.states += nfa2.states

    nfa1.finalState = nfa1.states + nfa2.states - 2
    return nfa1


def union(nfa1, nfa2):
    ##  ORing (+ or |)   ##

    result = NFA(nfa1.states + nfa2.states + 2)

    # the branching of S0 of nfa1 to beginning of result nfa
    result.transitions.append(Transition(0, 1, 'ε'))
    result.finalState = nfa1.states + nfa2.states + 1

    # copy existing transisitons of nfa1
    for t in nfa1.transitions:
        result.transitions.append(Transition(
            t.stateFrom + 1, t.stateTo + 1, t.symbol))

    # transition from last nfa1 to final state
    result.transitions.append(Transition(
        nfa1.states, result.finalState, 'ε'))

    # the branching of result nfa(S0) to beginning of nfa2
    result.transitions.append(Transition(0, nfa1.states + 1, 'ε'))

    # copy existing transisitons of nfa2
    for t in nfa2.transitions:
        result.transitions.append(Transition(
            t.stateFrom + nfa1.states + 1, t.stateTo + nfa1.states + 1, t.symbol))

    # transition from last of nfa2 to final state
    result.transitions.append(Transition(
        nfa2.states + nfa1.states, result.finalState, 'ε'))

    return result


def regexOperator(c):
    return c == '(' or c == ')' or c == '*' or c == '|' or c == '+'


def validate(re):
    prevChar = None
    inBr = False
    prevNonPerences = False
    charCountInBr = 0
    count = 0
    if len(re) == 0 or re[0] == '*' or re[0] == '|' or re[0] == '+':
        print('Invalid RE!')
        exit(-1)
    for c in re:
        count += 1
        if c == '*' and prevNonPerences and charCountInBr == 1:
            print('Invalid RE!')
            exit(-1)
        if c == '*':
            prevNonPerences = True
        elif c != ')':
            prevNonPerences = False

        if inBr and not regexOperator(c):
            charCountInBr += 1

        if c == '(':
            inBr = True
        elif c == ')':
            inBr = False

        if c == '*' or c == '|' or c == '+':
            if prevChar == c:
                print('Invalid RE!')
                exit(-1)
        if prevChar == '|' or prevChar == '+':
            if (c == ')' or c == '(') and count == len(re):
                print('Invalid RE!')
                exit(-1)
        if (c == ')' or c == '*') and prevChar == '(':
            print('Invalid RE!')
            exit(-1)
        prevChar = c

    if prevChar == '|' or prevChar == '+' or prevChar == '(':
        print('Invalid RE!')
        exit(-1)


def dealWithSqBrackets(re):
    re_edit = ""
    inSqBr = False
    squareNo = 0
    for char in re:
        if char == '[':
            if inSqBr:
                print('Invalid RE! -> cant concatenate square brackets')
                exit(-1)
            inSqBr = True

        elif char == ']':
            squareNo += 1
            inSqBr = False
        elif inSqBr:
            if squareNo in squares:
                if char == '-' and squares[squareNo].isnumeric():
                    squares[squareNo] += str('.')
                elif char == '-':
                    squares[squareNo] += str('_')
                else:
                    squares[squareNo] += str(char)

            else:
                if char == '-':
                    squares[squareNo] = str('_')
                else:
                    squares[squareNo] = str(char)
                re_edit += '_'
        else:
            re_edit += char

    return re_edit


if len(sys.argv) > 1:
    re = sys.argv[1]
# re = "A[A-Za-z[dssd]]|[0-9[gffg]]*BC(F|D)"
else:
    re = input("Enter the RE:")
# re = "1(0|1)*1(0|1)*"
# re = "(abc)d"
re_old = re
re = dealWithSqBrackets(re)

operands = []
operators = []  # +/| . *
concStack = []
concFlag = False
parCount = 0

#####################################################################
####                  Logic and Validation                       ####
#####################################################################

validate(re)
index = 0
for char in re:
    index += 1
    if not regexOperator(char):  # alphabet or anything else
        operands.append(NFA(char))
        if concFlag:
            operators.append('.')
        else:
            concFlag = True
    else:
        if char == ')':
            concFlag = True
            # if index != len(re) and not regexOperator(re[index]):
            #     concFlag = True
            if parCount == 0:
                print('Invalid RE -> more ) than (')
                exit(-1)
            else:
                parCount -= 1

            while len(operators) != 0 and operators[-1] != '(':
                oper = operators.pop()
                if oper == '.':  # conc
                    nfa2 = operands.pop()
                    nfa1 = operands.pop()
                    operands.append(concate(nfa1, nfa2))
                elif oper == '|' or oper == '+':  # ORing
                    nfa2 = operands.pop()
                    if len(operators) != 0 and operators[-1] == '.':
                        concStack.append(operands.pop())

                        while len(operators) != 0 and operators[-1] == '.':
                            concStack.append(operands.pop())
                            operators.pop()

                        nfa1 = concate(concStack.pop(), concStack.pop())
                        while len(concStack) > 0:
                            nfa1 = concate(nfa1, concStack.pop())
                    else:
                        nfa1 = operands.pop()
                    operands.append(union(nfa1, nfa2))

            # remove last occuring (
            if '(' in operators:
                operators.pop()
        elif char == '*':
            operands.append(star(operands.pop()))
            concFlag = True
        elif char == '(':
            if index-2 >= 0 and (not regexOperator(re[index-2]) or re[index-2] == '*'):
                operators.append('.')
                concFlag = False
            operators.append(char)
            parCount += 1
        elif char == '|' or char == '+':
            operators.append(char)
            concFlag = False

while len(operators) > 0:
    if len(operands) == 0:
        print('Invalid RE!')
        exit(-1)
    oper = operators.pop()
    if oper == '.':  # conc
        nfa2 = operands.pop()
        nfa1 = operands.pop()
        operands.append(concate(nfa1, nfa2))
    elif oper == '|' or oper == '+':  # ORing
        if len(operands) == 0:
            print('Invalid RE!')
            exit(-1)
        nfa2 = operands.pop()
        if len(operators) != 0 and operators[-1] == '.':
            concStack.append(operands.pop())
            while len(operators) > 0 and operators[-1] == '.':
                concStack.append(operands.pop())
                operators.pop()

            nfa1 = concate(concStack.pop(), concStack.pop())
            while len(concStack) > 0:
                nfa1 = concate(nfa1, concStack.pop())
        else:
            if len(operands) == 0:
                print('Invalid RE!')
                exit(-1)
            nfa1 = operands.pop()
        operands.append(union(nfa1, nfa2))
if len(operands) == 0:
    print('Invalid RE!')
    exit(-1)

finalNfa = operands.pop()
finalNfa.show()

formGraph(finalNfa, re_old)

finalNfa.jsonOutput()

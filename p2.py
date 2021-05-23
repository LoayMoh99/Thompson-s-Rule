import json

with open('nfa.json') as f:
    data = json.load(f)


class Transition:
    ###
    # Transition class for holding the states transitions
    ###
    nodeFrom = None
    nodeTo = None
    symbol = None

    def __init__(self, stateFrom, stateTo, symbol):
        self.nodeFrom = stateFrom
        self.nodeTo = stateTo
        self.symbol = symbol


class Node:
    ###
    # Node class; as a grouping of states..
    ###
    startNode = False
    states = []
    finalNode = False
    name = None

    def __init__(self):
        self.startNode = False
        self.states = []
        self.finalNode = False
        self.name = None

    def add(self, s):
        self.states.append(s)
        for other in data[s]:
            if other == "isTerminatingState":  # for seeing if it is terminating or not
                self.finalNode = self.finalNode or data[s][other]
            if other == "Epsilon":
                for same in data[s][other]:
                    self.add(same)


class DFA:
    ###
    # DFA class; group of nodes connected together..
    ###
    nodes = []
    transitions = []

    def __init__(self):
        self.nodes = []
        self.transitions = []

    def checkExistenceNode(self, node):
        for n in self.nodes:
            if len(n.states) == len(node.states):
                n.states.sort()
                node.states.sort()
                if n.states == node.states:
                    node.name = n.name
                    node.finalNode = n.finalNode
                    node.startNode = n.startNode
                    return False  # dont add it as it exist
        return True

    def checkExistenceTransition(self, tr):
        for t in self.transitions:
            if tr.symbol == t.symbol:
                tr.nodeFrom.states.sort()
                t.nodeFrom.states.sort()
                tr.nodeTo.states.sort()
                t.nodeTo.states.sort()
                if tr.nodeFrom.states == t.nodeFrom.states and tr.nodeTo.states == t.nodeTo.states:
                    return False  # dont add it as it exist SAME
                if tr.nodeFrom.states == t.nodeFrom.states:  # same symbol and same nodeFrom ->integrate nodeTo
                    for st in tr.nodeTo.states:
                        t.nodeTo.states.append(st)
                    t.nodeTo.finalNode = tr.nodeTo.finalNode
                    t.nodeTo.startNode = tr.nodeTo.startNode
                    return False
        return True

    def update(self, node):
        if self.checkExistenceNode(node):
            node.name = 'N'+str(len(self.nodes))
            self.nodes.append(node)
            sortedNodeStates = sorted(node.states)
            for state in sortedNodeStates:
                # print(state)
                for input in data[state]:
                    if input != "Epsilon" and input != "isTerminatingState":
                        # print(input)
                        n = Node()
                        for newstate in data[state][input]:
                            n.add(newstate)

                        t = Transition(node, n, input)
                        if self.checkExistenceTransition(t):
                            self.transitions.append(t)
                        self.update(n)


dfa = DFA()
n = Node()
n.startNode = True
n.add(data["startingState"])
dfa.update(n)

# printing and outputing in json file:
for tr in dfa.transitions:
    print(tr.nodeFrom.name+': '+str(tr.nodeFrom.states) + " - " +
          str(tr.symbol) + " -> "+tr.nodeTo.name+': '+str(tr.nodeTo.states))

out = {}
for tr in dfa.transitions:
    if tr.nodeFrom.startNode:
        out['startingState'] = tr.nodeFrom.name
    if tr.nodeFrom.name not in out.keys():
        out[tr.nodeFrom.name] = {}
        out[tr.nodeFrom.name]['isTerminatingState'] = tr.nodeFrom.finalNode
    if tr.symbol not in out[tr.nodeFrom.name].keys():
        out[tr.nodeFrom.name][tr.symbol] = []
    out[tr.nodeFrom.name][tr.symbol].append(tr.nodeTo.name)
with open('dfa.json', 'w') as outfile:
    json.dump(out, outfile, indent=4)

import argparse
import re
import sys

class Grammar:
        def __init__(self):
                self.variables = []
                self.terminals = []
                self.rules = {}
                self.start_variable = ''

        def format(self, input):
                output = ''

                if (input == 'epsilon'):
                        return input

                for i in range(len(input)):
                        if i < len(input)-1 and input[i+1] != '\'':
                                output += input[i] + ' '
                        else:
                                output += input[i]

                return output

        def __repr__(self):
                s = ''
                keys = list(self.rules.keys())

                for i in range(len(keys)):
                        s += keys[i] + " : "
                        values = self.rules[keys[i]]
                        for j in range(len(values)):
                                s += self.format(values[j])
                                if j < len(values)-1:
                                        s+= ' | '
                        if i < len(keys)-1:
                                s+= '\n'

                return s
                                
def construct_grammar(rules_list):
        grammar = Grammar()

        for rule in rules_list:
                r = rule.split(" : ")
                variable = r[0]
                rhs = r[1].split(" | ")
                rhs = [e.split(" ") for e in rhs]
                grammar.rules[variable] = rhs

        grammar.variables = list(grammar.rules.keys())
        grammar.start_variable = grammar.variables[0]

        return grammar

def get_var_first(var, grammar):
        prods = grammar.rules[var]
        first = []

        for i in range(len(prods)):
                j = 0

                if prods[i] == ["epsilon"]:
                        first.append("epsilon")
                else:         
                        prefix = prods[i][0]

                        if prefix not in grammar.variables:
                                first.append(prefix)

                        else:
                                if (prefix == var and ['epsilon'] in prods) or prefix != var:
                                        while prefix == var:
                                                j += 1
                                                if j<len(prods[i]):
                                                        prefix = prods[i][j]
                                                else:
                                                        break

                                        if j<len(prods[i]):
                                                if prefix in grammar.variables:
                                                        prefix_first = get_var_first(prefix, grammar)

                                                        while "epsilon" in prefix_first:
                                                                prefix_first.remove("epsilon")
                                                                j += 1
                                                                if j >= len(prods[i]):
                                                                        prefix_first.append("epsilon")
                                                                        break
                                                                else:
                                                                        next_prefix = prods[i][j]

                                                                        if next_prefix not in grammar.variables:
                                                                                prefix_first.append(next_prefix)
                                                                        else:
                                                                                if (next_prefix == var and ['epsilon'] in prods) or next_prefix != var:
                                                                                        while next_prefix == var:
                                                                                                j += 1
                                                                                                if j<len(prods[i]):
                                                                                                        next_prefix = prods[i][j]
                                                                                                else:
                                                                                                        break

                                                                                        if j<len(prods[i]):
                                                                                                if next_prefix in grammar.variables:
                                                                                                        next_prefix_first = get_var_first(next_prefix, grammar)
                                                                                                        prefix_first.extend(next_prefix_first)
                                                                                                else:
                                                                                                        prefix_first.extend(next_prefix)

                                                        first.extend(prefix_first)
                                                else:
                                                        first.extend(prefix)

        first = list(dict.fromkeys(first))
        return first

def compute_first(grammar):
        varss = grammar.variables
        first = {}

        for var in varss:
                first[var] = get_var_first(var, grammar)

        return first

def get_var_follow(var, grammar, first):
        varss = grammar.variables
        if var == grammar.start_variable:
                follow = ['$']
        else:
                follow = []
        for v in varss:
                for prod in grammar.rules[v]:
                        for i in range(len(prod)):
                                if prod[i] == var:
                                        if i == len(prod)-1:
                                                if v != var:
                                                        follow.extend(get_var_follow(v, grammar, first))
                                        else:
                                                nextt = prod[i+1]
                                                if nextt not in grammar.variables:
                                                        follow.append(nextt)
                                                else:
                                                        nextt_first = []
                                                        nextt_first.extend(first[nextt])
                                                        if "epsilon" not in nextt_first:
                                                                follow.extend(nextt_first)
                                                        else:
                                                                j = i+1

                                                                while  "epsilon" in nextt_first:
                                                                        nextt_first.remove("epsilon")
                                                                        if j == len(prod)-1:
                                                                                if v != var:
                                                                                        nextt_first.extend(get_var_follow(v, grammar, first))
                                                                                break
                                                                        j = j+1
                                                                        next_next = prod[j]
                                                                        if next_next not in grammar.variables:
                                                                                nextt_first.append(next_next)
                                                                        else:
                                                                                nextt_first.extend(first[next_next])

                                                                follow.extend(nextt_first)

        follow = list(dict.fromkeys(follow))
        return follow

def compute_follow(grammar, first):
        varss = grammar.variables
        follow = {}

        for var in varss:
                follow[var] = get_var_follow(var, grammar, first)

        return follow

def format_first_follow(varss, first, follow):
        s = ''
        for var in varss:
                s += var + " : "
                for f in first[var]:
                        s += f + ' '
                s += ': '
                for f in follow[var]:
                        s += f + ' '
                s += '\n'
        return s

if __name__ == '__main__':
        parser = argparse.ArgumentParser(add_help=True, description='Sample Commandline')
        parser.add_argument('--grammar_file', action="store", help="path of file to take as grammar", nargs="?", metavar="grammar_file")
        args = parser.parse_args()
        with open(args.grammar_file, "r", encoding='utf8') as file:
                grammar_file = file.read()

        rules_list = grammar_file.split("\n")
        rules_list = list(filter(lambda e: e != '' and not re.match(r'^(\s)+$', e), rules_list))                 
        grammar = construct_grammar(rules_list)
        first = compute_first(grammar)
        follow = compute_follow(grammar, first)
        first_follow = format_first_follow(grammar.variables, first, follow)

        output = open("task_5_1_result.txt", "w")
        output.write(first_follow)                
        output.close()
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

def left_recursion_elimination(grammar):
        keys = list(grammar.rules.keys())
        new_rules = {}

        for i in range(len(grammar.rules)):
                for j in range(0, i):
                        j_rule_lhs = keys[j]
                        new_rhs = []
                        for r in grammar.rules[keys[i]]:
                                if r[0] == j_rule_lhs:
                                        r_rhs = grammar.rules[j_rule_lhs]
                                        for e in r_rhs:
                                                new_rhs.append(e + r[1:])
                                else:
                                       new_rhs.append(r) 
                        grammar.rules[keys[i]] = new_rhs
                #immediate left recursion
                alphas = []
                betas = []
                for r in grammar.rules[keys[i]]:
                        if keys[i] == r[0]:
                                alphas.append(r[1:])
                        else:
                                betas.append(r)
                if (len(alphas) != 0):
                        grammar.rules[keys[i]] = []
                        for beta in betas:
                                grammar.rules[keys[i]].append(beta+[keys[i]+"'"])
                        new_rules[keys[i]+"'"] = []
                        for alpha in alphas:
                                new_rules[keys[i]+"'"].append(alpha+[keys[i]+"'"])
                        new_rules[keys[i]+"'"].append(["epsilon"])

        grammar.rules.update(new_rules)

        return grammar
                                
def construct_grammar(rules_list):
        grammar = Grammar()

        for rule in rules_list:
                r = rule.split(" : ")
                variable = r[0]
                rhs = r[1].split(" | ")
                rhs = [e.split(" ") for e in rhs]
                grammar.rules[variable] = rhs

        return grammar

if __name__ == '__main__':
        parser = argparse.ArgumentParser(add_help=True, description='Sample Commandline')
        parser.add_argument('--grammar_file', action="store", help="path of file to take as grammar", nargs="?", metavar="grammar_file")
        args = parser.parse_args()
        with open(args.grammar_file, "r", encoding='utf8') as file:
                grammar_file = file.read()

        rules_list = grammar_file.split("\n")
        rules_list = list(filter(lambda e: e != '' and not re.match(r'^(\s)+$', e), rules_list))
        grammar = construct_grammar(rules_list)
        grammar = left_recursion_elimination(grammar)

        output = open("task_4_1_result.txt", "w")
        output.write(str(grammar))                
        output.close()
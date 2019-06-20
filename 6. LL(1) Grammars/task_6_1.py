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
                                
def construct_grammar_and_ff(rules_list):
        grammar = Grammar()
        first = {}
        follow = {}

        for rule in rules_list:
                r = rule.split(" : ")
                variable = r[0]
                first[variable] = r[2].split(" ")
                follow[variable] = r[3].split(" ")                
                rhs = r[1].split(" | ")
                rhs = [e.split(" ") for e in rhs]
                grammar.rules[variable] = rhs

        grammar.variables = list(grammar.rules.keys())
        grammar.start_variable = grammar.variables[0]

        for k in list(grammar.rules.keys()):
                prods = grammar.rules[k]

                for p in prods:
                        for i in p:
                                if i != ' ' and i not in grammar.variables and i != 'epsilon':
                                        grammar.terminals.append(i)

        return grammar, first, follow

def construct_ll1_table(grammar, first, follow):
        ll1_table = {}

        for v in grammar.variables:
                for t in grammar.terminals + ['$']:
                        ll1_table[(v, t)] = []

        for v in grammar.variables:
                for t in grammar.terminals + ['$']:
                        prods = grammar.rules[v]
                        for p in prods:
                                if p != ['epsilon']:
                                        prefix = p[0]
                                        if prefix in grammar.terminals:
                                                if t == prefix:
                                                        if p not in ll1_table[(v, t)]:
                                                                ll1_table[(v, t)].append(p)
                                        else:
                                                prefix_first = first[prefix]
                                                if t in prefix_first:
                                                        if p not in ll1_table[(v, t)]:
                                                                ll1_table[(v, t)].append(p)
                                else:
                                        v_follow = follow[v]
                                        for f in v_follow:
                                                if ['epsilon'] not in ll1_table[(v, f)]:
                                                        ll1_table[(v, f)].append(['epsilon'])

        return ll1_table

def format_ll1_table(ll1_table):
        s = ''
        keys = list(ll1_table.keys())

        for k in range(len(keys)):
                s += keys[k][0] + ' : ' + keys[k][1]  + ' : '
                prods = ll1_table[keys[k]]
                if len(prods) > 1:
                        s = 'invalid LL(1) grammar'
                        return s
                else:
                        for p in prods:
                                for i in range(len(p)):
                                        s += p[i]
                                        if i < len(p) - 1:
                                                s += ' '
                if k < len(keys) - 1:
                        s += '\n'
                                                       
        return s

def check_input(input, grammar, ll1_table):
        input = input + ['$']
        stack = [grammar.start_variable, '$']
        p = 0

        while p < len(input):
                symbol = input[p]
                top = stack[0]

                if symbol not in grammar.terminals + ['$']:
                        return 'no'

                if symbol == top:
                        del stack[0]
                        p += 1
                else:
                        if top not in grammar.variables:
                                return 'no'

                        prod = ll1_table[(top, symbol)]

                        if prod == []:
                                return 'no'

                        del stack[0]

                        prod = prod[0]
                        if prod != ['epsilon']:
                                i = len(prod) - 1
                                while i > -1:
                                        stack.insert(0, prod[i])
                                        i -= 1
        
        if stack != []:
                return 'no'
                        
        return 'yes'
                
if __name__ == '__main__':
        parser = argparse.ArgumentParser(add_help=True, description='Sample Commandline')
        parser.add_argument('--grammar', action="store", help="path of file to take as input to read gramma", nargs="?", metavar="grammar_file")
        parser.add_argument('--input', action="store", help="path of file to take as input to test strings on LL table", nargs="?", metavar="input_file")
        args = parser.parse_args()

        with open(args.grammar, "r", encoding='utf8') as file:
                grammar = file.read()

        with open(args.input, "r", encoding='utf8') as file:
                input = file.read()

        rules_list = grammar.split("\n") 
        rules_list = list(filter(lambda e: e != '' and not re.match(r'^(\s)+$', e), rules_list))  

        grammar, first, follow = construct_grammar_and_ff(rules_list)

        ll1_table = construct_ll1_table(grammar, first, follow)
        ll1_table_formatted = format_ll1_table(ll1_table)

        output1 = open("task_6_1_result.txt", "w")
        output1.write(ll1_table_formatted)                
        output1.close()

        if ll1_table_formatted != 'invalid LL(1) grammar':
                result = check_input(input.split(" "), grammar, ll1_table)
                output2 = open("task_6_2_result.txt", "w")
                output2.write(result)                
                output2.close()
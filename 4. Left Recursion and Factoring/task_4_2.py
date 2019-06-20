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
                                if values[j] != []:
                                        s += self.format(values[j])
                                else:
                                        s+= "epsilon"
                                if j < len(values)-1:
                                        s+= ' | '
                        if i < len(keys)-1:
                                s+= '\n'

                return s

def get_prefix_dict(l):
    dic = {}

    for i in range(len(l)):
        if l[i] != [] and l[i][0] in dic.keys():
            if l[i][1:] not in dic[l[i][0]]:
                dic[l[i][0]].append(l[i][1:])
        else:
                if (l[i]!=[]):
                        dic[l[i][0]] = [l[i][1:]]
            
        for j in range(i+1, len(l)):
            if  l[i] != [] and l[j] != [] and l[i][0] == l[j][0]:
                if l[j][1:] not in dic[l[i][0]]:
                    dic[l[i][0]].append(l[j][1:])
                
    return dic

def left_factor_new_rule(var, productions, dash_counter):
        new_rule = {}
        new_rules = {}
        prefix_dict = get_prefix_dict(productions)
        prefix_present = [len(prefix_dict[k]) != 1 for k in prefix_dict.keys()]
        
        if(sum(prefix_present) != 0):
                betas = []
                new_productions = []
                #dash_counter = 1
                if [] in productions:
                        betas.append([])
                for key in prefix_dict.keys():
                        if len(prefix_dict[key]) == 1:
                                betas.append([key]+prefix_dict[key][0])
                        else:
                                new_rules[var+'\''*dash_counter] = prefix_dict[key]
                                new_productions.append([key]+[var+'\''*dash_counter])
                                dash_counter += 1

                new_productions.extend(betas)
                new_rule[var] = new_productions

                for k1 in new_rules.keys():
                        updated_rules, dash_counter = left_factor_new_rule(k1, new_rules[k1], dash_counter)
                        new_rule.update(updated_rules)
                
                return new_rule, dash_counter
        else:
                return {var:productions}, dash_counter

def left_factor(grammar):
        keys = list(grammar.rules.keys())
        new_rules = {}

        for i in range(len(keys)):
                productions = grammar.rules[keys[i]]
                prefix_dict = get_prefix_dict(productions)
                betas = []
                new_productions = []
                dash_counter = 1

                if [] in productions:
                        betas.append([])

                for key in prefix_dict.keys():
                        if len(prefix_dict[key]) == 1:
                                betas.append([key]+prefix_dict[key][0])
                        else:
                                new_productions.append([key]+[keys[i]+'\''*dash_counter])
                                new_rule_fac, dash_counter = left_factor_new_rule(keys[i]+'\''*dash_counter, prefix_dict[key], dash_counter)
                                new_rules.update(new_rule_fac)
                                dash_counter += 1

                new_productions.extend(betas)
                grammar.rules[keys[i]] = new_productions

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
        grammar = left_factor(grammar)

        output = open("task_4_2_result.txt", "w")
        output.write(str(grammar))                
        output.close()
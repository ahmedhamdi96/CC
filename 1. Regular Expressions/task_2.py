import argparse
import os
import re
import copy

precedence_dist = {
  '(': 1,
  '|': 2, #union
  '.': 3, #concatenate
  '?': 4, #zero or one
  '*': 5, #zero or more
  '+': 6  #one or more
}

def assign_concat_op(regex):
        #alphabet = list(set(re.sub(r'[^a-zA-Z0-9\s]+', '', regex)))
        alphabet = list(set(re.sub(r'(\(|\||\.|\?|\*|\+|\))', '', regex)))
        regex_concat = ''
        for i in range(len(regex)):
                if i+1<len(regex):
                        alpha_i = regex[i] in alphabet
                        close_bracket_i = regex[i] == ')'
                        single_char_op = regex[i] in ['?', '*', '+']

                        alpha_i1 = regex[i+1] in alphabet
                        open_bracket_i1 = regex[i+1] == '('

                        if((alpha_i or close_bracket_i or single_char_op) and (alpha_i1 or open_bracket_i1)):
                                regex_concat += regex[i] + '.'
                        else:
                                regex_concat += regex[i]
                else:
                        regex_concat += regex[i]

        return regex_concat

def infix_postfix(infix):
        infix = assign_concat_op(infix)
        #alphabet = list(set(re.sub(r'[^a-zA-Z0-9\s]+', '', infix)))
        alphabet = list(set(re.sub(r'(\(|\||\.|\?|\*|\+|\))', '', infix)))
        postfix = ''
        stack = []

        for i in infix:
                if i == '(':
                        stack.append(i)
                else:
                        if i == ')':
                                while(len(stack)>0 and stack[len(stack)-1] != '('):
                                        #pop and append till '('
                                        postfix = postfix + stack[-1]
                                        del stack[-1]
                                del stack[-1] #pop '('
                        else:
                                if (i in alphabet):
                                        #append
                                        postfix = postfix + i
                                else:
                                        while(len(stack)>0):
                                                top = stack[-1]

                                                top_precedence = precedence_dist[top]
                                                i_precedence = precedence_dist[i]

                                                if(top_precedence >= i_precedence):
                                                        #pop and append till lower precedence
                                                        postfix = postfix + stack[-1]
                                                        del stack[-1]
                                                else:
                                                        break
                                        stack.append(i) #push new operator

        while(len(stack) > 0):
                #empty stack
                postfix = postfix + stack[-1]                              
                del stack[-1]

        return postfix

class NFA:
        def __init__(self, symbol):
                self.symbol = symbol
                self.states = ['q0', 'q1']
                self.alphabet = [symbol]
                self.start_state = 'q0'
                self.final_states = ['q1']
                self.transitions = [['q0', symbol, 'q1']]

        def __repr__(self):
                s = ''

                for i in range(len(self.states)):
                        if i<len(self.states)-1:
                                s += self.states[i] + ', '
                        else:
                                s += self.states[i] + '\n'

                self.alphabet.sort()
                for i in range(len(self.alphabet)):
                        if i<len(self.alphabet)-1:
                                s += self.alphabet[i] + ', '
                        else:
                                s += self.alphabet[i] + '\n'

                s += self.start_state +'\n'

                for i in range(len(self.final_states)):
                        if i<len(self.final_states)-1:
                                s += self.final_states[i] + ', '
                        else:
                                s += self.final_states[i] + '\n'

                for i in range(len(self.transitions)):
                        s += '('
                        for j in range(len(self.transitions[i])):
                                if j<len(self.transitions[i])-1:
                                        s += self.transitions[i][j] + ', '
                                else:
                                        s += "[" +self.transitions[i][j] + "]"
                        if i<len(self.transitions)-1:
                                s += '), '
                        else:
                                s += ')'

                return s

def concatenate_nfas(nfa1, nfa2):
        #NFA1
        #states -> no change
        #alphabet -> no change
        #start_state -> no change
        #transitions -> no change
        #final_states -> no change

        #NFA2
        #states
        nfa1_connective_len = len(nfa1.states) - 1
        for i in range(len(nfa2.states)):
                nfa2.states[i] = 'q'+str(int(nfa2.states[i][1:])+nfa1_connective_len)
        del nfa2.states[0]
        #alphabet -> no change
        #start_state
        nfa2.start_state = 'q'+str(int(nfa2.start_state[1:])+nfa1_connective_len)
        #final_states
        for i in range(len(nfa2.final_states)):
                nfa2.final_states[i] = 'q'+str(int(nfa2.final_states[i][1:])+nfa1_connective_len)
        #transitions
        for i in range(len(nfa2.transitions)):
                nfa2.transitions[i][0] = 'q'+str(int(nfa2.transitions[i][0][1:])+nfa1_connective_len)
                nfa2.transitions[i][2] = 'q'+str(int(nfa2.transitions[i][2][1:])+nfa1_connective_len)

        #Merging
        concatenated_nfa = NFA(nfa1.symbol+nfa2.symbol+'.')
        #states
        concatenated_nfa.states = nfa1.states + nfa2.states
        #alphabet
        concatenated_nfa.alphabet = list(set(nfa1.alphabet + nfa2.alphabet))
        #start_state
        concatenated_nfa.start_state = nfa1.start_state
        #final_states
        concatenated_nfa.final_states = nfa2.final_states
        #transitions
        concatenated_nfa.transitions = nfa1.transitions + nfa2.transitions

        return concatenated_nfa

def union_nfas(nfa1, nfa2):
        union_start_state = 'q0'
        union_final_state = 'q'+str(len(nfa1.states)+len(nfa2.states)+1)

        #NFA1
        #states
        for i in range(len(nfa1.states)):
                nfa1.states[i] = 'q'+str(int(nfa1.states[i][1:])+1)
        #alphabet
        nfa1.alphabet.append(' ')
        #start_state
        nfa1.start_state = 'q'+str(int(nfa1.start_state[1:])+1)
        #transitions(1)
        for i in range(len(nfa1.transitions)):
                nfa1.transitions[i][0] = 'q'+str(int(nfa1.transitions[i][0][1:])+1)
                nfa1.transitions[i][2] = 'q'+str(int(nfa1.transitions[i][2][1:])+1)
        #final_states and transitions(2)
        for i in range(len(nfa1.final_states)):
                nfa1.final_states[i] = 'q'+str(int(nfa1.final_states[i][1:])+1)
                nfa1.transitions.append([nfa1.final_states[i],' ', union_final_state])
        #transitions(3)
        nfa1.transitions.insert(0, [union_start_state,' ', nfa1.start_state])

        #NFA2
        #states
        nfa1_connective_len = len(nfa1.states) + 1
        for i in range(len(nfa2.states)):
                nfa2.states[i] = 'q'+str(int(nfa2.states[i][1:])+nfa1_connective_len)
        #alphabet
        nfa2.alphabet.append(' ')
        #start_state
        nfa2.start_state = 'q'+str(int(nfa2.start_state[1:])+nfa1_connective_len)
        #transitions(1)
        for i in range(len(nfa2.transitions)):
                nfa2.transitions[i][0] = 'q'+str(int(nfa2.transitions[i][0][1:])+nfa1_connective_len)
                nfa2.transitions[i][2] = 'q'+str(int(nfa2.transitions[i][2][1:])+nfa1_connective_len)
        #final_states and transitions(2)
        for i in range(len(nfa2.final_states)):
                nfa2.final_states[i] = 'q'+str(int(nfa2.final_states[i][1:])+nfa1_connective_len)
                nfa2.transitions.append([nfa2.final_states[i],' ', union_final_state])
        #transitions(3)
        nfa2.transitions.insert(0, [union_start_state,' ', nfa2.start_state])
                
        #Merging
        unioned_nfa = NFA(nfa1.symbol+nfa2.symbol+'|')
        #states
        unioned_nfa.states = [union_start_state] + nfa1.states + nfa2.states + [union_final_state]
        #alphabet
        unioned_nfa.alphabet = list(set(nfa1.alphabet + nfa2.alphabet))
        #start_state
        unioned_nfa.start_state = union_start_state
        #final_states
        unioned_nfa.final_states = [union_final_state]
        #transitions
        unioned_nfa.transitions = nfa1.transitions + nfa2.transitions

        return unioned_nfa

def star_nfa(nfa):
        star_start_state = 'q0'
        star_final_state = 'q'+str(len(nfa.states)+1)

        #symbol
        nfa.symbol = (nfa.symbol+"*")
        #states(1)
        for i in range(len(nfa.states)):
                nfa.states[i] = 'q'+str(int(nfa.states[i][1:])+1)
        #alphabet
        if (' ' not in nfa.alphabet):
                nfa.alphabet.append(' ')
        #start_state(1)
        nfa.start_state = 'q'+str(int(nfa.start_state[1:])+1)
        #transitions(1)
        for i in range(len(nfa.transitions)):
                nfa.transitions[i][0] = 'q'+str(int(nfa.transitions[i][0][1:])+1)
                nfa.transitions[i][2] = 'q'+str(int(nfa.transitions[i][2][1:])+1)
        #final_states(2) and transitions(2)
        for i in range(len(nfa.final_states)):
                nfa.final_states[i] = 'q'+str(int(nfa.final_states[i][1:])+1)
                nfa.transitions.append([nfa.final_states[i],' ', nfa.start_state])
                nfa.transitions.append([nfa.final_states[i],' ', star_final_state])
        #transitions(3)
        nfa.transitions.insert(0, [star_start_state,' ', nfa.start_state])
        #start_state(2)
        nfa.start_state = star_start_state
        #final_states(2)
        nfa.final_states = [star_final_state]
        #states(2)
        nfa.states = [star_start_state] + nfa.states + [star_final_state]
        #transitions(4)
        nfa.transitions.insert(0, [star_start_state,' ', star_final_state])

        return nfa

def evaluate_operator(nfa1, nfa2, op):
        if (op == '.'):
                return concatenate_nfas(nfa1, nfa2)
        if (op == '|'):
                return union_nfas(nfa1, nfa2)

def evaluate_unary_operator(nfa, op):
        if (op == '*'):
                return star_nfa(nfa)
        if (op == '+'):
                nfa_copy = copy.deepcopy(nfa) 
                return concatenate_nfas(nfa_copy, star_nfa(nfa))
        if (op == '?'):
                return union_nfas(nfa, NFA(' '))

def postfix_nfa(postfix):
        #alphabet = list(set(re.sub(r'[^a-zA-Z0-9\s]+', '', postfix)))
        alphabet = list(set(re.sub(r'(\(|\||\.|\?|\*|\+|\))', '', postfix)))
        stack = []
        one_symbol_ops = ['?', '*', '+']

        for i in postfix:
                if (i in alphabet):
                        stack.append(NFA(i))
                else:
                        if (i in one_symbol_ops):
                                nfa = stack[-1]
                                del stack[-1]
                                result_nfa = evaluate_unary_operator(nfa, i)
                                stack.append(result_nfa)
                        else:
                                nfa2 = stack[-1]
                                del stack[-1]
                                nfa1 = stack[-1]
                                del stack[-1]
                                result_nfa = evaluate_operator(nfa1, nfa2, i)
                                stack.append(result_nfa)

        return stack[-1]

def regex_nfa(regex):
        postfix = infix_postfix(regex)
        nfa = postfix_nfa(postfix)
        return nfa

if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=True, description='Sample Commandline')                 
    parser.add_argument('--file', action="store", help="path of file to take as input", nargs="?",
                        metavar="file")                
    args = parser.parse_args()

    with open(args.file, "r", encoding='utf8') as file:
        input = file.read()
        matches = input.split("\n")
        matches = list(filter(lambda e: e != '' and not re.match(r'^(\s)+$', e), matches))

        output = open("task_2_result.txt", "w")
        for i in range(len(matches)):
                matches[i] = re.sub(' ', '', matches[i])
                matches[i] = re.sub('ε', ' ', matches[i])
                nfa = str(regex_nfa(matches[i]))
                nfa = nfa.replace(",  ,", ", ,")
                output.write(nfa)
                if (i<len(matches)-1):
                        output.write("\n\n")
        
        output.close()
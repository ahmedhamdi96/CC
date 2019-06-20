import argparse
import re
import sys

class NFA:
        def __init__(self, regex):
                self.regex = regex
                self.states = []
                self.alphabet = []
                self.start_state = ''
                self.final_states = []
                self.transitions = []
                self.epsilon_closure = {}

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
                                        s += self.transitions[i][j]
                        if i<len(self.transitions)-1:
                                s += '), '
                        else:
                                s += ')'

                return s

class DFA:
        def __init__(self, regex):
                self.regex = regex
                self.states = []
                self.alphabet = []
                self.start_state = ''
                self.final_states = []
                self.transitions = []

        def __repr__(self):
                s = ''

                for i in range(len(self.states)):
                        if i<len(self.states)-1:
                                s += str(self.states[i]) + ', '
                        else:
                                s += str(self.states[i]) + '\n'
                
                if len(self.alphabet) == 0:
                        s+='\n'
                else:
                        self.alphabet.sort()
                        for i in range(len(self.alphabet)):
                                if i<len(self.alphabet)-1:
                                        s += self.alphabet[i] + ', '
                                else:
                                        s += self.alphabet[i] + '\n'

                s += self.start_state +'\n'

                for i in range(len(self.final_states)):
                        if i<len(self.final_states)-1:
                                s += str(self.final_states[i]) + ', '
                        else:
                                s += str(self.final_states[i]) + '\n'

                for i in range(len(self.transitions)):
                        s += '('
                        for j in range(len(self.transitions[i])):
                                if j<len(self.transitions[i])-1:
                                        s += str(self.transitions[i][j]) + ', '
                                else:
                                        s += str(self.transitions[i][j])
                        if i<len(self.transitions)-1:
                                s += '), '
                        else:
                                s += ')'

                return s

def epsilon_closure(nfa, state):
        result = [state]

        for transition in nfa.transitions:
                if (transition[0] == state and transition[1] == ' '):
                        result.extend(epsilon_closure(nfa, transition[2]))

        result = list(set(result))
        result.sort()
        return result

def epsilon_closure_iter(nfa, state):
        result = []

        visited_states = {}
        for s in nfa.states:
                visited_states[s] = False

        to_be_visited = [state]

        while len(to_be_visited) != 0:
                s = to_be_visited[0]
                if (not visited_states[s]):
                        for transition in nfa.transitions:
                                if (transition[0] == s and transition[1] == ' '):
                                        to_be_visited.append(transition[2])
                        visited_states[s] = True          
                        result.append(s)
                del to_be_visited[0]

        result = list(set(result))
        result.sort()
        return result

def get_transitions(nfa, states, symbol):
        result = []
        for state in states:
                for transition in nfa.transitions:
                        if (transition[0] == state and transition[1] == symbol):
                                result.extend(nfa.epsilon_closure[transition[2]])

        result = list(set(result))
        result.sort()
        return result

def nfa_dfa(nfa):
        dfa = DFA(nfa.regex)

        if ' ' in nfa.alphabet:
                nfa.alphabet.remove(' ')
                dfa.alphabet = nfa.alphabet
        else:
                dfa.alphabet = nfa.alphabet

        dfa_start_state = nfa.epsilon_closure[nfa.start_state]
        states_to_visit = [dfa_start_state]
        dfa.start_state = str(dfa_start_state)

        visited_states = []

        while(len(states_to_visit) != 0):
                states = states_to_visit[0]
                if(states not in visited_states):
                        dfa.states.append(states)
                        for symbol in dfa.alphabet:
                                destination_states = get_transitions(nfa, states, symbol)
                                dfa.transitions.append([states, symbol, destination_states])
                                if (destination_states not in states_to_visit):
                                        states_to_visit.append(destination_states)
                        del states_to_visit[0]
                        visited_states.append(states)
                else:
                        del states_to_visit[0]

        for state in dfa.states:
                for final_state in nfa.final_states:
                        if final_state in state:
                                dfa.final_states.append(state)
                                break

        #renaming
        dfa_renamed = DFA(dfa.regex)
        dfa_renamed.alphabet = dfa.alphabet
        state_char_counter = ord('A')
        renamings_dict = {dfa.start_state : chr(state_char_counter)}
        state_char_counter += 1
        dfa_renamed.start_state = renamings_dict[dfa.start_state]

        for state in dfa.states:
                if state!=[] and str(state) not in list(renamings_dict.keys()):
                        renamings_dict[str(state)] = chr(state_char_counter)
                        state_char_counter += 1
                else:
                        if state == []:
                                renamings_dict[str(state)] = "DEAD"

        
        dfa_renamed.states = list(renamings_dict.values())

        for final_state in dfa.final_states:
                dfa_renamed.final_states.append(renamings_dict[str(final_state)])

        for transition in dfa.transitions:
                dfa_renamed.transitions.append([renamings_dict[str(transition[0])], transition[1], renamings_dict[str(transition[2])]])

        return dfa_renamed

def construct_nfa(nfa_list):
        nfa = NFA("")
        nfa.states = re.findall(r'q[0-9]+', nfa_list[0])
        nfa.alphabet =  re.split(r',', nfa_list[1])
        nfa.start_state = nfa_list[2]
        nfa.final_states = re.findall(r'q[0-9]+', nfa_list[3])
        nfa.transitions = re.split(r'(?<=\))\,', nfa_list[4])
        for i in range(len(nfa.transitions)):
                nfa.transitions[i] = nfa.transitions[i].replace(',,', ', ,')
                nfa.transitions[i] = nfa.transitions[i].replace('(', '')
                nfa.transitions[i] = nfa.transitions[i].replace(')', '')
                nfa.transitions[i] = nfa.transitions[i].split(',')
        for state in nfa.states:
                nfa.epsilon_closure[state] = epsilon_closure_iter(nfa, state)

        return nfa


if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=True, description='Sample Commandline')                 
    parser.add_argument('--file', action="store", help="path of file to take as input", nargs="?",
                        metavar="file")                
    args = parser.parse_args()

    with open(args.file, "r", encoding='utf8') as file:
        input = file.read()
        matches = input.split("\n\n")
        matches = list(filter(lambda e: e != '' and not re.match(r'^(\s)+$', e), matches))

        output = open("task_2_2_result.txt", "w")
        for i in range(len(matches)):
                matches[i] = matches[i].replace(", ", ",")
                nfa = construct_nfa(matches[i].split("\n"))
                dfa = nfa_dfa(nfa)
                output.write(str(dfa))
                if (i<len(matches)-1):
                        output.write("\n\n")
                
                                
        output.close()
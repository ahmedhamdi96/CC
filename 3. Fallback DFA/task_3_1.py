import argparse
import re
import sys

class DFA:
        def __init__(self, regex):
                self.regex = regex
                self.states = []
                self.alphabet = []
                self.start_state = ''
                self.final_states = []
                self.transitions = []
                self.labels = {}
                self.actions = {}

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
                                s += ')\n'

                s += str(self.labels)+"\n"

                s += str(self.actions)+"\n"

                return s

def construct_dfa(dfa_list):
        dfa = DFA("")
        dfa.states = re.split(r',', dfa_list[0])
        dfa.alphabet =  re.split(r',', dfa_list[1])
        dfa.start_state = dfa_list[2]
        dfa.final_states = re.split(r',', dfa_list[3])

        dfa.transitions = re.split(r'(?<=\))\,', dfa_list[4])
        for i in range(len(dfa.transitions)):
                dfa.transitions[i] = dfa.transitions[i].replace('(', '')
                dfa.transitions[i] = dfa.transitions[i].replace(')', '')
                dfa.transitions[i] = dfa.transitions[i].split(',')

        labels = re.split(r'(?<=\))\,', dfa_list[5])
        for i in range(len(labels)):
                labels[i] = labels[i].replace('(', '')
                labels[i] = labels[i].replace(')', '')
                labels[i] = labels[i].split(',')

        actions = re.split(r'(?<=\))\,', dfa_list[6])
        for i in range(len(actions)):
                actions[i] = actions[i].replace('(', '')
                actions[i] = actions[i].replace(')', '')
                actions[i] = actions[i].split(',')

        labels_dict = {}
        for label in labels:
                labels_dict[label[0]] = label[1]
        dfa.labels = labels_dict

        actions_dict = {}
        for action in actions:
                actions_dict[action[0]] = action[1]
        dfa.actions = actions_dict

        return dfa

def run_fallback_dfa(dfa, input_str):
        stack = [dfa.start_state]
        l = 0
        r = 0
        output = ''
        last_state = stack[0]
        last_state_flag = True

        while(True):
                input_str_symbol = input_str[l]
                destination_state = ''
                for transition in dfa.transitions:
                        if input_str_symbol == transition[1] and stack[0] == transition[0]:
                                destination_state = transition[2]
                                break
                stack.insert(0, destination_state)
                l += 1

                if(l == len(input_str)):
                        if stack[0] in dfa.final_states:
                                label = dfa.labels[stack[0]]
                                action = dfa.actions[label]
                                string = input_str[r:l]
                                output += string + ", "+ action + "\n"
                                break
                        else:
                                while(not(len(stack)==0 or stack[0] in dfa.final_states)):
                                        if last_state_flag:
                                             last_state = stack[0]   
                                             last_state_flag = False
                                        del stack[0]
                                        l -= 1

                                if len(stack) == 0:
                                        label = dfa.labels[last_state]
                                        action = dfa.actions[label]
                                        output += input_str + ", "+ action + "\n"
                                        break

                                if stack[0] in dfa.final_states:
                                        label = dfa.labels[stack[0]]
                                        del stack[0]
                                        l -= 1
                                        action = dfa.actions[label]
                                        string = input_str[r:l+1]
                                        output += string + ", "+ action + "\n"
                                        l += 1
                                        r = l
                                        stack = [dfa.start_state]                             
        return output

if __name__ == '__main__':
        parser = argparse.ArgumentParser(add_help=True, description='Sample Commandline')

        parser.add_argument('--dfa-file', action="store", help="path of file to take as input to construct DFA", nargs="?", metavar="dfa_file")
        parser.add_argument('--input-file', action="store", help="path of file to take as input to test strings in on DFA", nargs="?", metavar="input_file")

        args = parser.parse_args()

        with open(args.dfa_file, "r", encoding='utf8') as file:
                dfa_file = file.read()

        with open(args.input_file, "r", encoding='utf8') as file:
                input_file = file.read()

        dfa_file = dfa_file.replace(", ", ",")
        dfa_list = dfa_file.split("\n")            
        dfa = construct_dfa(dfa_list)

        inputs = input_file.split("\n")
        inputs = list(filter(lambda e: e != '' and not re.match(r'^(\s)+$', e), inputs))

        output = open("task_3_1_result.txt", "w")
        for i in range(len(inputs)):
                output.write(run_fallback_dfa(dfa, inputs[i]))
                if (i<len(inputs)-1):
                        output.write("\n")
                                        
        output.close()
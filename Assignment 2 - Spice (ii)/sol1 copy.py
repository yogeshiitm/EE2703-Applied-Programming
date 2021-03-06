
"""
        EE2703 Applied Programming Lab - 2019
        Assignment 2
        Name - Yogesh Agarwala
        Roll - EE19B130

        To check the code run $python assign2_ee19b130.py <inputfile>
"""

from sys import argv, exit
import numpy as np
from numpy import cos,sin


if len(argv) != 2:
    print('\nInvalid number of arguments. Expected command: $python %s <inputfile>' % argv[0])
    exit()


CIRCUIT = '.circuit'
END = '.end'

def extract_circuit(lines):
    '''getting the circuit definition block'''
    start = -1; end = -2
    for line in lines:
        # finding the line whose first word is .circuit
        if CIRCUIT == line[:len(CIRCUIT)]:
            start = lines.index(line)
        # finding the line whose first word is .end
        elif END == line[:len(END)]:
            end = lines.index(line)
            break
    # checking if netlist file contains .circuit and .end lines
    if start== -1 and end== -2:
        print(f'Invalid circuit defination: {CIRCUIT} and {END} lines are missing in the netlist file')
        exit()
    elif start== -1:
        print(f'Invalid circuit defination: {CIRCUIT} line is missing in the netlist file')
        exit()
    elif end == -2:
        print(f'Invalid circuit defination: {END} line is missing in the netlist file')
        exit()
    # validating circuit block
    if start >= end:
        print('Invalid circuit defination')
        exit(0)
    # extracting circuit_defination between .start and .end
    circuit_defination = []
    for line in lines[start+1:end]:
        circuit_defination.append(line)
    return circuit_defination


def remove_comments(cir_def):
    ''' Remove the comments from the circuit definition block'''
    no_comment = []
    for line in cir_def:
        no_comment.append(line.split('#')[0])
    return no_comment

def validate_circuit(cir_def):
    '''Analyzing the tokens from the circuit_defination'''
    for line in cir_def:
        tokens = line.split()
        ### for resistor, inductor, conductor, independent voltage and current source
        if len(tokens)==4 and tokens[0][0] in ['R','L','C','V','I']:
            n1= tokens[1]
            n2= tokens[2]
            # checking if the nodes are alphanumeric or not
            if(not (n1.isalnum() and n2.isalnum())):
                print('Node names should be alphanumeric')
                exit()
        ### for VCVS, VSCS
        elif len(tokens)==6 and tokens[0][0] in ['E','G']:
            n1= tokens[1]
            n2= tokens[2]
            n3= tokens[3]
            n4= tokens[4]
            # checking if the nodes are alphanumeric or not
            if(not (n1.isalnum() and n2.isalnum() and n3.isalnum() and n4.isalnum())):
                print('Node names should be alphanumeric')
                exit()
        ### for CCVS, CCCS
        elif len(tokens)==5 and tokens[0][0] in ['H','F']:
            n1= tokens[1]
            n1= tokens[2]
            # checking if the nodes are alphanumeric or not
            if(not (n1.isalnum() and n2.isalnum())):
                print('Node names should be alphanumeric')
                exit()
        else:
            print('Invalid circuit defination')
            exit()


def nodes_dictionary(cir_def):
    ''' Returns a dictionary of nodes from the circuit definition. 
    By default, the GND node is assigned value 0. '''
    nodes_dict = {}
    nodes = [one_port_element(line).from_node for line in cir_def]
    nodes.extend([one_port_element(line).to_node for line in cir_def])

    node_number = 1
    nodes = list(set(nodes))
    for node in nodes:
        if node == 'GND' :
            nodes_dict[node] = 0
        else :
            nodes_dict[node] = node_number
            node_number += 1
    return nodes_dict


class one_port_element():
    ''' Class for all the one port elements'''
    def __init__(self,line):
        self.line = line
        self.tokens = self.line.split()
        self.name = element_type(self.tokens[0])
        self.from_node = self.tokens[1]
        self.to_node = self.tokens[2]
        if len(self.tokens) == 5:
            self.type = 'dc'
            self.value = float(self.tokens[4])
        elif len(self.tokens) == 6:
            self.type = 'ac'
            Vm = float(self.tokens[4])/2
            phase = float(self.tokens[5])
            real = Vm*cos(phase)
            imag = Vm*sin(phase)
            self.value = complex(real,imag)
        else:
            self.type = 'RLC'
            self.value = float(self.tokens[3])


def element_type(token):
    ''' Gets the element name '''
    if token[0] == 'R':
        return 'Resistor'
    elif token[0] == 'L':
        return 'Inductor'
    elif token[0] == 'C':
        return 'Capacitor'
    elif token[0] == 'V':
        return 'Independent Voltage Source'
    elif token[0] == 'I':
        return 'Independent Current Source'


def make_dict(cir_def,element):
    ''' Makes a dictionary for each component of the particular type of element ''' 
    e = element
    dict = {}
    names = [one_port_element(line).tokens[0] for line in cir_def if one_port_element(line).tokens[0][0].lower()== e]
    for index,name in enumerate(names):
        dict[name] = index
    return dict


def get_key(nodes_dict,value):
    ''' Gets the corresponding key for a value in the dictionary '''
    for key in nodes_dict.keys():
        if nodes_dict[key] == value :
            return key


def nodes_voltage_count(cir_def):
    ''' Returns a tuple : number of nodes, number of voltage sources '''
    volt_ind = [i for i in range(len(cir_def)) if cir_def[i].split()[0][0] == 'V']
    k = len(volt_ind)
    n = len(nodes_dictionary(cir_def))
    return n,k


def node_finder(cir_def,node_key,nodes_dict):
    ''' Finds the lines and position ie from/to of the given node '''
    indexs = [(i,j) for i in range(len(cir_def)) for j in range(len(cir_def[i].split())) if cir_def[i].split()[j] in nodes_dict.keys() if nodes_dict[cir_def[i].split()[j]] == node_key]
    return indexs


AC = '.ac' 
def get_freq(lines):
    ''' Returns the frequency of the source '''
    w = 0
    for line in lines:
        if line[:len(AC)] == '.ac' :
            w = float(line.split()[2])
    return w


def matrix(cir_def,w,node_key,nodes_dict,voltage_dict,inductor_dict,M,b):
    ''' updates the M and b matrix for the given node '''
    inds = node_finder(cir_def,node_key,nodes_dict)
    n,k = nodes_voltage_count(cir_def)
    for ind in inds:
        #getting all the attributes of the element using the class definition
        element = one_port_element(cir_def[ind[0]])
        element_name = cir_def[ind[0]].split()[0]
        if element_name[0] == 'R':
            if ind[1] == 1:
                #node is the from_node
                adj_key = nodes_dict[element.to_node]
                M[node_key,node_key] += 1/(element.value)
                M[node_key,adj_key] -= 1/(element.value)
                    
            if ind[1] == 2 :
                # node is the to_node
                adj_key = nodes_dict[element.from_node]
                M[node_key,node_key] += 1/(element.value)
                M[node_key,adj_key] -= 1/(element.value)
                
        if element_name[0] == 'C' :
            if ind[1]== 1:
                # node is the from_node
                adj_key = nodes_dict[element.to_node]
                M[node_key,node_key] += complex(0, 2*np.pi*w*(element.value))
                M[node_key,adj_key] -= complex(0, 2*np.pi*w*(element.value))
            if ind[1] == 2 :
                # node is the to_node
                adj_key = nodes_dict[element.from_node]
                M[node_key,node_key] += complex(0, 2*np.pi*w*(element.value))
                M[node_key,adj_key] -= complex(0, 2*np.pi*w*(element.value))

        if element_name[0] == 'L' :
            try:
                if ind[1]== 1:
                    adj_key = nodes_dict[element.to_node]
                    M[node_key,node_key] -= complex(0,1/(2*np.pi*w*element.value))
                    M[node_key,adj_key] += complex(0,1/(2*np.pi*w*element.value))
                if ind[1] == 2 :
                    adj_key = nodes_dict[element.from_node]
                    M[node_key,node_key] -= complex(0,1/(2*np.pi*w*element.value))
                    M[node_key,adj_key] += complex(0,1/(2*np.pi*w*element.value))
            except ZeroDivisionError:
                index = inductor_dict[element_name]
                if ind[1]== 1:
                    adj_key = nodes_dict[element.to_node]
                    M[node_key,n+k+index] += 1 
                    M[n+k+index,node_key] -= 1
                    b[n+k+index] = 0
                if ind[1]== 2:
                    M[node_key,n+k+index] -= 1
                    M[n+k+index,node_key] += 1
                    b[n+k+index] = 0
        if element_name[0] == 'V' :
            index = voltage_dict[element_name]
            if ind[1]== 1:
                adj_key = nodes_dict[element.to_node]
                M[node_key,n+index] += 1
                M[n+index,node_key] -= 1
                b[n+index] = element.value
            if ind[1] == 2 :
                adj_key = nodes_dict[element.from_node]
                M[node_key,n+index] -= 1
                M[n+index,node_key] +=1
                b[n+index] = element.value

        if element_name[0] == 'I' :
            if ind[1]== 1:
                b[node_key] -= element.value
            if ind[1] == 2 :
                b[node_key] += element.value


''' Main function '''
try:
    if len(argv) != 2:
        print('\nInvalid number of arguments. Expected command: $python %s <inputfile>' % argv[0])
        exit()

    with open(argv[1]) as f:
        # read the lines and then close the netlist file
        lines = f.readlines()
        f.close()

        cir_def = extract_circuit(lines)
        cir_def = remove_comments(cir_def)
        validate_circuit(cir_def)

        nodes_dict = nodes_dictionary(cir_def)
        voltage_dict = make_dict(cir_def,'v')
        inductor_dict = make_dict(cir_def,'l')
        n,k = nodes_voltage_count(cir_def)
        w = get_freq(lines)

        print('The node dictionary is :',nodes_dict)
        print('The voltage dictionary is :',voltage_dict)
        print('The inductor dictionary is :',inductor_dict)

        M = np.zeros((n+k,n+k),dtype=complex)
        b = np.zeros(n+k,dtype=complex)
        dc_flag = False 
        if w == 0:
            dc_flag = True
            M = np.zeros((n+k+len(inductor_dict),n+k+len(inductor_dict)),dtype=complex)
            b = np.zeros(n+k+len(inductor_dict),dtype=complex)

        for i in range(len(nodes_dict)):
            matrix(cir_def,w,i,nodes_dict,voltage_dict,inductor_dict,M,b)
        M[0] = 0
        M[0,0] = 1
        print('The M matrix is :\n',M)
        print('The b matrix is :\n',b)
        try:
            x = np.linalg.solve(M,b)
        except Exception:
            print('The incidence matrix cannot be inverted as it is singular. Please provide a valid circuit definition')
            sys.exit()
        for i in range(n):
            print("Voltage at Node {} = {}".format(get_key(nodes_dict,i),x[i]))
        for j in range(k):
            print('Current through the source {} = {}'.format(get_key(voltage_dict,j),x[n+j]))
        if dc_flag:
            for i in range(len(inductor_dict)):
                print("Current through the inductor {} = {}".format(get_key(inductor_dict,i),x[n+k+i]))   


# if the file could not be found
except IOError:
    filename = argv[1]
    print(f'Invalid file: {filename}')
    exit()
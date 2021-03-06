
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

# It's recommended to use constant variables than hard-coding them everywhere.
CIRCUIT = '.circuit'
END = '.end'


# Checks if the number of arguments received in commandline is correct
if len(argv) != 2:
    print('\nInvalid command, expected: $python %s <inputfile>' % argv[0])
    exit()

class one_port_element():
    ''' General class for all the one port elements '''
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

def convert_to_dict(cir_def):
    ''' Returns a dictionary of nodes from the circuit definition. By default, the GND node is assigned value 0. '''
    diction = {}
    nodes = [one_port_element(line).from_node for line in cir_def]
    nodes.extend([one_port_element(line).to_node for line in cir_def])
    ind = 1
    nodes = list(set(nodes))
    for node in nodes:
        if node == 'GND' :
            diction[node] = 0
        else :
            diction[node] = ind
            ind += 1
    return diction


def get_key(diction,value):
    ''' Gets the corresponding key for a value in the dictionary '''
    for key in diction.keys():
        if diction[key] == value :
            return key

def make_dict(cir_def,element):
    ''' Makes a dictionary for each component of the particular type of element ''' 
    e = element
    volt_dict = {}
    volt_names = [one_port_element(line).tokens[0] for line in cir_def if one_port_element(line).tokens[0][0].lower()== e]
    for ind,name in enumerate(volt_names):
        volt_dict[name] = ind
    return volt_dict


AC = '.ac' 
def get_freq(lines):
    ''' Returns the frequency of the source '''
    w = 0
    for line in lines:
        if line[:len(AC)] == '.ac' :
            w = float(line.split()[2])
    return w


def matrix_dims(cir_def):
    ''' Returns a tuple : number of nodes, number of voltage sources '''
    volt_ind = [i for i in range(len(cir_def)) if cir_def[i].split()[0][0] == 'V']
    k = len(volt_ind)
    n = len(convert_to_dict(cir_def))
    return n,k
    
def node_finder(cir_def,node_key,diction):
    ''' Finds the lines and position ie from/to of the given node '''
    inds = [(i,j) for i in range(len(cir_def)) for j in range(len(cir_def[i].split())) if cir_def[i].split()[j] in diction.keys() if diction[cir_def[i].split()[j]] == node_key]
    return inds

def mod_matrix(cir_def,w,node_key,diction,volt_dict,ind_dict,M,b):
    ''' Updates the M and b matrix for the given node '''
    inds = node_finder(cir_def,node_key,diction)
    n,k = matrix_dims(cir_def)
    for ind in inds:
        #getting all the attributes of the element using the class definition
        element = one_port_element(cir_def[ind[0]])
        element_name = cir_def[ind[0]].split()[0]
        if element_name[0] == 'R':
            if ind[1] == 1:
                #node is the from_node
                adj_key = diction[element.to_node]
                M[node_key,node_key] += 1/(element.value)
                M[node_key,adj_key] -= 1/(element.value)
                    
            if ind[1] == 2 :
                # node is the to_node
                adj_key = diction[element.from_node]
                M[node_key,node_key] += 1/(element.value)
                M[node_key,adj_key] -= 1/(element.value)
                
        if element_name[0] == 'C' :
            if ind[1]== 1:
                # node is the from_node
                adj_key = diction[element.to_node]
                M[node_key,node_key] += complex(0, 2*np.pi*w*(element.value))
                M[node_key,adj_key] -= complex(0, 2*np.pi*w*(element.value))
            if ind[1] == 2 :
                # node is the to_node
                adj_key = diction[element.from_node]
                M[node_key,node_key] += complex(0, 2*np.pi*w*(element.value))
                M[node_key,adj_key] -= complex(0, 2*np.pi*w*(element.value))

        if element_name[0] == 'L' :
            try:
                if ind[1]== 1:
                    adj_key = diction[element.to_node]
                    M[node_key,node_key] -= complex(0,1/(2*np.pi*w*element.value))
                    M[node_key,adj_key] += complex(0,1/(2*np.pi*w*element.value))
                if ind[1] == 2 :
                    adj_key = diction[element.from_node]
                    M[node_key,node_key] -= complex(0,1/(2*np.pi*w*element.value))
                    M[node_key,adj_key] += complex(0,1/(2*np.pi*w*element.value))
            except ZeroDivisionError:
                index = ind_dict[element_name]
                if ind[1]== 1:
                    adj_key = diction[element.to_node]
                    M[node_key,n+k+index] += 1 
                    M[n+k+index,node_key] -= 1
                    b[n+k+index] = 0
                if ind[1]== 2:
                    M[node_key,n+k+index] -= 1
                    M[n+k+index,node_key] += 1
                    b[n+k+index] = 0
        if element_name[0] == 'V' :
            index = volt_dict[element_name]
            if ind[1]== 1:
                adj_key = diction[element.to_node]
                M[node_key,n+index] += 1
                M[n+index,node_key] -= 1
                b[n+index] = element.value
            if ind[1] == 2 :
                adj_key = diction[element.from_node]
                M[node_key,n+index] -= 1
                M[n+index,node_key] +=1
                b[n+index] = element.value

        if element_name[0] == 'I' :
            if ind[1]== 1:
                b[node_key] -= element.value
            if ind[1] == 2 :
                b[node_key] += element.value

# class Component():
#     def __init__(self,name,node1,node2,value,element):
#         self.name = name
#         self.node1 = node1
#         self.node2 = node2
#         self.value = value
#         self.element = element


# try-except is used to catch the error in case wrong filename is entered
try:
    with open(argv[1]) as f:

        # read the lines and then close the netlist file
        lines = f.readlines()
        f.close()


        # these values will be changed only if .ciruit and .end are found in the netlist file
        start = -1; end = -2
        for line in lines:
            # finding the line whose first word is .circuit
            if CIRCUIT == line[:len(CIRCUIT)]:
                start = lines.index(line)
                line_number = start+1
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


        # Parse each line of the circuit part and analyse the words(tokens)
        else:
            ##### extracting circuit_defination between .start and .end
            circuit_defination = []
            for line in lines[start+1:end]:
                circuit_defination.append(line)

            ##### removing comments from the circuit_defination
            circuit_defination_no_comment = []
            for line in circuit_defination:
                circuit_defination_no_comment.append(line.split('#')[0])

            
            ##### Analyzing the tokens from the circuit_defination
            for line in circuit_defination_no_comment:

                line_number +=1
                ### extracting the tokens
                tokens = line.split()

                ### for resistor, inductor, conductor, independent voltage and current source
                if len(tokens)==4:
                    if tokens[0][0] == 'R':
                        element='Resistor'
                    elif tokens[0][0] == 'L':
                        element='Inductor'
                    elif tokens[0][0] == 'C':
                        element='Capacitor'
                    elif tokens[0][0] == 'V':
                        element='Independent Voltage Source'
                    elif tokens[0][0] == 'I':
                        element='Independent Current Source'
                    # if the number of tokens are 4
                    # but the line don't start with R/L/C/V/I
                    # then it don't satisfy the circuit defination
                    else:
                        print(f'Line {line_number}: Invalid circuit defination')
                        continue
                    
                    n1= tokens[1]
                    n2= tokens[2]
                    # checking if the nodes are alphanumeric or not
                    if(not (n1.isalnum() and n2.isalnum())):
                        print(f'Line {line_number}: Node names should be alphanumeric')
                        continue

                    print (f'Line {line_number}: Element:{element}, n1:{n1}, n2:{n2}, value:{tokens[3]}')

                ### for VCVS, VSCS
                elif len(tokens)==6:
                    if tokens[0][0] == 'E':
                        element='Voltage Controlled Voltage Source'
                    elif tokens[0][0] == 'G':
                        element='Voltage Controlled Current Source'
                    # if the number of tokens are 6
                    # but the line don't start with E/G
                    # then it don't satisfy the circuit defination
                    else:
                        print(f'Line {line_number}: Invalid circuit defination')
                        continue

                    n1= tokens[1]
                    n2= tokens[2]
                    n3= tokens[3]
                    n4= tokens[4]
                    # checking if the nodes are alphanumeric or not
                    if(not (n1.isalnum() and n2.isalnum() and n3.isalnum() and n4.isalnum())):
                        print(f'Line {line_number}: Node names should be alphanumeric')
                        continue

                    print (f'Line {line_number}: Element:{element}, n1:{n1}, n2:{n2}, n3:{n3}, n4:{n4}, value:{tokens[5]}')

                ### for CCVS, CCCS
                elif len(tokens)==5:
                    if tokens[0][0] == 'H':
                        element='Current Controlled Voltage Source'
                    elif tokens[0][0] == 'F':
                        element='Current Controlled Current Source'
                    # if the number of tokens are 5
                    # but the line don't start with H/F
                    # then it don't satisfy the circuit defination
                    else:
                        print(f'Line {line_number}: Invalid circuit defination')
                        continue

                    n1= tokens[1]
                    n1= tokens[2]
                    # checking if the nodes are alphanumeric or not
                    if(not (n1.isalnum() and n2.isalnum())):
                        print(f'Line {line_number}: Node names should be alphanumeric')
                        continue

                    # for CCVS, CCCS syntax is
                    # name n1 n2 vname value
                    # where vname should begin with V...
                    vname = tokens[3]
                    if not vname[0] == 'V':
                        print(f'Line {line_number}: vname should be of the form V...')
                        continue

                    print (f'Line {line_number}: Element:{element}, n1:{n1}, n2:{n2}, vname:{vname} value:{tokens[4]}')

                # if the tokens don't satisty the above conditions
                # then it don't comes under circuit defination
                else:
                    print(f'Line {line_number}: Invalid circuit defination')
                    continue




# if the file could not be found
except IOError:
    filename = argv[1]
    print(f'Invalid file: {filename}')
    exit()
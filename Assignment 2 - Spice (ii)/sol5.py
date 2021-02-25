'''
LTSpice Part 2
written by Pruthvi Raj RG
EE17B114
'''
'''
This code is applicable for DC circuits with resistors,current sources and voltage sources and AC circuits with all components.
This code expects the input in this format:
DC sources: I1 GND 1 dc 10 or V1 GND 1 dc 10
AC sources: I1 GND 1 dc 10(vpp) 0.5(phase)

defining ac volatge/current sources and frequency:
.ac V1 1000(frequency) or .ac I1 1000

This file outputs RMS voltages and currrents.To get the instantaneous value we can just multiply the value by sqrt(2).
'''




#importing neccesery packages/libs
import sys
import math
import cmath
import numpy as np

if(len(sys.argv)!=2):
	print("Invalid file name")
	exit()

else:
	if(sys.argv[1].endswith('.netlist')):
		f = open(sys.argv[1],'r')

#to extract the circuit definition
flag = 0
circuit_def_array = []
circuit_ac_def_array = []
lines = f.readlines()

#collecting all the lines in the file:
for line in lines:
    if line.split(' ')[0] == '.ac' :
        circuit_ac_def_array.append(line)
#extrating the circuit part.        
for line in lines:
    if line == '.circuit\n' :
        flag = 1
    if line == '.end\n' or line == ".end":
        flag = 0
    if flag == 1:
        circuit_def_array.append(line)

#to avoid addiinf '.circuit' to the circuit def

circuit_def_array = circuit_def_array[1:]
non_comment_def =[]
# to remove comments:
for i in circuit_def_array:
    non_comment_def.append(i.split(' #')[0])

stripped_array = []

for i in non_comment_def:
	stripped_array.append(i.rstrip())

list.reverse(stripped_array)

final_array= []

for i in stripped_array:
	list_bla = i.split(" ")
	list.reverse(list_bla)
	final_array.append(list_bla)

final_string = []

for i in final_array:
	string = ' '.join(i)
	final_string.append(string)

#defining our own value reader to read the values of the components given in the circuit netlist;
def value_reader(value):
    try:
        val = float(value)
        return val
    except ValueError:
        value_string = value
        if 'e' in value_string:
            split_array = value_string.split('k')
            #print(split_array)
            coefficient = split_array[0]
            exponent = split_array[1]
            return(float(coefficient)*(10**(float(exponent))))
        if 'k' in value_string:
            split_array = value_string.split('k')
            #print(split_array)
            coefficient = split_array[0]
            return(1000*float(coefficient))

#if the circuit is ac:
if circuit_ac_def_array!= []:
	circuit_ac_def_array[-1] = circuit_ac_def_array[-1].rstrip()
	#removing white spaces from lines
	alfa_3 = 0
	for i in circuit_ac_def_array:
	    circuit_ac_def_array[alfa_3]= circuit_ac_def_array[alfa_3].rstrip()
	    alfa_3 = alfa_3+1
	#spiltting the netlist lines to extract components
	alfa_4 = 0
	for i in circuit_ac_def_array:
	    circuit_ac_def_array[alfa_4] = i.split(' ')[1:]
	    alfa_4 = alfa_4+1

#setting frequency according to ac or dc:
if circuit_ac_def_array == []:
    is_ac = False
    frequency = 0
else:
    is_ac = True
    frequency = value_reader(circuit_ac_def_array[0][1])

#reverting back the list created by previous labs code:
for i in final_array:
	list.reverse(i)
final_array_straight = final_array
components = [i[0] for i in final_array_straight]

#collecting all the volatage sources for easy processing:
comps_voltage = []
for i in final_array_straight:
    if i[0][0]=='V':
        comps_voltage.append(i)

#likewise collecting all the UNIQUE nodes present in the network:
nodes_1 = [i[1] for i in final_array_straight]
nodes_2 = [i[2] for i in final_array_straight]
nodes = nodes_1 + nodes_2
nodes = list(set(nodes))

#assigning indices for the nodes which are found:
nodes_dict = {}
alfa = 0
for i in nodes:
    nodes_dict[i] = alfa
    alfa = alfa + 1
#assigning indices for the voltage_sources which are found:
volt_dict = {}
alfa = 0
for i in comps_voltage:
    volt_dict[alfa] = i
    alfa = alfa + 1
#finding all the components connected to a certain node:
node_connected_elements = {}
for i in nodes:
    node_connected_comps = []
    for t in final_array_straight:
        if t[1]==i or t[2]==i:
            node_connected_comps.append(t)
    node_connected_elements[i] = node_connected_comps

#total number of nodes;
num_nodes = len(nodes)
num_voltage_sources = len(comps_voltage)

#initializing values of M and B
M = np.zeros((num_nodes+num_voltage_sources+1,num_nodes+num_voltage_sources+1),dtype=complex)
#setting ground to zero:
M[-1][nodes_dict['GND']] = 1
b = np.zeros((num_nodes+num_voltage_sources+1,1),dtype=complex)


#updating matrix elements for voltage sources
alfa_0 = 0
for i in comps_voltage:
    if frequency != 0:
        #updating M
        node_1 = i[1]
        node_2 = i[2]
        
        frequency = None
        
        for t in circuit_ac_def_array:
            if i[0] == t[0]:
                frequency = t[1]
            
        phase = i[-1]
        value = cmath.rect(value_reader(i[4])/(2*math.sqrt(2)),value_reader(phase))
        node_index_n1 = nodes_dict[node_1]
        node_index_n2 = nodes_dict[node_2]
        M[num_nodes+alfa_0][node_index_n1] = -1
        M[num_nodes+alfa_0][node_index_n2] = 1
        
    else:
        frequency = 0
        node_1 = i[1]
        node_2 = i[2]
        value = cmath.rect(value_reader(i[4]),0)
        node_index_n1 = nodes_dict[node_1]
        node_index_n2 = nodes_dict[node_2]
        M[num_nodes+alfa_0][node_index_n1] = -1
        M[num_nodes+alfa_0][node_index_n2] = 1
    
    #updating b
    b[num_nodes+alfa_0] = value

#Applying kirchoff -current law for nodes and updating in the matrix corresponding to each element:

for i in nodes:
    node_index= nodes_dict[i]
    connected_elements = node_connected_elements[i]
    
    for t in connected_elements:
        
        if t[0][0]=='R':
            if t[1]==i:
                other_node_r = t[2]
            else:
                other_node_r = t[1]    
            
            other_node_index_r = nodes_dict[other_node_r]
            
            M[node_index][node_index] = M[node_index][node_index] + (1.0/cmath.rect(value_reader(t[3]),0))
            M[node_index][other_node_index_r]= M[node_index][other_node_index_r] - (1.0/cmath.rect(value_reader(t[3]),0))
            
            
        if t[0][0]=='V':
            if t[1]==i:
                other_node_v = t[2]
                polarity_v= 1
            else:
                other_node_v = t[1]
                polarity_v= 0
            
            print(polarity_v)
            
            other_node_index_v = nodes_dict[other_node_v]
            
            for index,v_source in volt_dict.items():
                if v_source == t:
                    volt_source_index = index
                    
            if polarity_v == 1:
                M[node_index][num_nodes+volt_source_index] = 1
            else:
                M[node_index][num_nodes+volt_source_index] = -1
                
        if t[0][0]=='I':
            if frequency == 0:
                if t[1]==i:
                    other_node_i = t[2]
                    polarity_i= 1
                else:
                    other_node_i = t[1]
                    polarity_i= 0
                other_node_index_i = nodes_dict[other_node_i]

                if polarity_i == 1:
                    b[node_index] = b[node_index]+ cmath.rect(value_reader(t[4]),0)
                else:
                    b[node_index] = b[node_index]- cmath.rect(value_reader(t[4]),0)
            else:
                if t[1]==i:
                    other_node_i = t[2]
                    polarity_i= 1
                else:
                    other_node_i = t[1]
                    polarity_i= 0
                other_node_index_i = nodes_dict[other_node_i]

                if polarity_i == 1:
                    b[node_index] = b[node_index]+ cmath.rect(value_reader(t[4])/2,value_reader(t[5]))
                else:
                    b[node_index] = b[node_index]- cmath.rect(value_reader(t[4])/2,value_reader(t[5]))
                
        if t[0][0]=='C':
            if t[1]==i:
                other_node_r = t[2]
            else:
                other_node_r = t[1]    
            
            other_node_index_r = nodes_dict[other_node_r]
            
            M[node_index][node_index] = M[node_index][node_index] + cmath.rect(2*math.pi*value_reader(frequency),0)*cmath.rect(value_reader(t[3]),(math.pi)/2)
            M[node_index][other_node_index_r]= M[node_index][other_node_index_r] - cmath.rect(2*math.pi*value_reader(frequency),0)*cmath.rect(value_reader(t[3]),(math.pi)/2)


        if t[0][0]=='L':
            if t[1]==i:
                other_node_r = t[2]
            else:
                other_node_r = t[1]    
            
            other_node_index_r = nodes_dict[other_node_r]
            
            M[node_index][node_index] = M[node_index][node_index] + (1/(cmath.rect(2*math.pi*value_reader(frequency),0)*cmath.rect(value_reader(t[3]),(math.pi)/2)))
            M[node_index][other_node_index_r]= M[node_index][other_node_index_r] - (1/(cmath.rect(2*math.pi*value_reader(frequency),0)*cmath.rect(value_reader(t[3]),(math.pi)/2)))

#SOLVING THE MATRIX EQUATIONS:        
x = np.linalg.lstsq(M, b)

#loading voltage values into a list for easy printing:
str_0 = "voltage at node  "
t = 0
final_node_voltages = []
for i in nodes_dict:
    if i == 'GND':
        str_1 = str_0 + "GND" + "  is ===> " + '[0.]'
        final_node_voltages.append(str_1)
        t = t+1
    
    else:
        str_1 = str_0 + str(i) + "  is ===> " + str(x[0][t])
        final_node_voltages.append(str_1)
        t = t+1
#loading current values into a list for easy printing:
str_0 = "current through the voltage source  "
t = 0
voltage_source_currents = []
for i in volt_dict:
    str_1 = str_0 + volt_dict[i][0]  + "  is ===> " + str(x[0][t+num_nodes])
    voltage_source_currents.append(str_1)
    t = t+1

print('\n');print('\n');print('\n')
#printing the final results:
print('THE RMS VALUES OF THE NODE VOLTAGES ARE : ')

for i in final_node_voltages:
	print(i)
	print('\n')

print('THE RMS VALUES OF THE CURRENTS FLOWING THROUGH VOLTAGE SOURCES FROM NEGETIVE TERMINAL TO POSITIVE TERMINAL ARE:')
print('\n')
for i in voltage_source_currents:
	print(i)
	print('\n')


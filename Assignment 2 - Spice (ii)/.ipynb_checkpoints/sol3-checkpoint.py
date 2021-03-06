#!/usr/bin/env python3

import sys
import os
import numpy as np
import cmath

DEVICES = ['R','C','L','V','I','E','F','G','H']

def main():
    # Checks if the number of arguments is correct, else exits the script.
    if len(sys.argv) != 2:
        print("Incorrect format.The correct format is $ python3 assign2.py filename")
        sys.exit()
    else:
        filename = sys.argv[1]

    # Checks if the file exists, else exits the script.
    try:
        f = open(filename,'r')
    except IOError:
        print('Could not read the file:{0}'.format(filename))
        sys.exit()        

    lines = f.read().splitlines()
    f.close()
    # print(lines)

    def ExtractCircuit(lines):
        """
        Extracts the circuit part from the netlist file.

        Args:
            A list of lines of the parsed file.
        
        Returns:
            A list describing the circuit removing all the comments and other parts.
        """
        final_circuit,flag,ac_flag,circuit = [],0,0,[]
        for line in lines:
            words = line.strip().split()
            newline = []
            for word in words:
                if word[0] == '#':
                    break
                newline.append(word)
            newline = ' '.join(newline)
            circuit.append(newline)
        
        for line in circuit:
            # print(line.split(' ',1)[0])
            if line == '.circuit':
                final_circuit.append(line)
                flag = 1
            elif line == '.end' and flag == 1:
                final_circuit.append(line)
                flag = 2
            elif line.split(' ',1)[0] == '.ac' and flag == 2:
                final_circuit.append(line)
                ac_flag = 1
            elif flag == 1:
                final_circuit.append(line)
        
        if len(final_circuit) == 0:
            print('The netlist file doesnot contain ".circuit" and/or ".end" line.')
            sys.exit()

        if final_circuit[-1] != '.end' and ac_flag == 0:
            print('The netlist file doesnot contain ".end" line.')
            sys.exit()
        
        return ac_flag,final_circuit
    
    def val(Str):
        """
        Returns the numeric value from exponential notation.
        """
        if Str.isnumeric() or '-' in Str or '.' in Str:
            return float(Str)
        if Str.isalnum() or '-' in Str or '.' in Str:
            i = Str.index('e')
            try:
                c,m = float(Str[:i]),int(Str[i+1:])
                return c * (10**m)
            except Exception:
                print('Error in numeric values.')
                sys.exit()
        return
    
    def Nodes(circuit):
        """
        Extracts nodes from the circuit.

        Args:
            A list describing the circuit.
        
        Returns:
            Returns a dictionary containing nodes.
        """
        nodes,nodes_dict = [],{}
        for line in circuit:
            words = line.split()
            x = words[0][0]
            if x in DEVICES:
                nodes.extend(words[1:3])
            else:
                print('Unidentified type of device.')
                sys.exit()
        nodes = list(set(nodes))
        for i,node in enumerate(nodes):
            nodes_dict[node] = i
        for key,value in nodes_dict.items():
            if value == 0:
                nodes_dict[key],nodes_dict['GND'] = nodes_dict['GND'],0
        return nodes_dict

    def Print():
        """
        Utility function to print the variables.
        """
        print('Incidence matrix:');print(graph)
        print('Z:');print(Z)
        print('R:');print(R)
        print('C:');print(C)
        print('L:');print(L)
        print('A:');print(A)
        print('b:');print(b)
    
    def PrintSolution(solution,inv_nodes,nodes):
        """
        Utility function to print the solution.
        """
        for key,value in inv_nodes.items():
            if value in nodes:
                print('V_' + str(value),end = ' ')
                print('= {0:.6f} ' .format(solution[key]),end = 'V\n')
            else:
                print('I_' + str(value),end = ' ')
                print('= {0:.6f} ' .format(-solution[key]),end = 'A\n')

    ac_flag,final_circuit = ExtractCircuit(lines)
    dtype = np.float
    if ac_flag:
        dtype = np.complex
        freq = val(final_circuit[-1].split()[2])
        w = 2 * np.pi * freq
        del final_circuit[-1]
    del final_circuit[0],final_circuit[-1]

    nodes = Nodes(final_circuit)
    ind_curr = np.zeros(len(nodes),dtype = dtype)
    graph = np.zeros((len(nodes),len(nodes)),dtype = np.int32)
    Z,V = np.zeros_like(graph),np.zeros_like(graph)
    R,C,L = -np.ones_like(graph,dtype = dtype),-np.ones_like(graph,dtype = dtype),\
                                            -np.ones_like(graph,dtype = dtype)
    variables = nodes.copy()                                      
    for line in final_circuit:
        if line[0] == 'V':
            words = line.split()
            variables[words[0]] = len(variables)
        
    inv_var = variables.__class__(map(reversed,variables.items()))

    n_variables = len(variables)
    A = np.zeros((n_variables,n_variables),dtype = dtype)
    b = np.zeros((n_variables),dtype = dtype)
    solution = np.zeros_like(b)
    n_eq = 0

    for line in final_circuit:
        words = line.split()
        x = words[0][0]
        pos,neg = nodes[words[1]],nodes[words[2]]
        graph[pos,neg],graph[neg,pos] = 1,1
        value = val(words[-1])
        if x == 'V':
            V[pos,neg],V[neg,pos] = variables[words[0]],-variables[words[0]]
            if words[3] == 'ac':
                phase = value
                A[n_eq,pos],A[n_eq,neg],b[n_eq] = 1,-1,cmath.rect(val(words[-2])*0.5,phase)
                n_eq += 1
            elif words[3] == 'dc':
                A[n_eq,pos],A[n_eq,neg],b[n_eq] = 1,-1,value
                n_eq += 1
            else:
                print('Error in voltage types.')
                sys.exit()
        if x == 'I':
            if words[3] == 'ac':
                phase = value
                ind_curr[pos] += cmath.rect(val(words[-2])*0.5,phase)
                ind_curr[pos] -= cmath.rect(val(words[-2])*0.5,phase)
            elif words[3] == 'dc':
                ind_curr[pos] += value
                ind_curr[neg] -= value
            else:
                print('Error in current types.')
                sys.exit()
        if x == 'R':
            Z[pos,neg],Z[neg,pos] = 1,1
            R[pos,neg] = value if R[pos,neg] == -1 else ((R[pos,neg]*value)/(value + R[pos,neg]))
            R[neg,pos] = R[pos,neg]
        if x == 'C' and ac_flag:
            Z[pos,neg],Z[neg,pos] = 1,1
            C[pos,neg] = value if C[pos,neg] == -1 else C[pos,neg] + value
            C[neg,pos] = C[pos,neg]           
        if x == 'L':
            if ac_flag:
                Z[pos,neg],Z[neg,pos] = 1,1
                L[pos,neg] = value if L[pos,neg] == -1 else ((L[pos,neg]*value)/(value + L[pos,neg]))
                L[neg,pos] = L[pos,neg]
            else:
                A[n_eq,pos],A[n_eq,neg] = 1,-1
                n_eq += 1

    I = (R > 0)*R + (C > 0)*(np.reciprocal(1j*w*C)) + (L > 0)*(1j*w*L) if ac_flag else (R > 0)*R
    
    for i in range(len(nodes)-1):
        for j in range(len(nodes)):
            if graph[i,j] and Z[i,j]:
                A[n_eq,i] += np.reciprocal(I[i,j])
                A[n_eq,j] -= np.reciprocal(I[i,j])
            if graph[i,j] and V[i,j]:
                A[n_eq,abs(V[i,j])] += np.sign(V[i,j])               
        b[n_eq] -= ind_curr[i]
        n_eq += 1
    A[n_eq,0] = 1
    
    try:
        solution = np.linalg.solve(A,b)
        PrintSolution(solution,inv_var,nodes)
    except np.linalg.LinAlgError:
        print('Singular Matrix.Inverse doesnot exist.')

if __name__ == "__main__":
    main()
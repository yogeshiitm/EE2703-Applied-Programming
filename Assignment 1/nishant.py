from sys import argv, exit

import re
CIRCUIT = '.circuit'
END = '.end'

"""
It's a good practice to check if the user has given required and only the required inputs
Otherwise, show them the expected usage.
"""

if len(argv) != 2:
    print('\nUsage: %s <inputfile>' % argv[0])
    exit()

"""
The use might input a wrong file name by mistake.
In this case, the open function will throw an IOError.
Make sure you have taken care of it using try-catch
"""
##################################################################

'''
Validations checked in the code:
1)Names should be alphanumeric and in the right notation
2)RLVCIHF - 2 nodes - alphanumeric
3)EG - 4 nodes - alphanumeric
4)In HF, the vname should be present in the circuit
    4.1) If the vname element is a voltage source then no problem otherwise 
         add a 0 volt voltage source in the controlling current's branch
5) Value should be numeric
'''
##################################################################
try:
    with open(argv[1]) as f:
        lines = f.readlines()
        start = -1; end = -2
        for line in lines:              # extracting circuit definition start and end lines
            if CIRCUIT == line[:len(CIRCUIT)]:
                start = lines.index(line)
            elif END == line[:len(END)]:
                end = lines.index(line)
                break
        if start >= end:                # validating circuit block
            print('Invalid circuit definition')
            exit(0)

        add_list = [] #For Adding a 0 Volt Voltage Source in case a source is controlled by current flowing in a branch not having a voltage source

        for line in lines[start+1:end]:
            tokens = line.split('#')[0].split()

            try:
                float(tokens[len(tokens)-1])
                pass
            except:
                print('value should be a numeric value') #Ensuring that the value is numeric
                exit(0)

            if tokens[0].isalnum():
                if tokens[0][0] in ['R','L','C','V','I'] and tokens[0][1:len(tokens[0])].isnumeric(): # Ensuring that the name is in the correct form
                    if len(tokens[1:len(tokens)-1]) < 2:
                        print('2 nodes should be specified') #Ensuring that the number of nodes is 2
                        exit(0)
                    
                    elif len(tokens[1:len(tokens)-1]) > 2:
                        print('Only 2 nodes should be specified') #Ensuring that the number of nodes is 2
                        exit(0)
                    
                    else:
                        if tokens[0][0] in ['R','L','C','V','I']: 
                            for token in tokens[1:len(tokens)-1]:
                                if token.isalnum(): # Ensuring that the node is alphanumeric
                                        pass
                                else:
                                    print("Node should be Alphanumeric !!")
                                    exit(0)

                elif tokens[0][0] in ['H','F'] and tokens[0][1:len(tokens[0])].isnumeric(): #For Current controlled Source
                    if len(tokens[1:len(tokens)-2]) < 2:
                        print('2 nodes should be specified') #Ensuring that the number of nodes is 2
                        exit(0)
                    
                    elif len(tokens[1:len(tokens)-2]) > 2:
                        print('Only 2 nodes should be specified') #Ensuring that the number of nodes is 2
                        exit(0)
                    
                    else:
                        for token in tokens[1:len(tokens)-2]:
                            if token.isalnum(): # Ensuring that the node is alphanumeric
                                pass
                            else:
                                print("Node should be Alphanumeric !!")
                                exit(0)

                        if tokens[3] in [line.split('#')[0].split()[0] for line in lines[start+1:end]]: #Checking if the Controlling current branch exists or not
                            if tokens[3][0] in ['V','E']: #Checking if the Controlling current branch already has a voltage source
                                pass
                            else:
                                for line in lines[start+1:end]:
                                    d_tokens = line.split('#')[0].split()
                                    if tokens[3] == d_tokens[0]: 
                                        add_list.append([f'V_null{len(add_list)}',f'{d_tokens[1]}',f"{d_tokens[1]}'",'0']) # Adding a 0 volt voltage source(with diff names) in the branch on whose current this current controlled source is based on.
                        else:
                            print('The Controlling Current source branch doesnt exist in the Circuit. Make sure it is there')
                            exit(0)
                                        
                elif tokens[0][0] in ['E','G'] and tokens[0][1:len(tokens[0])].isnumeric(): #Checking the Voltage controlled Sources has the correct name
                    if len(tokens[1:len(tokens)-1]) < 4:
                        print('4 nodes should be specified') #Ensuring that the number of nodes is 2
                        exit(0)
                    
                    elif len(tokens[1:len(tokens)-1]) > 4:
                        print('Only 4 nodes should be specified') #Ensuring that the number of nodes is 2
                        exit(0)
                    
                    else:
                        for token in tokens[1:len(tokens)-1]:
                            if token.isalnum():# Ensuring that the node is alphanumeric
                                pass
                            else:
                                print("Node should be Alphanumeric !!")
                                exit(0)
                            

                else:
                    print('The Element you defined is incorrect; Try using correct element name') #If the name is defined wrong, Error it out
                    exit(0)
            
            else:
                print('The Element name should be alphanumeric !!') #If the name is not alphanumeric, Error it out
                exit(0)

        for line in reversed([' '.join(reversed(line.split('#')[0].split())) for line in lines[start+1:end]]):
            print(line) # print output in reverse order
        
        for line in add_list:
            print(' '.join(reversed(line))) # printing out the added 0 volt Voltage sources in the reverse order


except IOError:
    print('Invalid file: Make sure that the file name is correct')
    exit()


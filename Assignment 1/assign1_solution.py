
"""
        EE2703 Applied Programming Lab - 2019
        Assignment 1
        Name - Yogesh Agarwala
        Roll - EE19B130

        To check the code run $python ee19b130_assign1.py <inputfile>
"""


from sys import argv, exit


"""
It's recommended to use constant variables than hard-coding them everywhere.
For example, if you decide to change the command from '.circuit' to '.start' later,
    you only need to change the constant
"""
CIRCUIT = '.circuit'
END = '.end'

# Checks if the number of arguments received is correct
if len(argv) != 2:
    print('\nInvalid command, expected type: $python %s <inputfile>' % argv[0])
    exit()


"""
The use might input a wrong file name by mistake.
In this case, the open function will throw an IOError.
Make sure you have taken care of it using try-catch
"""
try:
    with open(argv[1]) as f:
        lines = f.readlines()
        f.close()
        start = -1; end = -2
        # extracting circuit defination between start and end lines
        for line in lines:
            if CIRCUIT == line[:len(CIRCUIT)]:
                start = lines.index(line)
            elif END == line[:len(END)]:
                end = lines.index(line)
                break
        
        # checking if netlist file contains .circuit and .end lines
        if start== -1 and end== -2:
            print(f'Invalid circuit defination: {CIRCUIT} and {END} lines are missing')
            exit()
        elif start== -1:
            print(f'Invalid circuit defination: {CIRCUIT} line is missing')
            exit()
        elif end == -2:
            print(f'Invalid circuit defination: {END} line is missing')
            exit()

        # validating circuit block
        if start >= end:
            print('Invalid circuit defination')
            exit(0)

        # Parse each line of the circuit part and analyse the words(tokens)
        else:
            line_number = start+1
            for line in lines[start+1:end]:
                
                line_number +=1
                # extracting the tokens after ignoring the comments
                tokens = line.split('#')[0].split()

                # for resistor, inductor, conductor, independent voltage and current source
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

                    print (f'Element:{element}, n1:{n1}, n2:{n2}, value:{tokens[3]}')

                # for VCVS, VSCS
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

                    print (f'Element:{element}, n1:{n1}, n2:{n2}, n3:{n3}, n4:{n4}, value:{tokens[5]}')

                # for CCVS, CCCS
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

                    print (f'Element:{element}, n1:{n1}, n2:{n2}, vname:{tokens[3]} value:{tokens[4]}')

                # if the tokens don't satisty the above conditions
                # then it don't comes under circuit defination
                else:
                    print(f'Line {line_number}: Invalid circuit defination')
                    continue


        # print out each line with words in reverse order.
        print('Words in reverse order:') 
        for line in reversed(lines[start+1:end]):
            # in below code line.split('#')[0] ensures that comments are neglected
            for word in reversed(line.split('#')[0].split()):
                print(word, end=' ')
            print('\b')


# if the file could not be found
except IOError:
    filename = argv[1]
    print(f'Invalid file: {filename}')
    exit()
from sys import argv, exit

CIRCUIT = '.circuit'
END = '.end'

if len(argv) != 2:
    print('\nUsage: %s <inputfile>' % argv[0])
    exit()

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

        else:
            for line in lines[start+1:end]:
                tokens = line.split('#')[0].split()
                if tokens[0][0] == 'R' and len(tokens)==4:
                    print (f'Element:Resistor, n1:{tokens[1]}, n2:{tokens[2]}, value:{tokens[3]}')

                elif tokens[0][0] == 'L' and len(tokens)==4:
                    print (f'Element:Inductor, n1:{tokens[1]}, n2:{tokens[2]}, value:{tokens[3]}')

                elif tokens[0][0] == 'C' and len(tokens)==4:
                    print (f'Element:Capacitor, n1:{tokens[1]}, n2:{tokens[2]}, value:{tokens[3]}')

                elif tokens[0][0] == 'V' and len(tokens)==4:
                    print (f'Element:Independent Voltage Source, n1:{tokens[1]}, n2:{tokens[2]}, value:{tokens[3]}')

                elif tokens[0][0] == 'I' and len(tokens)==4:
                    print (f'Element:Independent Current Source, n1:{tokens[1]}, n2:{tokens[2]}, value:{tokens[3]}')

                elif tokens[0][0] == 'E' and len(tokens)==6:
                    print (f'Element:Voltage Controlled Voltage Source, n1:{tokens[1]}, n2:{tokens[2]}, n3:{tokens[3]}, n4:{tokens[4]}, value:{tokens[5]}')

                elif tokens[0][0] == 'G' and len(tokens)==6:
                    print (f'Element:Voltage Controlled Current Source, n1:{tokens[1]}, n2:{tokens[2]}, n3:{tokens[3]}, n4:{tokens[4]}, value:{tokens[5]}')

                elif tokens[0][0] == 'H' and len(tokens)==5:
                    print (f'Element:Current Controlled Voltage Source, n1:{tokens[1]}, n2:{tokens[2]}, vname:{tokens[3]}, value:{tokens[4]}')

                elif tokens[0][0] == 'F' and len(tokens)==5:
                    print (f'Element:Current Controlled Current Source, n1:{tokens[1]}, n2:{tokens[2]}, vname:{tokens[3]}, value:{tokens[4]}')

                else:
                    print('Invalid Format')


        print('Words in reverse order:')  

        for line in reversed([' '.join(reversed(line.split('#')[0].split())) for line in lines[start+1:end]]):
            print(line)                 # print output

except IOError:
    print('Invalid file')
    exit()
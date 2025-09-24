#Matthew Gomes
#ENME441

import random
counter = 1
sequence = []
user_input = []
user_input2 = []
time = False



for i in range(4):
    sequence.append(random.randint(1,6))

#print(sequence)

while time == False:
    result = []

    uinput = list(input('Guess a sequence 4 values from 1-6: '))
    user_input = [int(x) for x in uinput]
    user_input1 = ' '.join(str(x) for x in user_input)

    split_input = [int(x) for x in uinput]
    print('Guess ', counter, 'of 12: ', user_input1)
    #print("generated: ", sequence)

    for i in range(4):
        if sequence[i] == split_input[i]:
            result.append('\u25CF')
    
    print(result)

    
    #checks the entire sequence to see if it matches guess
    if sequence == split_input:
        print('Correct - you win!')
        print(sequence)
        time = True
    
    counter+=1
    
    if counter > 12:
        print('You lost')
        time = True
        



    

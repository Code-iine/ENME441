#Problem 1

def between(number, lbound, hbound):

    lbound = 0
    hbound = 0.3
    mainNum = [None] * 3
    



    #Asks the user for 3 numbers, creates a list of those 3 numbers and split them into indiviudal elements
    #values = (input(('Type 3 numbers: the number, the lower bound, the upper bound, with spaces in between: '))).split()

    #Converts those string list elements into Integer list elements
    numbers = [float(x) for x in values]

    #Replaces existing lens element with the user 3 arguements
    for i in range(len(numbers)): 
        mainNum[i] = numbers[i]

    #Check if user inputed lower and upper bounds and if not, use the default bounds
    if lbound == None:
        lbound = 0
    if hbound == None:
        hbound = 0.3

    #Compares the first number with the bounds
    if numbers[0] >= lbound and numbers[0] <= hbound:
        print('true')
    else:
        print('False')


#values = (input(('Type 3 numbers: the number, the lower bound, the upper bound, with spaces in between: '))).split()

between(5,0,0.5)
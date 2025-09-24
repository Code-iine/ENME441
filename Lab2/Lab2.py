#Matthew Gomes
#ENME441

#Problem 1

#number ask for main number
#lbound/hbound set to none by default if no parameters are given
def between(number, lbound = None, hbound = None):
    
    #if loop checks if parameters are empty or not
    if lbound == None:
        lbound = 0
    if hbound == None:
        hbound = 0.3

    ''' 
    #for loop checks the number between given bounds
    #Returns either true or false
    for i in range(lbound,hbound+1):
        if i == number:
            print('True')
            return True
        
        elif (i == hbound and i != number):
            print('False')
            return False
    '''

    test = lbound <= number <= hbound
    if test == True:
            #print('True')
            return True
    else:
        #print('False')
        return False

#############################################

#Problem 2
def rangef(max,step):
    
    difference = max/step

    for i in range(int(difference) + 1):
        yield i * step

#Uncomment the below code to run problem 2
'''
for i in rangef(5,0.5): 
        print(i, end=' ')
'''

#############################################

#Problem 3
alist = []

def rangeStep(max,step):
    
    difference = max/step

    for i in range(int(difference) + 1):
        yield i * step
        alist.append(i*step)
        print(alist)
    
##Uncomment the below code to run problem 3A & b

'''
for i in rangeStep(1,0.25):
    print(i, end = ' ')
'''


#############################################

##Problem 3.A
#uncomment code to run problem 3a
'''
blist = alist[:]
blist.reverse()
alist.extend(blist)
print(alist)
'''

#############################################

#uncomment print line to run problem 3B
#Problem 3.B
lamba = alist[:]
lamba.sort(key = lambda x: between(x, 0, 0.3))
#print(lamba)


#################################################
#Problem 4

#Uncomment print line to run problem 4
divisible = [x for x in range(0,16) if x % 2 == 0 or x % 3 == 0]
#print(divisible)n 


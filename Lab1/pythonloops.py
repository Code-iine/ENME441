#Question 1

x = 0.5
sum = 0

kterms = 5
kstart = 1
kend = kterms + 1


for k in range(kstart,kend,1):
    term1 = (-1)**(k-1)
    term2 = (x-1)**k
    eqn = (term1*term2)/k
    sum = (eqn) + sum
    
print( f'f({x}) ~= {sum:.9f} with {kterms} terms')
      


#Question 2

sum2 = 0
k = 1
while True:
    term1 = (-1)**(k-1)
    term2 = (x-1)**k
    eqn1 = (term1*term2)/k
    sum2 += (eqn1)
    k = k + 1

    if abs(eqn1) < 10**(-7):
        break
    
print( f'f({x}) ~= {sum2:.9f} with {k} terms')
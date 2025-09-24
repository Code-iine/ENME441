
while True:
    try:
        val = int(input('Enter Value: ')) #converts the string input to integer
        with open('data.txt', 'r') as f:
            for v in f:
                if int(v) > val:
                    print(v.strip())
        
    except:
        print('Must enter a numerical value!')
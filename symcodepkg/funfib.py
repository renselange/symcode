
def fib(n):
    a = 0
    b = 1
    c = 0
    for _ in range(n):
        a,b = b,a+b
        c += 1
        #if c % 100000==0: print '\n\n\n%d = %d' % (c,a)
    return a
    
''' 
for v in range(9999):
    print v,fib(v)'''
    
print fib(99999)
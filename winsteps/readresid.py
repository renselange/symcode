
def parse(sym):
    s = sym.strip()
    igrade = s[1]
    itype  = ''
    icont  = ''
   
    for ci,c in enumerate(s[2:]):
        if c.isdigit():
            itype = c
            return ','.join([igrade,itype,icont])
        else: icont += c
    return '*,*,*'

fout = open('spssin.txt','w')
xname = []
freq  = [0]*900
max   = 0


vars ='igrade,itype,icode,ploc,school,student,sgrade,v2,sex,residual,count'
fout.write('%s\n'% vars)

with open('residuals.txt','r') as fin:
    for i,v in enumerate(fin): 
           
        if i % 100 == 0: print i   
        t = (v.strip()).split(',')
        loc = t[0]
        fld = ','.join(t[1][1:].split('|'))
        fields = t[2:]
    
        if i == 0: 
            pass
            # for j in range(10): print fields[j]
        elif i == 1:
            for fi,f in enumerate(fields):
                print f
                s = f.split('=')
                idnum = s[0]
                label = s[1]
                xname.append(parse(label))
        else:
            n = 0
            store = []
            for fi,f in enumerate(fields):
                if f != '.': 
                    n += 1
                    freq[fi] += 1
                    if fi > max: max = fi
                    st = '%s,%s,%s,%s' % (xname[fi],loc,fld,f)
                    store.append(st)
            for st in store:
                fout.write('%s,%d\n' % (st,n))
print '|'        
print xname

for i in range(max+1):
    print "%4d [%5d]: %s"%(i,freq[i],xname[i])

fout.close()        
  
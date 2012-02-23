d = {}
cats = {}

with open('studaggr.csv','r') as fin:
    for iv,v in enumerate(fin):
        if iv % 1000 == 0: print iv
        f = v.strip().split(',')
        stud = f[1]
        school = f[2]
        ploc = f[5]
        
        if not stud in d: t = {'CC':{}, 'EE':{},'F':{},'G':{},'MD':{},'NBT':{},'NF':{},'NS':{},'OA':{},'RP':{},'SP':{},'used':0, 'school':school,'ploc': ploc}
        else: t = d[stud]
        
        c = f[0]
        if not c in cats: cats[c]=1
        else: cats[c] += 1
    
        t[c]['m'] = f[3]
        t[c]['s'] = f[4]
        t[c]['n'] = f[6]
        t['used'] += 1
        d[stud] = t
        
vars = ['school','ploc','used','CC', 'EE','F','G','MD','NBT','NF','NS','OA','RP','SP']        
area = ['CC', 'EE','F','G','MD','NBT','NF','NS','OA','RP','SP']

studs= sorted(d,key=d.__getitem__)

freq =[0]*len(vars)

s = ['school','used','ploc']
for stat in ['m','s','n']: 
    for arx in area: 
        s.append('%s_%s'%(stat,arx))
print s

fout = open('byarea.csv','w')
fout.write(','.join(s)+'\n')

for iv,v in enumerate(studs):
    if True: # iv < 5: 
        case = d[v]
        collect = [case['school'],str(case['used']),case['ploc']]

        for stat in ['m','s','n']: 
            # collect.append('|')
            for arx in area: 
                t = case[arx]
                if stat in t: collect.append(t[stat])
                else: collect.append(' ')
            
        fout.write(','.join(collect) + '\n')
    else: break
    freq[d[v]['used']] += 1

fout.close()
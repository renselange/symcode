# the data is in Symphony format, a text file:
# EX:
#   93;"Math";-8.47;"01";[.00, .00];"[DB#  93 MKCC2e_1] ncats=2"
#

from item import Item

#
# labels look like: MKCC2e_1 => ['M','K','2','CC'], as from [M][K][CC][2]
#

def parselabel(sym):
    s = sym.strip()
    iarea  = s[0] # math vs reading
    
    igrade = s[1] # P=-1, K=0, 1, ...,8
    if igrade == 'K': igrade = 0
    elif igrade == 'P': igrade =-1
    else: igrade = int(igrade)
    
    itype  = ''   # 1 - 8, as in Monterey paper
    icont  = ''   # between grade and type

    for ci,c in enumerate(s[2:]):
        if c.isdigit():
            itype = c
            return [iarea,igrade,icont,itype]
        elif c == '_': break
        else: icont += c
    return ['*'] * 4
    

def loadfile(name):
    with open(name,'r') as fin:
        items = []
        for v in fin:
            f = v.strip().split(';')
            label   = parselabel(f[5].split(' ')[-2][:-1])
            sub     = label[2]   # f[5] looks like: '"[DB# 103 MKCC4m_1] ncats=2"'
            itemno  = int(f[0])
            iloc    = float(f[2])
            recode  = f[3]
            steps   = eval(f[4])
            #print itemno,sub
            items.append((label,Item(itemno,iloc,steps,cat=sub)))
        return items
        
def gradearea(name):
    table   = {}
    grades  = []
    areas   = []
    tt       = loadfile(name)
    for it in tt:
        flds = it[0]
        item = it[1]
        itgrade = flds[1]
        if not itgrade in grades: grades.append(itgrade)
        if not itgrade in table: table[itgrade] = {}
        area   = flds[2]
# for now ...
        if area[0] == 'K': area = 'K'
        
        if not area in areas: areas.append(area)
        if not area in table[itgrade]: table[itgrade][area] = [item]
        else: table[itgrade][area].append(item)
        
# we want a square table        
    for g in grades:
        t = table[g]
        for a in areas:
            if not a in t: t[a] = []
            
    grades.sort()
    areas.sort()   
    print 'Read from file: "%s" [%d items]' % (name,len(tt))
    print '\n     ',
    for a in areas: print '%-4s'%a,
    for g in grades:
        print '\n%2d'%g,
        for a in areas: print '%4d'%len(table[g][a]),
            
    return table,grades,areas
        
            
#print parsesymlabel('MKCC2e_1')
#print parsesymlabel('MKCCiie_1')
           
#loadfile('../data/itemdefs.txt')
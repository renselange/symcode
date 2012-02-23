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
    igrade = s[1] # P, K, 1, ...,8
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
            sub     = parselabel(f[5].split(' ')[-2][:-1])[2]   # f[5] looks like: '"[DB# 103 MKCC4m_1] ncats=2"'
            itemno  = int(f[0])
            iloc    = float(f[2])
            recode  = f[3]
            steps   = eval(f[4])
            #print itemno,sub
            items.append(Item(itemno,iloc,steps,cat=sub))
        return items
        
            
#print parsesymlabel('MKCC2e_1')
#print parsesymlabel('MKCCiie_1')
           
#loadfile('../data/itemdefs.txt')
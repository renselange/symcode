
from item import Item
from factor import Factor
from random import random
import loaditemdat

itembank = loaditemdat.loadfile('../data/itemdefs.txt')

class Multifactor:
    
    def __init__(self,facprob):  
    # facprob supposed to look like: {'Fluency':0.3,'Spatial':0.5,'Reasoning': 0.2} and a common factor '*' will always be pushed at start
        self.facprob = [('*',0.0,0,Factor())] + [(Name,Prob,0,Factor()) for Name,Prob in facprob.iteritems()]
    # so this will become to look like: [('*', 0.0, 0, <factor.Factor instance at 0x10377a6c8>), ..., ('Reasoning', 0.2, 0, <factor.Factor instance at 0x10377a710>)]
    # the first one is always '*', the order of the others is essentially random, depending on the hash function
    # the fields are: (<sub-area>,<desired-prop>,<actual-count>,<simple-factor>)
        self.comfac  = self.facprob[0][3] # quick reference to main factor
        self.count   = 0
    
        
    def randfac(self): # used to make the first choice
        r = random()
        c = 0.0
        for fi,f in enumerate(self.facprob[1:]): # skip the first
            c += f[1]
            if c > r: return fi+1,f
    # return index value, as well as factor itself
        return len(facprob)-1,self.facprob[-1]      # we might get to end due to accumulated rounding errors
        
    def needyfac(self):
        if self.count < 3: 
            at,fac  = self.randfac() # first few times around is random
        else:
            min = 2.0
            fac = None
            at  = -1
            for fi,f in enumerate(self.facprob[1:]):
                dif = float(f[2])/self.count - f[1] # observed - desired proportions
                if dif < min:
                    fac = f     # ptr to chosen factor
                    min = dif   # max negative difference
                    at  = fi+1  # index into list - was off by 1
                
    # the fields are: (<0=sub-area>,<1=desired-prop>,<2=actual-count>,<3=simple-factor>) 
        self.facprob[at] = (fac[0],fac[1],fac[2]+1,fac[3]) # increase count the hard way
        print at,self.facprob[at]
        return fac
        
    def addobs(self,item,obs=-1):
        #self.comfac.addobs(item,obs)
        self.count += 1
        
m = Multifactor({'Fluency':0.3,'Spatial':0.5,'Reasoning': 0.2})

print m.facprob
print m.comfac

frq = {'Fluency':0,'Spatial':0,'Reasoning': 0}

for i in range(40):
    f = m.needyfac()
    m.addobs(Item(0,0.0,[0.0,0.0],cat=f[0]))
    print m.facprob
    print
    frq[f[0]] += 1
    '''print
    for v in frq.keys(): print '(%s,%4.2f)'%(v,float(frq[v])/len(m.comfac.answered)),
    print'''
print;print    
print frq
        
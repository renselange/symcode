
from item import Item
from factor import Factor
from random import random
import loaditemdat

itembank = loaditemdat.loadfile('../data/itemdefs.txt')

class Multifactor:
    
    def __init__(self,facprob):  
    # facprob supposed to look like: {'Fluency':0.3,'Spatial':0.5,'Reasoning': 0.2}, and additional common factor '*' will always be pushed at start
    
        self.facprob = [('*',0.0,0,Factor())] + [(Name,Prob,0,Factor()) for Name,Prob in facprob.iteritems()]
        
    # so this will become to look like: [('*', 0.0, 0, <factor.Factor instance at 0x10377a6c8>), ..., ('Reasoning', 0.2, 0, <factor.Factor instance at 0x10377a710>)]
    # the first entry is always '*', the order of the others is essentially random, depending on the hash function
    # the fields are: (<0=sub-area>,<1=desired-prop>,<2=actual-count>,<3=simple-factor>) 
    
        self.comfac  = self.facprob[0][3] # quick reference to main factor
        self.count   = 0
    
    # randomly select one of the factor, regardless of anything ...   
    
    def randfac(self): # used to make the first choice
        r = random()
        c = 0.0
        for fi,f in enumerate(self.facprob[1:]): # skip the first
            c += f[1]
            if c > r: return fi+1,f # increase fi because first element was omitted
    # return index value, as well as factor itself
        return len(facprob)-1,self.facprob[-1]      # we might get here due to accumulated rounding errors
    
    # find the factor whose selection brings observed and wanted proportions max closer 
    # the sequence is deterministic, given the first few (3?) randomly selected items
    # EX: for six subfactors, this yields 3C6 possible orders = 120/6 = 20, good enough ...
      
    def needyfac(self):
        if self.count < 3: 
            at,fac  = self.randfac() # first few times around select at random
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
        self.facprob[at] = (fac[0],fac[1],fac[2]+1,fac[3]) # kludge to replace tuple, use lists?
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
    print f[0],
    m.addobs(Item(0,0.0,[0.0,0.0],cat=f[0]))
    frq[f[0]] += 1
    print frq
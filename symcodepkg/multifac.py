
from item import Item
from factor import Factor
from random import random
import math
import loaditemdat

itembank = loaditemdat.loadfile('../data/itemdefs.txt')


##########################################################################################################################

class Multifactor:
    
    def __init__(self,facprob):  
    # facprob supposed to look like: {'Fluency':0.3,'Spatial':0.5,'Reasoning': 0.2}, and additional common factor '*' will always be pushed at start
    
        self.facprob = {'*': (0.0,0,Factor())}
        for Name,Prob in facprob.iteritems(): self.facprob[Name] = (Prob,0,Factor())
    
    # randomly select one of the factor, regardless of anything ...   
    
    def xxxrandfac(self): # used to make the first choice
        r = random()
        c = 0.0
        t = ''
    # looks like: '*': (0.0, 0, <factor.Factor instance at 0x105526710>)
        for Name,Tup in self.facprob.iteritems():
            if Name == '*': continue    # Skip the "all" category ...
            t = Name
            c += Tup[0]
            if c > r: return t 
        return t     # we might get here due to accumulated rounding errors
    
    # find the factor whose selection brings observed and wanted proportions max closer 
    # also update the frequency with which factor now selected
    # the sequence is deterministic, given the first few (3?) randomly selected items
    # EX: for six subfactors, this yields 3C6 possible orders = 120/6 = 20, good enough ...
    
    def xxxupdatefreq(self,sub):
        for f in ['*',sub]:
            if sub == '': continue
            t = self.facprob[f]
            self.facprob[f] = (t[0],t[1]+1,t[2])    # prop-wanted, freq-used, factor
      
    def nextfac(self): # also UPDATE THE USAGE COUNTS
        
        if len(self.facprob) == 1: return ''
              
        n = self.facprob['*'][1]
        
        if n < 5: 
            sub  = self.xxxrandfac() # first few times around select at random
        else:    
            min = 2.0
            sub = ''
            
            for Name,Tup in self.facprob.iteritems():
                if Name == '*': continue
                dif = float(Tup[1])/n - Tup[0] # observed - desired proportion
                if dif < min:
                    sub = Name  # name of last min-est factor
                    min = dif   # max negative difference
                
        self.xxxupdatefreq(sub)
        return sub
        
    # sometimes we may want to just pick an area  
    def assignsub(self,sub):
        self.xxxupdatefreq(sub)
        return sub
        
    def addobs(self,item,obs=-1):
        t = item.cat
        # t = ''
    # add to general freq '*' and to the subfactor of the item (item.cat)
    # '*' and '' indicated "main" factor, but should not be doubled
        if t in ['*','']: vars = ['*']  # no subfactors are used if item.cat == ''
        else: vars = ['*',t]            # else use both
        
        for f in vars:
            self.facprob[f][2].addobs(item,obs)
    
    # when computing ploc for next CAT move, use only the '*' factor        
    def catest(self):
        f = self.facprob['*'][2]
        return f.rawtorasch(f.rawsum)
        
    def allest(self):
        out = {}
        for k,f in self.facprob.iteritems():
            fac     = f[2]
            if len(fac.answered) < 1: continue
            est     = fac.rawtorasch(fac.rawsum)
            ploc    = est[0]    # keep only the person estimate
            pse     = est[1]
            m,var,n = fac.resid(ploc)
            #print m,var,n
            out[k] = (ploc,pse,m,var,n) # math.sqrt(var))
        return out
            
            
##########################################################################################################################
#
# To create a new Multifactor:              M = Multifactor({'Fluency':0.3,'Spatial':0.5,'Reasoning': 0.2})
# To use an item from a particular area:    M.assignsub('Fluency')  => 'Fluency'    (will update factor freq of 'Fluency')
# To have next factor computed:             M.nextfac()             => 'Spatial'    (will update factor freq of 'Spatial')
#
##########################################################################################################################
        
m = Multifactor({'Fluency':0.3,'Spatial':0.5,'Reasoning': 0.2})

frq = {'Fluency':0,'Spatial':0,'Reasoning': 0}

print m.facprob

for i in range(40):
    f = m.nextfac()
    it = Item(0,0.0,[0.0,0.0],cat=f)
    print '>%s<'%f,
    m.addobs(it,it.randval(0.0))
    print m.allest()
    
#for n,e in m.facprob.iteritems():
#    print n,len(e[2].answered)   
#print m.facprob
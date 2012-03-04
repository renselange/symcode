
from item import Item
from factor import Factor
from random import random 
from random import gauss
import math
import loaditemdat

# itembank = loaditemdat.loadfile('../data/itemdefs.txt')


##########################################################################################################################

class Multifactor:
    
    def __init__(self,grade,facprob):  
    # facprob supposed to look like: {'Fluency':0.3,'Spatial':0.5,'Reasoning': 0.2}, an additional common factor '*' will always be added
    
        self.facprob = {'*': (0.0,0,Factor())}
        for Name,Prob in facprob.iteritems(): self.facprob[Name] = (Prob,0,Factor(),grade) # for each factor, store <selection-prob>,<n-chosen>,<factor>,<current-grade>
    
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
      
    def xnextcat(self): # also UPDATE THE USAGE COUNTS
        
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
            #print f,
            self.facprob[f][2].addobs(item,obs)
    
    # when computing ploc for next CAT move, use only the '*' factor        
    def facest(self):
        f = self.facprob['*'][2]
        return f.rawtorasch(f.rawsum)
    
    # estimate person locs on all factors, incl '*' etc    
    def allest(self):
        t       = self.facprob['*'][2]
        rasch   = t.rawtorasch(t.rawsum)
        ploc    = rasch[0]
        fit     = t.resid(ploc)

        out = {'*':{'est':rasch,'fit':fit}}
        
        for k,f in self.facprob.iteritems():# iterate through dict
            if k == '*': continue
            fac     = self.facprob[k][2]    # dig out factor from dict item
            if len(fac.answered) > 0:       # check if this subfactor was used at all
                t = fac.rawtorasch(fac.rawsum)  # get person estimate (<loc>,<se>,<niter>)
                fit = fac.resid(ploc)           # compute fit stuff
                out[k] = {'est':t, 'fit':fit}   # didn't work using tuples => Python bug?
            
        return out
'''        
    def fsm(self):
        cond = None
        while True:
            c = (yield cond)
            if c == 1: state = 1
            else: state = 2
            # print v
            cond = state
        
    def def_fsm(self,tuple):    # (<current_state>,<condition>,<new_state>)
        self.storefsm[tuple[0]] = (tuple[1],tuple[2])
        
    def run_fsm(self,old_state,condition):
        t = self.storefsm[old_state]
        return
        
        
m = Multifactor({})       

f = m.fsm()
f.next()
print f
print f.send(3<8)
print f.send(28)
'''
            
##########################################################################################################################
#
# To create a new Multifactor:              M = Multifactor({'Fluency':0.3,'Spatial':0.5,'Reasoning': 0.2})
# To find the area most in need of items:   M.nextfac()             => 'Spatial'    (will update factor freq of 'Spatial')
# To compute the overall Rasch location:    M.facest()              => (1.2, 0.4)   (Use this to select next item, as before)
# When all done:                            M.allest()              => all factor estimates + fit (See simulation)
##########################################################################################################################

##################################################### begin of simulation code ##########################################
'''def boundgauss(m,sd,wide):
    while True:
        t = gauss(m,sd)
        if t < m-wide: continue
        if t > m+wide: continue
        return t
        
def simulate(pm,psd,pn,im,isd,itn,sub):
    names= sub.keys() 
    names= sorted(names)
    names= ',id'.join(['idall']+names)+',  '+',se'.join(['seall']+names)+',  '+',z'.join(['zall']+names)+',  '+',zz'.join(['zzall']+names)
    print names
    
    keys = sub.keys() + ['*']
    keys = sorted(keys)
    
    # its = [boundgauss(im,isd,2.5) for i in xrange(itn)] # keep same set of items across people
    fout = open('simout.txt','w')
    fout.write('trueloc,facrasch,facse,'+names+'\n')

    
    for p in xrange(pn):
        if p % 100 == 0: print 'PERS:',p
        m = Multifactor(sub)
        fac1 = Factor()
        ploc = boundgauss(pm,psd,2.5)
        its  = [boundgauss(im,isd,2.5) for i in xrange(itn)] # refresh set of items across people
        
        for i in its:
            cat     = m.nextcat()
            it      = Item('',i,[0.0,0.0],cat=cat)
            obs     = it.randval(ploc)
            m.addobs(it,obs)
            fac1.addobs(it,obs)
 
        #print '%6.3f' % (ploc),
        allv = m.allest() 
        est1 = fac1.rawtorasch(fac1.rawsum) # for control vs '*'
        
        line = ','.join([
                    '%6.3f'%ploc,
                    ','.join(['%6.3f'%est1[k] for k in range(2)]),  
                    ','.join(['%6.3f'%allv[k]['est'][0] for k in keys]),
                    ','.join(['%6.3f'%allv[k]['est'][1] for k in keys]),
                    ','.join(['%6.3f'%allv[k]['fit'][0] for k in keys]),
                    ','.join(['%6.3f'%allv[k]['fit'][1] for k in keys])
                    ])
        fout.write(line+'\n')
        
    fout.close()
            
simulate(0.5,1.5,10000, 0.0,1.0,25, {'1':0.2,'2':0.2,'3':0.2, '4':0.4})''

    
''' 

####################################################### TEST CODE #######################################
'''       
mult = Multifactor({'Fluency':0.3,'Spatial':0.5,'Reasoning': 0.2})

items = [
    Item(0, -1.5,[0.0,0.0],cat='Fluency'),
    Item(1, -1.5,[0.0,0.0],cat='Spatial'),
    Item(2, -1.5,[0.0,0.0],cat='Reasoning'),
    Item(3, -1.0,[0.0,0.0],cat='Fluency'),
    Item(4, -1.0,[0.0,0.0],cat='Spatial'),
    Item(5, -1.0,[0.0,0.0],cat='Reasoning'),
    Item(6, -0.5,[0.0,0.0,0.0],cat='Fluency'),
    Item(7, -0.5,[0.0,0.0,0.0],cat='Spatial'),
    Item(8, -0.5,[0.0,0.0,0.0],cat='Reasoning'),
    Item(9,  1.5,[0.0,0.0,0.0],cat='Fluency'),
    Item(10, 1.5,[0.0,0.0,0.0],cat='Spatial'),
    Item(11, 1.5,[0.0,0.0,0.0],cat='Reasoning'),
    Item(12, 2.5,[0.0,0.0],cat='Fluency'),
    Item(13, 2.5,[0.0,0.0],cat='Spatial'),
    Item(14, 2.5,[0.0,0.0],cat='Reasoning')
    ]
obs = [
    0,1,0,1,0,1,
    0,1,2,2,1,0,
    0,1,0
    ]
  
for it,v in zip(items,obs): # makes effectively an array with two columns: items and observations
    mult.addobs(it,v)       # and adds them to the multifactor, i.e., it = item and v= observation
    allest = mult.allest()
    
    print 'Added:',it.cat
    for f in ['*','Fluency','Spatial','Reasoning']: 
        if f in allest:
            print f,allest[f]
            
mult = Multifactor({'Fluency':0.3,'Spatial':0.5,'Reasoning': 0.2}) 
freq = {'*':0,'Fluency':0,'Spatial':0,'Reasoning':0}

print
print 'Item type ordering:'
for v in range(15):
    print v,mult.nextcat()
print
print 'Category frequencies'    
for f in ['*','Fluency','Spatial','Reasoning']: 
    print f,mult.facprob[f][1]
    
#################################################### PRODUCESS ##########################################

Added: Fluency
* {'est': (-2.3472978603872034, -1.0, 0), 'fit': (-0.6546536707079772, 0.0, 0)}
Fluency {'est': (-2.3472978603872034, -1.0, 0), 'fit': (-0.6546536707079772, 0.0, 0)}
Added: Spatial
* {'est': (-1.5, -1.0, 0), 'fit': (0.0, 2.0, 1)}
Fluency {'est': (-2.3472978603872034, -1.0, 0), 'fit': (-1.0, 0.0, 0)}
Spatial {'est': (-0.6527021396127966, -1.0, 0), 'fit': (1.0, 0.0, 0)}
Added: Reasoning
* {'est': (-2.1931471805599454, -1.0, 0), 'fit': (7.401486830834377e-17, 1.5000000000000002, 2)}
Fluency {'est': (-2.3472978603872034, -1.0, 0), 'fit': (-0.7071067811865475, 0.0, 0)}
Spatial {'est': (-0.6527021396127966, -1.0, 0), 'fit': (1.4142135623730951, 0.0, 0)}
Reasoning {'est': (-2.3472978603872034, -1.0, 0), 'fit': (-0.7071067811865475, 0.0, 0)}
Added: Fluency
* {'est': (-1.375972715316746, 1.0058047410175568, 1), 'fit': (0.004683349143067395, 1.5345896384267226, 3)}
Fluency {'est': (-1.25, -1.0, 0), 'fit': (0.07142009583098874, 2.578252493552497, 1)}
Spatial {'est': (-0.6527021396127966, -1.0, 0), 'fit': (0.93987006467512, 0.0, 0)}
Reasoning {'est': (-2.3472978603872034, -1.0, 0), 'fit': (-1.0639768597648278, 0.0, 0)}
Added: Spatial
* {'est': (-1.711917386768383, 0.9187280074888532, 1), 'fit': (0.007979874930325726, 1.3455969536230197, 4)}
Fluency {'est': (-1.25, -1.0, 0), 'fit': (0.2640433894067939, 2.707488656354338, 1)}
Spatial {'est': (-1.25, -1.0, 0), 'fit': (0.2056371984348389, 1.6421748809030685, 1)}
Reasoning {'est': (-2.3472978603872034, -1.0, 0), 'fit': (-0.899461801031637, 0.0, 0)}
Added: Reasoning
* {'est': (-1.2499999999999998, 0.8228837706261181, 1), 'fit': (-1.1102230246251565e-16, 1.3387406465787552, 5)}
Fluency {'est': (-1.25, -1.0, 0), 'fit': (-1.1102230246251565e-16, 2.5680508333754837, 1)}
Spatial {'est': (-1.25, -1.0, 0), 'fit': (-1.1102230246251565e-16, 1.5576015661428095, 1)}
Reasoning {'est': (-1.25, -1.0, 0), 'fit': (-1.1102230246251565e-16, 2.5680508333754837, 1)}
Added: Fluency
* {'est': (-1.5306784923986916, 0.7323504534150596, 2), 'fit': (0.035187793986308794, 1.226755793130748, 6)}
Fluency {'est': (-2.09861228866811, -1.0, 0), 'fit': (-0.10709754998607197, 1.522779985899762, 2)}
Spatial {'est': (-1.25, -1.0, 0), 'fit': (0.12425588693437412, 1.5884806170185057, 1)}
Reasoning {'est': (-1.25, -1.0, 0), 'fit': (0.15954771699681464, 2.618961781373274, 1)}
Added: Spatial
* {'est': (-1.283598454976864, 0.6349422267162452, 2), 'fit': (0.004451588184880173, 1.099989056931889, 7)}
Fluency {'est': (-2.09861228866811, -1.0, 0), 'fit': (-0.23472495773703408, 1.477573083465155, 2)}
Spatial {'est': (-1.0, -1.0, 0), 'fit': (0.23390458354615687, 0.9230069174841016, 2)}
Reasoning {'est': (-1.25, -1.0, 0), 'fit': (0.019036914025836515, 2.5687756415667367, 1)}
Added: Reasoning
* {'est': (-0.8189554518673852, 0.5491548845035228, 2), 'fit': (-0.06443527836667025, 1.3311934195651534, 8)}
Fluency {'est': (-2.09861228866811, -1.0, 0), 'fit': (-0.4951790210849712, 1.5306978910598643, 2)}
Spatial {'est': (-1.0, -1.0, 0), 'fit': (-0.040239644724571054, 0.8843362876568206, 2)}
Reasoning {'est': (0.09861228866810978, -1.0, 0), 'fit': (0.3421128307095316, 2.3826290511863064, 2)}
Added: Fluency
* {'est': (-0.2676802812129747, 0.5476407965990759, 2), 'fit': (0.02244503750774447, 3.2775160116413993, 9)}
Fluency {'est': (-0.1008213835160197, 0.9043330846913478, 2), 'fit': (0.3562077219962758, 7.191099341334607, 3)}
Spatial {'est': (-1.0, -1.0, 0), 'fit': (-0.36423728351254553, 1.0049071620834096, 2)}
Reasoning {'est': (0.09861228866810978, -1.0, 0), 'fit': (-0.03588955412334075, 2.505081606231387, 2)}
Added: Spatial
* {'est': (-0.03377975591750617, 0.5441999370312599, 2), 'fit': (-0.026782244749040594, 3.019021655324818, 10)}
Fluency {'est': (-0.1008213835160197, 0.9043330846913478, 2), 'fit': (0.07717384197688104, 6.475901595647529, 3)}
Spatial {'est': (-0.1008213835160197, 0.9043330846913478, 2), 'fit': (-0.010647189492210773, 1.7385385366777701, 3)}
Reasoning {'est': (0.09861228866810978, -1.0, 0), 'fit': (-0.18690376739270945, 2.712855309164534, 2)}
Added: Reasoning
* {'est': (-0.1008213835160198, 0.5221169498836343, 2), 'fit': (-0.008142461360690662, 2.8075222170684677, 11)}
Fluency {'est': (-0.1008213835160197, 0.9043330846913478, 2), 'fit': (0.15686727768655384, 6.646261254186314, 3)}
Spatial {'est': (-0.1008213835160197, 0.9043330846913478, 2), 'fit': (0.04255034462731133, 1.7584141827310955, 3)}
Reasoning {'est': (-0.1008213835160197, 0.9043330846913478, 2), 'fit': (-0.22384500639593716, 1.7878052756748908, 3)}
Added: Fluency
* {'est': (-0.11931609698435183, 0.5170954038388416, 2), 'fit': (-0.013878256608392913, 2.592902429629809, 12)}
Fluency {'est': (-0.1543929140892489, 0.8796069461676527, 2), 'fit': (0.08912213186621812, 5.063801269215888, 4)}
Spatial {'est': (-0.1008213835160197, 0.9043330846913478, 2), 'fit': (0.0572491664962439, 1.7650307946392498, 3)}
Reasoning {'est': (-0.1008213835160197, 0.9043330846913478, 2), 'fit': (-0.2137561653062935, 1.7771483799449996, 3)}
Added: Spatial
* {'est': (0.12942343691353672, 0.5207591346547611, 2), 'fit': (0.03848379135100899, 3.1489798970388514, 13)}
Fluency {'est': (-0.1543929140892489, 0.8796069461676527, 2), 'fit': (-0.15442521831924072, 4.63475969932227, 4)}
Spatial {'est': (0.6518204097501424, 0.9143534420176621, 2), 'fit': (0.5423562908733107, 3.61522344525538, 4)}
Reasoning {'est': (-0.1008213835160197, 0.9043330846913478, 2), 'fit': (-0.35022057096405584, 1.9589782830431257, 3)}
Added: Reasoning
* {'est': (0.10676060983862173, 0.5146075169790562, 1), 'fit': (0.03380101243076362, 2.9458569360456535, 14)}
Fluency {'est': (-0.1543929140892489, 0.8796069461676527, 2), 'fit': (-0.1321961315741854, 4.6617572696804155, 4)}
Spatial {'est': (0.6518204097501424, 0.9143534420176621, 2), 'fit': (0.5641865534616353, 3.6422851178408187, 4)}
Reasoning {'est': (-0.1543929140892489, 0.8796069461676527, 2), 'fit': (-0.3305873845951591, 1.454403416339136, 4)}

Item type ordering:
0 Fluency
1 Fluency
2 Reasoning
3 Spatial
4 Spatial
5 Spatial
6 Reasoning
7 Spatial
8 Fluency
9 Spatial
10 Spatial
11 Fluency
12 Reasoning
13 Spatial
14 Fluency

Category frequencies
* 15
Fluency 5
Spatial 7
Reasoning 3
'''
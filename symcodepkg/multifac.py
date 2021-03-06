
from item import Item
from factor import Factor
from random import random 
from random import gauss
from random import choice
from random import uniform
import math
import loaditemdat
import copy
import operator

# itembank = loaditemdat.loadfile('../data/itemdefs.txt')


##########################################################################################################################

class Multifactor:
    
    ############################################## reset the item store ##################################################    
    #
    def reset_items(self):   
             
        self.table,self.grades,self.areas = copy.deepcopy(self.itemstore)
        self.useditems = []
        
    # facprob supposed to look like: {'Fluency':0.3,'Spatial':0.5,'Reasoning': 0.2}, an additional common factor '*' will always be added
    
        self.faclist    = {'*': {'prob':-1.1,'nused':0,'fac':Factor(),'curgrade':self.studgrade,'floc':0.0,'fse':0.0}}
        for Name,Prob in self.facprob.iteritems(): self.faclist[Name] = {'prob':Prob,'nused':0,'fac':Factor(),'curgrade':self.studgrade,'floc':0.0,'fse':0.0}
    
    #################
    #
    def colnames(self):
        locs = ''
        ses  = ''
        fits = ''
        lfits= ''
        lens = ''
        for v in self.facorder:
            locs += ',%s_loc' % v
            ses  += ',%s_se'  % v
            fits += ',%s_fit' % v
            lfits+= ',%s_log' % v
            lens += ',%s_n'   % v
            
        locs += ',loc_mean,loc_sd'      # variance of fac estimates
        lens += ',n_range'      # range of items per fac
        
        return ','.join(['cond','pid','phase','ploc','ndone','itid','itcat','itloc','obs','est_all','se_all']) + locs + ses + fits + lfits + lens
        #record += '\n%5d,%d,%6.2f,%2d,%4d,%4s,%6.2f,%d,%6.2f,%6.2f%s'%(pid,phase,ploc,len(self.useditems),it.itid,it.cat,it.loc,####,obs,estloc,estse,self.str_allest(allest),####)  
        
    def nofacs(self):
        return ','*( len(self.facorder)*5  + 3)
        
    ###############################################  constructor  #######################################################    
    def __init__(self,grade,facprob,condition,itemfile): 
        
        self.studgrade  = grade
        self.condition  = condition
        self.facprob    = facprob
        self.facorder   = facprob.keys()
        self.facorder.sort()                                # order of results   
        self.maxrun     = 0    
        
        self.itemstore  = loaditemdat.gradearea(itemfile)    # store the original list with all items. Within cells, items are sorted by loc
        
        self.reset_items()                                  # must be called whenever simulating a new person
        
        
    ######################################## Really should be a separate method  ########################################
        better = False
        self.fatal  = False
        
        print; print
        print 'Usage and priority:',facprob
        print 'Student grade',self.studgrade
        print
        for a in self.areas:
            if not a in facprob: print 'WARNING: Sub-area occurs in Item DB, but will not be used:',a ; better = True
            
        tot = 0.0
        for a in facprob: 
            if not a in self.areas: print 'FATAL: Sub-area was specified, but does not occur in Item DB:',a ; better = True; self.fatal = True
            else: tot += self.faclist[a]['prob'] # facprob[a]
        if better: print '***** Better make sure!'
        
        if len(self.faclist) == 1: tot = 1.0
        print tot
        
        if abs(tot-1.0) > 0.01:
            print 'FATAL: Selection probabilities of retained sub-areas do not sum to 1.0, but to %6.4f instead'%tot
            print facprob
            self.fatal = True
        if self.fatal: print '*** FATAL errors discovered, program exits'
        
    ############################################### sort area / factor by being most in need ###########################################
    # also works if no sub-areas were specified: {}
    # if no items were yet selected, then pick one area at random
    
    def factorpriority(self):
    
    # no sub-areas => use only '*'
        if len(self.faclist) == 1:
            return ('*',['*'],[('*',1.1)])          # if there are no sub-areas, we're done
            
    # there are sub-areas
        totdone = len(self.useditems)               # total used
        facpdone = {}
    
    # looks like: {'*': {'prob':-1.1,'nused':0,'fac':Factor(),'curgrade':grade,'floc':0.0,'fse':0.0}, 'FF': {...}, ...}
        
        for key,fac in self.faclist.iteritems():    # include '*' 
            facdone = fac['nused']
            
            if totdone == 0: pdone = uniform(-0.001,0.001)
            else: pdone   = facdone / float(totdone) + uniform(-0.001,0.001) # add small perturbation
            
            # will be smallest (and negative) for most needy factor
            facpdone[key] = pdone - fac['prob'] # for '*', fac['prob] = 0.0
            
    # we now know which proportion of items each factor received. 
    # now sort factors by above proportion to get priority queue
    # see: http://stackoverflow.com/questions/613183/python-sort-a-dictionary-by-value
    # the small perturbation causes random ordering of identical values
    # we now get areas / factors in order of neediness. this is done so that we always know which one to pick when a sub=area is exhausted
    # the last element is always '*' - so we can pick any item, if need be ...

        return sorted(facpdone.iteritems(),key=operator.itemgetter(1)) # result looks like: [('F',-0.333),('HH',0.222), ..., ('*',1.1)]
    
    
    ######################################################################################################
    # Little helper that returns a list of range of item locs by grade
    # It also return the first grade that has items ... (favoring strongly ['curgrade'] )
    # The search starts at current grade, and goes down
    # If no items are found that way, then the search only 1 higher grade
    
    def start_grade(self,subfac):
        
        t = [(False,0,0)]*10                            # since the last element is -1, this covers grades 0=KG,1,...,8,-1=PK
        
        for g in range(-1,9):                           # we are looking at the table column with subfac as label
            f = self.table[g][subfac]
            if len(f) > 0: t[g] = (True,f[0].loc,f[-1].loc)     # True means that there were items left for this grade, False = no
            
        # t looks like: [(True, -9.59, -0.98), (True, -9.66, 0.24), ..., (True, -6.83, -2.03)], ignore when False ...
        
        curgrade = self.faclist[subfac]['curgrade']     # just easier to look at later
        
        for g in range(curgrade,-2,-1):                 # starting at current grade, if need be go down to -1 to find a valid range
            if t[g][0]: return g,t                      # t[g] will look like: (True, ...,...)
            
        for g in range(curgrade+1,curgrade+2):          # nothing was found at or below, now try higher if need be
            if t[g][0]: return g,t
        
        return curgrade,t                               # t[curgrade] will look like (False,..,..)
        
    
    ####################################################################################################
    # Starting at grade, we look for a grade (maybe this one) with items whose locations include wanted_loc
    # If there are any items to be had, the closest grade will be selected
    # Search does not go over current grade + 1
        
    def next_grade(self,start_grade,occur_list,wanted_loc):
        
        minv    = 100000.0      # as a last ditch effort, also find grade closest to wanted_loc
        at      = 99            # best grade
    
    # go down from current grade    
    
        for g in range(start_grade,-2,-1):
            t = occur_list[g]
            if t[0]:
                d = min(abs(wanted_loc - t[1]), abs(wanted_loc - t[2])) # closest to lowest or highest val
                if d < minv:
                    d = minv
                    at = g
                if t[1] <= wanted_loc <= t[2]: return True,g    # returns (True,grade)
    
    # check next grade up - keep "range" for easy changes later
    
        for g in range(start_grade+1,start_grade+2):    # go up at most one grade
            t = occur_list[g]
            if t[0]:
                d = min(abs(wanted_loc - t[1]), abs(wanted_loc - t[2]))
                if d < minv:
                    d = minv
                    at = g
                if t[1] <= wanted_loc <= t[2]: return True,g
                
    # return closest, if something (anything!) was found (iff "at" was changed)
        if at != 99: return True,at
             
     # sorry, nothing found           
        return False,0
        
    ##################################################################################################################
    # within table[grade][subfac] identify the item closest to wanted_loc, and remove this item from table cell
    # also, update grade info
    
    def get_and_remove_item(self,grade,subfac,wanted_loc):
        
        t = self.table[grade][subfac]   # this is a sorted list of items in cell [grade][subfac] (by loc)
        at   = 0
        
        if len(t) > 1:          # at stays 0 if there is only one item in the list
            minv = 10000.0      # will always be undercut
            
            for iv,item in enumerate(t): 
                d = abs(item.loc - wanted_loc)
                if d < minv: 
                    minv = d
                    at = iv
                else: break     # remember: the items are sorted low->high by their locations
                
        self.faclist[subfac]['curgrade'] = grade    # to avoid big jumps, start from this grade the next time    
        
        fac_it  = t.pop(at)     # remove item "at" from list, and return this item later
        # print fac_it.itid
        
        if subfac == '*': return fac_it # potential error: returning does not remove item from subfactor ....
        
        itid    = fac_it.itid       # also remove from '*'
        t       = self.table[grade]['*']
        at      = -1
        
        for iv,i in enumerate(t):   # find item with same DB id = not very efficient ....
            if i.itid == itid:
                at = iv
                break
                
        if at == -1: return fac_it # Not found: it was already removed from '*'
                
        return t.pop(at)
              
            
    #################################################################################################################
    # get the next item to be administered, given the location being wanted
    
    def nextitem(self,wanted_loc):
        for p,wanted in enumerate(self.factorpriority()):       # go through sub-areas [factors] in order of their priority, see above
        
            subfac          = wanted[0]                         # name of next sub-area (e.g., 'F')
            
        # find starting grade for this sub-factor to start looking
            grade,occurs    = self.start_grade(subfac)          # get grade and list of item loc range by grade: 6, [(True, -9.59, -0.98), (True, -9.66, 0.24), ..., (True, -6.83, -2.03)] 
            if not occurs[grade][0]: continue                   # check if a starting grade was identified ... (strongly favors 'curgrade')
            
            #print subfac,grade,occurs,self.next_grade(grade,occurs,0.0)
            
            found,grade = self.next_grade(grade,occurs,wanted_loc)      # given a start grade, find the optimal grade
            if not found: continue                                      # nothing found, go to next factor
            # print grade
            return self.get_and_remove_item(grade,subfac,wanted_loc)    # done   
                

    #################################################################################################################
    # when computing ploc for next CAT move, use only the '*' factor 
           
    def facest(self):
        f = self.faclist['*']['fac']
        return f.rawtorasch(f.rawsum)
        
        
    ####################################### compute m, sd, max, and min for a list of numbers ##########################    
    def m_sd(self,x):
        sx,sxx = 0.0, 0.0
        minv, maxv = x[0],x[0]

        for v in x:
            sx += v
            sxx+= v * v
            if v > maxv: maxv = v
            elif v < minv : minv = v
            
        n = len(x)
        
        if n < 2: return 0.0,-1.0,0.0,0.0
        
        sxx = math.sqrt((sxx - sx*sx/n)/(n-1))
        
        return sx / n, sxx,minv,maxv
        
    
    ##################################################################################################################
    # estimate person locs on all factors, incl '*' etc    
    
    def allest(self):
        t       = self.faclist['*']['fac']
        rasch   = t.rawtorasch(t.rawsum)
        ploc    = rasch[0]
        fit     = t.resid(ploc)

        out = {'*':{'est':rasch,'fit':fit}}
        
        for k,f in self.faclist.iteritems():    # iterate through dict
            if k == '*': continue
            fac = f['fac']                      # dig out factor from dict item
            if len(fac.answered) > 0:           # check if this subfactor was used at all
                t = fac.rawtorasch(fac.rawsum)  # get person estimate (<loc>,<se>,<niter>)
                fit = fac.resid(ploc)           # compute fit stuff - relative to OVERALL Rasch person estimate - NOT factor specific
                out[k] = {'est':t, 'fit':fit}   # didn't work using tuples => Python bug?
            else: out[k] = {'est': (-9.0,-9.0,0), 'fit': (-9.0,-9.0,0)}
            
        return out
        
    ################################################### MAKE OUTPUT REC FROM SIMULATION RESULTS #######################
        
    def str_allest(self,allest):
        locstr = ''
        sestr  = ''
        fitstr = ''
        lfitstr= ''
        lenstr = ''
        lenv   = []
        locv   = []
        for v in self.facorder:
            lenstr += ',%2d' % self.faclist[v]['nused']
            lenv.append(self.faclist[v]['nused'])
            t = allest[v]['est']
            locstr += ',%6.2f' % (t[0])
            locv.append(t[0])
            sestr  += ',%6.2f' % (t[1])
            t = allest[v]['fit']
            fitstr += ',%6.2f' % (t[0])
            lfitstr+= ',%6.2f' % (t[1])
            
        lenstats = self.m_sd(lenv)  # m, sd, min, max
        lenstr   += ',%2d' % (lenstats[3]-lenstats[2])
        locstats = self.m_sd(locv)
        locstr   += ',%6.2f,%6.2f' % (locstats[0],locstats[1])
        
        return locstr+sestr+fitstr+lfitstr+lenstr
            
        
    
    ################################################################################################################
    # add item to to general freq '*' and to the subfactor of the item (item.cat)
    
    def addobs(self,item,obs=-1):
        
        t = item.cat
        
        # '*' and '' indicated "main" factor, but should not be doubled
        
        if t in ['*','']: vars = ['*']  # no subfactors are used if item.cat == ''
        else: vars = ['*',t]            # else use both

        for f in vars: 
            if f == 'PK': print 'Seeing f ==',f
            self.faclist[f]['fac'].addobs(item,obs)
            self.faclist[f]['nused'] += 1
        
        
    ###############################################################################################################
    # Simulate a single person taking a test
    # Return a list of strings representing the simulation results
    #
        
    def one_sim(self,pid,ploc):        
        self.reset_items()
        grade = max(self.studgrade - 3,-1)  # don't go below -1   
        record = ''
   
             
    ######################### Phase 1: "administer" three bootstrap items #################
        phase = 1
        for v in range(3):
            plist = self.factorpriority()   # this will randomly reshuffle the order of the sub-factors
            
            for p in plist:                 # p looks like: ('F', -0.2)
                subfac = p[0]
                t = self.table[grade][subfac]
                
                if len(t) > 0:              # is there an item of this type? Note: There is always '*' as a last resort
                    low     = t[0].loc      # lowest loc
                    high    = t[-1].loc     # highest loc
                    it = self.get_and_remove_item(grade,subfac,(low+high)/2.0)  # approximate "average" item
                    self.useditems.append(it)
                    
                    obs = it.randval(ploc)              # get an "empirical observation" (at least, a simulated one)
                    self.addobs(it,obs)                 # add to factor for later estimation
                    correct = (obs == len(it.steps)-1)  # correct iff highest response category was reached
                    
                    record += '\n%2d,%5d,%d,%6.2f,%2d,%4d,%4s,%6.2f,%d,,%s'%(self.condition,pid,phase,ploc,len(self.useditems),it.itid,it.cat,it.loc,obs,self.nofacs())  
                    #outside, glue person-id and person-loc to front
                    
                    
                    #print grade,it.steps,obs,correct,
                    if correct and grade <= self.studgrade: grade += 1 # no more than up to 1 higher
                    #print grade
                    break
                                
    ############################# Phase 2: One factor CAT for nfac x 4 items (but < 20), need based by cat freq ###############  
         
        phase = 2
                
        # reset ALL factor grades to the actual studend grade
        for _,f in self.faclist.iteritems(): f['curgrade'] = self.studgrade
    
        estloc,estse,_ = self.facest() # get an estimate based on all 3 items thus far ...
        
        niter2 = min(20,len(self.facprob)*4)    # no more than 20, if that ..
        
        while len(self.useditems) < niter2: 
            estloc = estloc - 0.7 + uniform(-0.2,0.2)   # to achieve p-correct = 0.67
            it = self.nextitem(estloc)
            obs = it.randval(ploc)
            self.addobs(it,obs)
            self.useditems.append(it)
            
            estloc,estse,_ = self.facest()
            record += '\n%2d,%5d,%d,%6.2f,%2d,%4d,%4s,%6.2f,%d,%6.2f,%6.2f%s'%(self.condition,pid,phase,ploc,len(self.useditems),it.itid,it.cat,it.loc,obs,estloc,estse,self.nofacs()) 

    ########################## Phase 3: Need based by SE ######################################################################
    
        phase = 3
                
        # reset ALL factor grades to the actual studend grade
        # for _,f in self.faclist.iteritems(): f['curgrade'] = self.studgrade
        
        while len(self.useditems) < 100: # 35:
            allest = self.allest()
            priority = sorted([(k,defn['est'][1]) for k,defn in allest.iteritems()],key=lambda x: -x[1]) # list of subfactors, largest SE first
            #print priority
            
            for facname,se in priority: # looks like: [('F',1.09),('DD',1.01), ...,('*',0.8)]
                grade = self.faclist[facname]['curgrade']
                wanted_loc = allest[facname]['est'][0]
                wanted_loc = wanted_loc - 0.7 + uniform(-0.2,0.2)   # to achieve p-correct = 0.67
                
                if len(self.table[grade][facname]) > 1:
                    g,occurs = self.start_grade(facname)
                    if not occurs[g][0]: continue
                    
                    found,gg = self.next_grade(g,occurs,wanted_loc)             # given start grade g, find the optimal grade gg
                    if not found: continue                                      # nothing found, go to next factor
                    it = self.get_and_remove_item(gg,facname,wanted_loc)        # done
                    #print it.show()
                    obs = it.randval(ploc)
                    self.addobs(it,obs)
                    self.useditems.append(it)
                    allest = self.allest()
                    #print allest
                    estloc = allest['*']['est'][0]
                    estse  = allest['*']['est'][1]
                    lastadd = '%2d,%5d,%d,%6.2f,%2d,%4d,%4s,%6.2f,%d,%6.2f,%6.2f%s'%(self.condition,pid,phase,ploc,len(self.useditems),it.itid,it.cat,it.loc,obs,estloc,estse,self.str_allest(allest)) 
                    record += '\n'+lastadd 
                    if estse < 0.5: 
                        if len(self.useditems) > self.maxrun: 
                            self.maxrun = len(self.useditems)
                            print 'new maxrun:',self.maxrun
                        return '\n1,'+lastadd # COMMENT OUT????
                    break
        return '\n0,'+lastadd
        # return '%s'%(record[1:]+'\n')n # KEEP KEEP
        
'''   Grad ScSc Logit
        0   406 -5.53
        1   517 -3.83
        2   615 -2.32
        3   678 -1.35
        4   740 -0.40
        5   786  0.31
        6   813  0.72
        7   853  1.34
        8   895  1.98   
''' 


def runsim(grade,condition):
    foutname = '/Users/renselange/symphony/symresults/grade%d.txt' % (grade)
    defsname = '/Users/renselange/symphony/symcode/data/itemdefs.txt'
    
    mean     =  [-5.53,-3.83,-2.32,-1.35,-0.40, 0.31,0.72,1.34,1.98]
    
    facset   =  {
                0 : {'CC':0.25,'G':0.25,'MD':0.25,'OA':0.25},
                4 : {'MD':0.25,'NBT':0.25,'NF':0.25,'OA':0.25},
                8 : {'EE':0.33333,'G':0.33333,'SP':0.33333}
                }
          
    m = Multifactor(grade,facset[grade],condition,defsname)  
    
    fout = open(foutname,'w')
    fout.write(m.colnames()+'\n')

    ntrial = 10000

    for x in xrange(ntrial+1):
        v = float(x) / ntrial
        v = mean[grade] + (v - 0.5) * 5.0  # 2.5 logits down and up
    
        if x % 100 == 0: print x,'=>',v
        fout.write(m.one_sim(x,v))
            
    fout.close()

def run_to_end(grade,condition):
    foutname = '/Users/renselange/symphony/symresults/to_end_%d.txt' % (grade)
    defsname = '/Users/renselange/symphony/symcode/data/itemdefs.txt'
    
    mean     =  [-5.53,-3.83,-2.32,-1.35,-0.40, 0.31,0.72,1.34,1.98]
    
    facset   =  {
                0 : {'CC':0.25,'G':0.25,'MD':0.25,'OA':0.25},
                4 : {'MD':0.25,'NBT':0.25,'NF':0.25,'OA':0.25},
                8 : {'EE':0.33333,'G':0.33333,'SP':0.33333}
                }
          
    m = Multifactor(grade,facset[grade],condition,defsname)  
    
    fout = open(foutname,'w')
    fout.write(m.colnames()+'\n')

    ntrial = 10000
    maxrun = 0

    for x in xrange(ntrial+1):
        v = float(x) / ntrial
        v = mean[grade] + (v - 0.5) * 5.0  # 2.5 logits down and up
    
        if x % 100 == 0: print x,'=>',v
        fout.write(m.one_sim(x,v))
            
    fout.close()



for g in [0]: 
    run_to_end(g,1)


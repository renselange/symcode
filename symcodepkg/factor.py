

import math
import random
import item

'''
for i in itemdb: # a dictionary that looks like: 123: Item(123,-0.48,[0.0,0.0],"001")
    v = itemdb[i]
    print v.show(),
    for c in range(len(v.cat)):
        print ',',c+1,'=',v.cat[c],
    print
'''
class Factor:
	
	def reset(self):
		self.answered  = []			# items with the answer they received, as in: (item,answer)
		self.maxraw    = 0
		self.sumloc	   = 0.0
		self.rawsum	   = 0
		
	def __init__(self):				# start from scratch
		self.reset()
		
	def answer_random(self,atloc):	# draw random answers for all items in this factor
		self.rawsum = 0				# recompute the raw sum of item drawings
		for i in self.answered: self.rawsum += i.randval(atloc)	# randval also stores drawing inside item
		
	def score_and_var(self,atloc):
		"Compute the expected raw sum score and their variance across all items in 'answered'"
		sum = 0.0
		var = 0.0
		for i in self.answered:	# just add'm up across all items in answered list
			s,v		= i.score_and_var(atloc)
			sum		+= s
			var		+= v
		return sum,var			# return two values
		   
	def addobs(self,item,obs=-1):
		"Add this item and observation pair at the end of the answered list"
		item.obs     = obs
		self.maxraw += item.last			# keep track of these sums
		self.sumloc += item.loc
		self.rawsum += obs
		self.answered.append(item)			# make item and answer into a single pair (...)
			   
	def rawtorasch(self,raw,eps=0.01,maxits=15,maxprox=3):	
		"Transform raw score to Rasch logit using UCON, given the items in 'answered'"
		
		nans = len(self.answered)
		if nans == 0: return 0.0, -1.0, 0	# no questions were answered: there is nothing to estimate
		
		raw = float(raw)					# we may have to deal with non-integer raw sums
		if    raw < 0.3:					raw  = 0.3
		elif  raw >= self.maxraw-0.3:		raw  = self.maxraw - 0.3
		
		# Use trusty PROX as initial estimate
		new   = math.log(raw / (float(self.maxraw)-raw)) + self.sumloc / float(nans)
		
		if	nans <= maxprox: return new, -1.0, 0	# Don't bother computing anything better for less than 4 answers
		
		eps	  = abs(eps)						# just in case ...
		t	  = 0.5+eps
		trial = 0
		
		while (t > eps) and (trial < maxits):
			trial  += 1
			if t < 1.5: old = new				# Truncate |changes| > 1.5 logits
			elif new > old: old += 1.5			
			else: old -= 1.5
			
			est,var	= self.score_and_var(old)	# the actual workhorse
			new     = old + (raw - est)/var		# Newton-Rahpson step
			t		= abs(old-new)
			
		return new, math.sqrt(1.0 / var), trial			# return 3 values
		
	############################################## NEW #############################################
	#
	# determine if we are looking at an extreme low or high raw sum (sum = 0 or sum = max possible)
	
	def raw_lowest(self):  # lowest possible?
	    return self.rawsum == 0
	    
	def raw_highest(self):  # highest possible?
	    return self.rawsum == self.maxraw
	    
	def raw_extreme(self):
	    return self.raw_lowest() or self.raw_highest()
		
	############################################## NEW ############################################	
	#
	# Compute mean and var of residuals (=outfit)
	#
	
	
	def resid(self,atloc):
	    n = len(self.answered)
	    if n < 1: return 0.0,0.0,0              # there is stuff to compute?
	    
	    sx, sxx = 0.0, 0.0
	    
	    for a in self.answered:                 # go through all items in this factor
	        z   = a.resid(atloc,a.obs)
	        sx  += z
	        sxx += z * z
	        if n > 1: var = (sxx - sx*sx/n)/(n-1)   # we allready know that n > 0
	        else: var = (sxx - sx*sx/n)/n           # n==1 -> best that can be done in this case
        
	    return sx/n,var,n-1                     # mean, outfit, df (n-1, that is)
	    
	###############################################################################################
		
	def test1(self,atloc):						# for correctness testing only
		for i in range(30):
			item = Item(i,normal_in_range(-2,2,0,1),[0.0,0],"Cat%d" % (i % 3))
			self.addobs(item,item.randval(atloc))


#################################################### TEST RUNS for resid Feb 27, 2012 ##############################################
######## all of the following is commment

'''############################################## NEW #############################################
#
# determine if we are looking at an extreme low or high raw sum (sum = 0 or sum = max possible)
def raw_lowest(self):  # lowest possible?
    return self.rawsum == 0
    
def raw_highest(self):  # highest possible?
    return self.rawsum == self.maxraw
    
def raw_extreme(self):
    return self.raw_lowest() or self.raw_highest()
	
############################################## NEW ############################################	
#
# Compute mean and var of residuals (=outfit)
#


def resid(self,atloc):
    n = len(self.answered)
    if n < 1: return 0.0,0.0,0              # there is stuff to compute?
    
    sx, sxx = 0.0, 0.0
    
    for a in self.answered:                 # go through all items in this factor
        z   = a.resid(atloc,a.obs)
        sx  += z
        sxx += z * z
        if n > 1: var = (sxx - sx*sx/n)/(n-1)   # we allready know that n > 0
        else: var = (sxx - sx*sx/n)/n           # n==1 -> best that can be done in this case
    
    return sx/n,var,n-1                     # mean, outfit, df (n-1, that is)
    
###############################################################################################
'''

from item import Item
fac = Factor()
print 'extreme?',fac.raw_lowest(),fac.raw_highest(),fac.raw_extreme()

v = 0
for loc in [-3.5,-2.0,-1.0,0.5,2.5,5.0]: # these are the hypothetical item locations ...
    v   = v + 1
    print v,len(fac.answered),fac.resid(-2.0),fac.resid(0.0),fac.resid(1.0) # residuals are computed at -2,0,and 1
    
    it2 = Item(2,loc,[0.0,0.0],cat='2') 
    v2  = v % 2 #Python: v mod 2
    fac.addobs(it2,v2)
    print v,len(fac.answered),fac.resid(-2.0),fac.resid(0.0),fac.resid(1.0)
    
    print 'extreme?',fac.raw_lowest(),fac.raw_highest(),fac.raw_extreme()
    
    it5 = Item(5,loc+0.5,[0.0,-2.0,-0.5,0.0,2.5],cat='5')
    v5  = v % 5
    fac.addobs(it5,v5)
    print v,len(fac.answered),fac.resid(-1.0),fac.resid(0.0),fac.resid(2.0),
    print fac.rawtorasch(fac.rawsum) # just to be sure
    print
'''
######################## produces ##### lines with ? need not correspond exactly!!!!!! (due to differences in approximations when < 4 items)

extreme? True True True
1 0 (0.0, 0.0, 0) (0.0, 0.0, 0) (0.0, 0.0, 0)
?   1 1 (0.4723665527410148, 0.0, 0) (0.1737739434504453, 0.0, 0) (0.10539922456186418, 0.0, 0)
extreme? False True True
?   1 2 (-1.6765131896987906, 7.706879231108148, 1) (-2.352867786551112, 12.767836863570526, 1) (-5.4159157250800565, 60.05737146033636, 1) (-3.6554651081081646, -1.0, 0)

?   2 2 (-1.0019236835378467, 4.347063401574362, 1) (-2.352867786551112, 12.767836863570526, 1) (-3.462646171186861, 25.461895892247355, 1)
?   2 3 (-1.0012824556918978, 2.1735329343066323, 2) (-2.4746724671870894, 6.428427572459762, 2) (-3.8023271375705963, 13.07709742289384, 2)
extreme? False False False
2 4 (-1.4064871444377245, 2.8411188194146617, 3) (-2.251257589890634, 4.4852752112294025, 3) (-5.470151505991263, 22.341039032387243, 3) (-2.999685029094662, 0.7319016364649438, 2)

3 4 (-0.6767092137395806, 1.8704131137701714, 3) (-2.251257589890634, 4.4852752112294025, 3) (-3.470518625967898, 9.158452502083888, 3)
3 5 (-0.21162311685163884, 2.4843352229199285, 4) (-1.6796999399699803, 4.997347144336153, 4) (-2.70283901254003, 9.81549932092672, 4)
extreme? False False False
3 6 (-0.5398373574961436, 3.522238791010678, 5) (-1.2996791990999301, 4.8643722964174545, 5) (-3.734829151322361, 20.726838447085846, 5) (-1.6513020095030895, 0.6192656316376858, 2)

4 6 (0.247915739623227, 3.2545239419973067, 5) (-1.2996791990999301, 4.8643722964174545, 5) (-2.264989117671185, 9.002674639361326, 5)
4 7 (0.17156994869702455, 2.7529040435427876, 6) (-1.2252679968101408, 4.092402769531362, 6) (-2.124851446102122, 7.639698835084029, 6)
extreme? False False False
4 8 (0.1243658838520818, 5.944080329197957, 7) (-0.6908551029821834, 5.792550931172026, 7) (-2.86182045432007, 18.421563762592573, 7) (-0.5047996901117647, 0.5837675324327792, 2)

5 8 (1.0492749561515236, 8.522560678208006, 7) (-0.6908551029821834, 5.792550931172026, 7) (-1.599040993261826, 8.760126345743817, 7)
5 9 (1.9868817206189684, 15.369198596407998, 8) (-0.22627754071062517, 7.010972867071176, 8) (-1.1861475477202148, 9.199439528866852, 8)
extreme? False False False
5 10 (0.6382009232384753, 7.878868487990733, 9) (-0.26392013318710544, 6.246145529524549, 9) (-2.311260659204812, 16.106305462642776, 9) (-0.2643208622805439, 0.5666778964562921, 2)

6 10 (1.765883618940847, 14.149911472927107, 9) (-0.26392013318710544, 6.246145529524549, 9) (-1.1643598138666023, 8.182026634679739, 9)
6 11 (1.602603527816923, 13.028184595366202, 10) (-0.2473896664086321, 5.6245367962231505, 10) (-1.070812129263876, 7.460086833451608, 10)
extreme? False False False
6 12 (1.314393532239654, 13.034252681363318, 11) (0.2462399614374473, 8.03725778314328, 11) (-1.7871426803798247, 14.879221818317081, 11) (0.04767891275781385, 0.5690048527518411, 2)
'''


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


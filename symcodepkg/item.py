
import math
from random import random

class Item:
	#--------------------------------------------------------------------------------------------------
	# itid = anything
	# loc = real : Location of item in logits, coming from Winsteps etc
	# steps = [0.0,....] (reals) : steps[0] = 0.0, and the others are located where adjacent cats have equal prob
	# cat = string : the name of item subcategories ("" = default)
	
 	def __init__(self,itid,loc,steps=[0.0, 0.0],cat=""):  	
 		"Define a Rasch Partial Credit Item by storing its parameters and pre-computing things"
		
 		# steps: first element should be 0.0, and steps should sum to 0.0
 		# there are len(steps) actual step values (including the 0.0 for the first one)
 		# parameters will be forced to be of the right type
 	
		self.loc      = float(loc)                      # enforce argument types
		self.steps    = steps[:]						# this is just to create self.steps
		self.steps[0] = 0.0								# by definition
		self.cum      = steps[:]						# and cum as well
		self.cum[0]   = 0.0								# by definition
		self.itid     = itid
		self.nsteps   = len(steps)		# one higher than index of last step
		self.last     = len(steps) - 1	# highest index of step and cum arrays
		self.cat	  = cat				#  items may belong to different categories
		self.obs      = -1
		
		t = 0.0		
		for i in range(1,self.nsteps): 					# remember: in Python this stops BEFORE nsteps
			self.steps[i] = float(steps[i])				# make steps and cum all floats			  
			t += self.steps[i]
			self.cum[i] = t
				
		self.cum[self.last] = 0.0    # better safe than sorry: convergence may suffer greatly if different
		
		if abs(t) > 0.001: print "Item %3s: Sum of item steps deviates from 0 = %f" % (itid,t)
		
		
	#------------------------------------------------------------------------------------------------------
	# Compute the probability of observing a particular (recoded) rating value, given the item and step
	# parameters. First the top and bottom of the prob expression are computed
	
	def prob(self,atloc,rating):
	 	"Given the initialization parameters, compute prob of observing rating = 'rating'"
	 	
	 	d = float(atloc) - self.loc
	 	irating = int(rating)
	 	
	 	top = math.exp(float(rating) * d - self.cum[irating])
	 	bot = 1.0 + math.exp(float(self.last) * d)

		# this loop is executed only if there are more than 2 rating categories
	 	
	 	for h in range(1,self.last): # remember: in Python this "stops" BEFORE last
	 	 	if h == irating:
	 	 	  	bot += top
	 	 	else:
	 	 		bot += math.exp(float(h) * d - self.cum[h])
	 	
	 	return top / bot	
	 	
	#-------------------------------------------------------------------------------------------------------
	# Compute the expected raw score and variance of this item for person at "atloc" 
	 	
	def score_and_var(self,atloc):
		" This item's score and variance at atloc"
		
	 	sx  = 0.0
	 	sxx = 0.0

	 	for i in range(1,self.nsteps):				# cat = 0 can be skipped safely, but include all others
	 		fi   = float(i)							# again: in Python i will only go up to nsteps-1
	 		t    = fi * self.prob(atloc,i)
	 		sx  += t
	 		sxx += fi * t
	   	return sx, sxx - sx * sx						# defs of mean and var, right?
	   	
    ################################################# NEW #############################################
    # Compute residual of obs at atloc
    # Return <raw-residual>, <exptd value>, <exptd sd>, <std-residual>
    
	def resid(self,atloc,obs):
		m,v = self.score_and_var(atloc)
		s = math.sqrt(v)
		d = obs - m         # positive if observation is "too high"
		return d/s
	###################################################################################################
	   	
	#--------------------------------------------------------------------------------------------------------
	# Return a randomly drawn observation, given atloc and the item loc/step parms

	def randval(self,atloc):
		"Randomly draw an observation (recoded rating value) for this item"
		
		r = random()
		t = 0.0
		v = 0
		for i in range(self.nsteps):
			t += self.prob(atloc,v)
			if t >= r: 
				self.obs = v
				return v		# stop inside the first category when cum-prob exceeds random drawing 0..0.99999
			v += 1
		self.obs = v - 1
		return self.obs	# just to be safe because probs may not sum to less than 1.0 due to rounding errors (I've seen it)
		
	#------------------------------------------------------------------------------------------------------------	
	# obvious
	
	def show(self):
		return 'Item %3s [cat="%s"] loc=%6.3f step range 0..%d = %s' % (self.itid,self.cat,self.loc,self.last,self.steps)
 	

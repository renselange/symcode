# from multifac import Multifactor
from item import Item
import loaditemdat

'''                                     Actual Occurence
########################################################################################################
Count
                                                IGRADE
                1	    2	    3	    4	    5	    6	    7	    8	    K	    P	    Total
________________________________________________________________________________________________________
icode	CC	    0	    0	    0	    0   	0   	0   	0	    0	28476   	0	    28476
	    EE	    0	    0	    0	    0	    0	12166	3519	    7024    0	    0	    22709
	    F	    0	    0	    0	    0	    0   	0	    0	    3406	0	    0	    3406
	    G	    10274	12892	4382	7414	5984	5570	2625    7524	14898	0	    71563
	    KA	    0	    0   	0	    0   	0   	0   	0	    0	    0   	1472	1472
	    KDA	    0	    0	    0	    0   	0   	0	    0	    0	    0	    3	    3
	    KG	    0	    0	    0	    0	    0	    0	    0	    0   	0	    3003	3003
	    KM	    0	    0	    0	    0	    0	    0	    0	    0	    0	    1446	1446
	    KNO	    0	    0	    0	    0	    0	    0	    0	    0	    0	    2917	2917
	    MD	    7548	36924	24737	14112	12764	0	    0	    0	    8934	0	    105019
	    NBT	    29621	38509	10047	15834	11487	0	    0	    0	    4939	0	    110437
	    NF	    0	    0	    13339	21169	20860	0		0	    0	    0	    0       55368
	    NS	    0	    0   	0	    0	    0	    14239	6681	1345	0	    0   	22265
	    OA	    21981	6761	24552	5966	6468	0	    0	    0	    6672	0	    72400
	    RP	    0	    0	    0	    0	    0	    7605	4144	0	    0	    0	    11749
	    SP	    0   	0	    0	    0	    0	    7442	7105	3078	0   	0	    17625
_________________________________________________________________________________________________________
Total		    69424	95086	77057	64495	57563	47022	24074	22377	63919	8841	529858

#########################################################################################################


771 items were loaded from ../data/itemdefs.txt

      CC   EE    F    G   KA   KG   KM  KNO   MD  NBT   NF   NS   OA   RP   SP
_______________________________________________________________
 -1    0    0    0    0    1    2    1    2    0    0    0    0    0    0    0
  0   30    0    0   17    0    0    0    0    9    3    0    0   15    0    0
  1    0    0    0    9    0    0    0    0   12   24    0    0   23    0    0
  2    0    0    0    8    0    0    0    0   30   31    0    0   12    0    0
  3    0    0    0    6    0    0    0    0   31    9   19    0   26    0    0
  4    0    0    0    9    0    0    0    0   22   18   32    0   11    0    0
  5    0    0    0   12    0    0    0    0   21   23   31    0    8    0    0
  6    0   31    0    6    0    0    0    0    0    0    0   34    0   15   21
  7    0    9    0   12    0    0    0    0    0    0    0   23    0   12   26
  8    0   22   10   26    0    0    0    0    0    0    0    6    0    0   11
_______________________________________________________________
SUM   30   62   10  105    1    2    1    2  125  108   82   63   95   27   58


CUMULATIVE VERSION - by row

      CC   EE    F    G   KA   KG   KM  KNO   MD  NBT   NF   NS   OA   RP   SP
_______________________________________________________________
 -1    0    0    0    0    1    2    1    2    0    0    0    0    0    0    0
  0   30    0    0   17    1    2    1    2    9    3    0    0   15    0    0
  1   30    0    0   26    1    2    1    2   21   27    0    0   38    0    0
  2   30    0    0   34    1    2    1    2   51   58    0    0   50    0    0
  3   30    0    0   40    1    2    1    2   82   67   19    0   76    0    0
  4   30    0    0   49    1    2    1    2  104   85   51    0   87    0    0
  5   30    0    0   61    1    2    1    2  125  108   82    0   95    0    0
  6   30   31    0   67    1    2    1    2  125  108   82   34   95   15   21
  7   30   40    0   79    1    2    1    2  125  108   82   57   95   27   47
  8   30   62   10  105    1    2    1    2  125  108   82   63   95   27   58
_______________________________________________________________
SUM   30   62   10  105    1    2    1    2  125  108   82   63   95   27   58


'''
class ItemDB:
    
    def __init__(self,fname,itgrade):
        itgrade    = str(itgrade).strip()
        if itgrade[0] == 'K': self.itgrade = 0
        elif itgrade[0] == 'P': self.itgrade = -1
        else: self.itgrade = int(itgrade)
        
        self.freq   = {} # store by grade and cat
        self.cfreq  = {} # cumulative version of freq across grades
        self.count  = {} # count of all content areas, regardless of grade
        
        self.fname      = fname
        self.store      = loaditemdat.loadfile(fname)
        print len(self.store),'items were loaded from',fname
        self.itemcats   = {}
        
        for tup in self.store: # looks like: ([iarea,itgrade,itcontent,itformat],<item>), where itgrade is integer -1,0,1, ...,8
            info    = tup[0]
            item    = tup[1]
            grade   = info[1]
            content = info[2]
            
        # fix low cell freqs
            if grade == -1: content = 'K'
            if grade ==  0 and content == 'NBT': content = 'MD'
            
            
            if not grade in self.freq: self.freq[grade] = {}
            if not content in self.freq[grade]: self.freq[grade][content] = 0
            if not content in self.count: self.count[content] = 1
            else: self.count[content] += 1
            self.freq[grade][content] += 1
            
            #if grade <= self.itgrade:
            #    if not item.cat in self.itemcats and grade == self.itgrade: self.itemcats[item.cat] = [item]
            #    elif item.cat in self.itemcats: self.itemcats[item.cat].append(item)
                
    # print tables
        kk = self.count.keys()
        self.sortedcats = sorted(kk)
        print
        print ' '*3,
        for c in self.sortedcats: print '%4s'%c,
        print
        print '_'*(3+len(self.sortedcats)*4)
        for g in range(-1,9):
            if not g in self.freq: continue
            print '%3d'%g,
            for k in self.sortedcats: 
                if not k in self.freq[g]: self.freq[g][k] = 0
                print '%4d'%self.freq[g][k],
            print
        print '_'*(3+len(self.sortedcats)*4)
        print 'SUM',
        for k in self.sortedcats: print '%4d'%self.count[k],
        print;print
        
        last = ''
        for g in range(-1,9):
            self.cfreq[g] = {}
            for k in self.sortedcats: self.cfreq[g][k] = 0
            if g == -1: 
                for k in self.sortedcats: self.cfreq[g][k] = self.freq[g][k]
            else:
                for k in self.sortedcats: self.cfreq[g][k] = self.freq[g][k]+self.cfreq[g-1][k]

        print
        print 'CUMULATIVE VERSION - by row'
        print
        print ' '*3,
        for c in self.sortedcats: print '%4s'%c,
        print
        print '_'*(3+len(self.sortedcats)*4)
        for g in range(-1,9):
            if not g in self.cfreq: continue
            print '%3d'%g,
            for k in self.sortedcats: 
                if not k in self.cfreq[g]: self.cfreq[g][k] = 0
                print '%4d'%self.cfreq[g][k],
            print
        print '_'*(3+len(self.sortedcats)*4)
        print 'SUM',
        for k in self.sortedcats: print '%4d'%self.count[k],
        print;print
    
        
db = ItemDB('../data/itemdefs.txt',3)


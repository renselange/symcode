from copy  import copy
import time

class facfile():
    def __init__(self,fname):
        self.fname = fname
        self.fptr  = open(fname,'r')
        self.count = 0
        self.nerr  = 0
        self.line  = self.fptr.readline()
        self.names = self.line.strip().split(',')
        print self.names
        self.nread = 1
        self.ateof = False
        self.rec   = {}
        self.last  = ''
        self.fstud = {}
        self.fitem = {}
        
    def done(self):
        self.fptr.close()
        
   # Given the number of points (0..100) and the number of categories (2...),
   # deduce the category as used in Rasch scoring
   # Missing / error values are returned as the integer 9
           
    def sym_to_cat(self,points,nval):
        try: 
            return {2:{0:0,100:1},
                3:{0:0,50:1,100:2},
                4:{0:0,33:1,66:2,67:2,100:3},
                5:{0:0,25:1,50:2,75:3,100:4},
                6:{0:0,20:1,40:2,60:3,80:4,100:5}
                }[nval][points]
        except:
            self.error = True
            self.nerr  += 1
            print 'Line:',self.nread,' ***************',
            print 'sym_to_cat error:',points,nval,'***************'
            print self.line
            print '*******************************************'
            return 9
                
    # Given an observation, as used for Rasch, apply recoding (e.g., "001123", etc) to obtain "cat"
    # the recoding should be given in a string, Winsteps style
               
    def obs_to_cat(self,codestring,obs):
        cat = int(codestring[obs])
        self.rec['recd-cat']        = cat
        self.rec['recd-catmax']     = int(codestring[-1])   # look in the last position. WILL FAIL FOR: "0021"
        self.rec['recode-string']   = codestring
        return cat
        
    def get_sub_lists(self,s):
        if len(s) == 2: return [[s[0]],[s[1]]] # two one-element lists
        sub = []
        t   = []
        inside = False
        
        for v in s:
            if '"' in v:    # it is either the first or the last in the sub-list
                if not inside:
                    if len(sub) > 0: t.append(sub)
                    sub = [v[1:]]
                    inside = True
                else:                           # the last
                    sub += [v[:len(v)-1]]
                    t.append(sub)
                    sub = []
                    inside = False
            else:
                sub.append(v)

        if sub != []: t.append(sub)
        return t

 # keep in mind that we start out not having read any data yet (except the variable names in the col headers)
 
    def next_student(self):
        if self.ateof: return []
        
        if self.last == '': self.itemlist   = []
        else: self.itemlist   = [self.rec.copy()]
        
        while True:
            self.next()
            if self.last == '': self.last = self.rec['Student ID#']     # special case in beginning
            if self.rec['Student ID#'] == self.last and not self.ateof: self.itemlist.append(self.rec.copy())
            else:
                self.last = self.rec['Student ID#']
                return self.itemlist
            
# recodings made into functions for consistency

    def grade_code(self,g):
        if g == 'pk': g = 'P'
        if g == 'PK': g = 'P'
        if g == 'k' : g = 'K'
        if not g in ['P','K','1','2','3','4','5','6','7','8','9']: g = 'X'
        return {'P':10,'K':11,'X':12,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9}[g]

    def gender_code(self,x):
        if not x in ['F','M']: x = 'x'
        return {'F':1,'M':2,'x':3}[x]
        
    def item_cat_code(self,ncat):
        if ncat == 2: return '2'
        else: return '1'
    
# assuming that we have just read a student's worth of data
# this will take those and make a Winsteps style data record
# The default lowest item id# is 96. This becomes winrec[0]

    def winrec(self,lo=93,hi=1300): # Python range style!
        s   = [' ']*(hi - lo)         # doesn't work for strings, so ...
        
        for v in self.itemlist:
            itid         = int(v['ItemDB#'])
            #print itid,lo
            s[itid - lo] = '%s' % v['recd-cat']
            
        v = self.itemlist[0]
            
        g = self.grade_code(v['Grade'])      # grade goes: P,K,1, ...,9,+
        x = self.gender_code(v['gender'])
        
        return '%s|%5s|%7s|%2s|%3d|%1s' % (''.join(s),v['schoolID'],v['Student ID#'],g,len(self.itemlist),x)

# print facet labels 

    def print_winprog(self,outfile):
        fout = open(outfile+'.win.con','w')

        fout.write('title  = data orgin="%s" on %s to "%s"\n' % (self.fname,time.asctime( time.localtime(time.time()) ),outfile))

        fout.write('data   = '+outfile+'\n')
        
        
        # self.fitem[ids] = {'ID':self.rec['Item ID'],'NVAL':self.rec['Scoring Levels']}
        for i in range(93,1300):
            if i in self.fitem: fout.write('%d = %s (%s)\n' % (i,self.fitem[i]['ID'],self.fitem[i]['NVAL']))
            else: fout.write('%d = ***\n' % (i))
        
        fout.close()
        
# get next record from file

    def next(self):
        if self.ateof: return ''
        
        self.line = self.fptr.readline().strip()
        self.nread += 1
        while self.line and (not self.line[0] in '0123456789' or 
                             ',50,4' in self.line or 
                             '25,4' in self.line or
                             '33,3' in self.line):
            self.line = (self.fptr.readline()).strip()
            self.nread += 1
        #print self.line
        
        if self.line != '':
            self.error  = False
            self.fields = self.line.split(',')
            for v in range(12):     self.rec[self.names[v] ] = self.fields[v]
            for v in range(1,26):   self.rec[self.names[-v]] = self.fields[-v]
            if not self.rec['ItemDB#'] in self.fitem: 
                ids = int(self.rec['ItemDB#'])            
                self.fitem[ids] = {'ID':self.rec['Item ID'],'NVAL':self.rec['Scoring Levels']}
            
            points              = int(self.rec['Item Score']) # self.fields[9])
            self.rec['points']  = points            # points according to symphony
            nval                = int(self.rec['Scoring Levels']) # self.fields[10]) # no of cats for points
            self.rec['nval']    = nval
            cat                 = self.sym_to_cat(points,nval)
            self.rec['orig-cat']    = cat           # Rasch coded value 0..nval-1 = 0..catmax
            self.rec['orig-catmax'] = nval - 1
        
            self.rec['recode-string'] = '0123456789'[:nval]     # to be consistent
            self.rec['recd-cat']    = cat           # this could be overwritten later by 'cat_to_code'
            self.rec['recd-catmax'] = nval - 1      # this could be overwritten later by 'cat_to_code'
            if nval > 2: self.rec['recd-cat'] = self.obs_to_cat('00123456789'[:nval],cat) # ****************** quicky ******************
            
            t                   = self.get_sub_lists(self.fields[11:len(self.fields)-25]) # in Symphony's notation
            #self.rec['Student Response'] = t[0]     # string representation
            #self.rec['Solution'] = t[1]             # string representation
            self.count  += 1
            self.ateof = False
        else:
            self.ateof = True
        return self.line

######################################### A typical record
    '''*****************************************
         ;userID = 564883
             ADA = NULL
              AR = NULL
             BIL = NULL
             CF1 = NULL
             CF2 = NULL
             CF3 = NULL
             CF4 = NULL
  Duration(secs) = 17
             ESL = NULL
        End Time = 9/26/2011 2:10
              FL = NULL
              GT = NULL
           Grade = 5
         Item ID = M4NF3Be_1
      Item Score = 0
       Item Type = 1
         ItemDB# = 592
              LD = NULL
             LEP = NULL
              MG = NULL
              NA = NULL
              PD = NULL
              RL = NULL
              SE = NULL
  Scoring Levels = 2
        Solution = ['d']
      Start Time = 9/26/2011 2:09
     Student ID# = 564883
Student Response = ['b']
              T1 = NULL
    Test Edition = 0
      Test Event = 4262
             dob = NULL
       ethnicity = NULL
          gender = NULL
        language = NULL
            nval = 2
        orig-cat = 0
     orig-catmax = 1
          points = 0
        recd-cat = 0
     recd-catmax = 2
   recode-string = 01122
        schoolID = 4124'''

    def recstring(self):
        kk = self.rec.keys()
        kk.sort()
        s = '*****************************************\n'
        for k in kk:
            s += '%16s = %s\n' % (k,self.rec[k])
        return s

      
f = facfile('/Users/renselange/symphony/2011recalib23/combo23.csv')

c = 0
with open('windat.txt','w') as fout:
    while not f.ateof:
        f.next_student()
        c += 1
        if c % 100 == 0: print 'Person:',c,' Recs read:',f.nread
        # fout.write(f.winrec()+'\n')
        fout.write(f.winrec()+'\n')
print 'Tot errors found:',f.nerr

f.print_winprog('winprog.con')
    
f.done()

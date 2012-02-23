
from symcodepkg.test import *

print da()

with open('feb2012.csv','r') as fin:
    for i,v in enumerate(fin):
        print v.strip()
        if i > 10: break
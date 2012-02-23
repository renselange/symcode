
 
GET DATA 
  /TYPE=TXT 
  /FILE="/Users/renselange/symphony/symcode/winsteps/spssin.txt" 
  /DELCASE=LINE 
  /DELIMITERS="," 
  /ARRANGEMENT=DELIMITED 
  /FIRSTCASE=2 
  /IMPORTCASE=ALL 
  /VARIABLES= 
  igrade A1 
  itype F1.0 
  icode A3 
  ploc F5.2 
  school F4.0 
  student F6.0 
  sgrade F1.0 
  v2 F2.0 
  sex F1.0 
  residual F6.3 
  count F2.0.

CACHE. 
select if((sgrade<>9 or sgrade <> 12) and (sgrade < 9) and (icode <> 'KA') and (icode <> 'KG') and (icode <> 'KM') and (icode <> 'KNO') and 
 (school > 395) and (school <> 1389) and (school <> 1394) and (school <> 4134) and (school <> 4121) and (school <> 4139) and (school <> 4117) and (school <> 4091) and (school <> 4055)).
EXECUTE. 
DATASET NAME DataSet2 WINDOW=FRONT. 
DATASET ACTIVATE DataSet2. 
DATASET CLOSE DataSet1. 

CROSSTABS 
  /TABLES=sgrade BY igrade 
  /FORMAT=AVALUE TABLES 
  /CELLS=COUNT 
  /COUNT ROUND CELL.

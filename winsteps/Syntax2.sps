GET DATA 
  /TYPE=TXT 
  /FILE="/Users/renselange/symphony/symcode/winsteps/spssin.txt" 
  /DELCASE=LINE 
  /DELIMITERS="," 
  /ARRANGEMENT=DELIMITED 
  /FIRSTCASE=2 
  /IMPORTCASE=ALL 
  /VARIABLES= 
  itno F4.0 
  igrade A1 
  icat A3 
  ploc F5.2 
  xxx F1.0 
  school F4.0 
  student F6.0 
  v1 F1.0 
  v2 F2.0 
  v3 F1.0 
  residual F6.3 
  count F2.0. 
CACHE. 
select if(v1<>9 or v1 <> 12).
EXECUTE. 
DATASET NAME DataSet2 WINDOW=FRONT. 
DATASET ACTIVATE DataSet2. 
DATASET CLOSE DataSet1. 
CROSSTABS 
  /TABLES=v1 BY igrade 
  /FORMAT=AVALUE TABLES 
  /CELLS=COUNT 
  /COUNT ROUND CELL.

import os
B='C:/Users/corin/Desktop/LEVIATHANV2/leviathan'
def w(p,c):
  fp=os.path.join(B,p)
  with open(fp,'w',encoding='utf-8') as f: f.write(c)
  print('Wrote',fp)

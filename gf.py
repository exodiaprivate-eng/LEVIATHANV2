import os,base64,sys
B='C:/Users/corin/Desktop/LEVIATHANV2/leviathan'
for l in open('gf.dat'):
  p,b=l.strip().split('|',1)
  fp=os.path.join(B,p)
  open(fp,'wb').write(base64.b64decode(b))
  print('Wrote',fp)

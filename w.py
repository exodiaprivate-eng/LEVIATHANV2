import base64,sys,os,json
data=json.load(open(sys.argv[1]))
for p,b in data.items():
  os.makedirs(os.path.dirname(p),exist_ok=True)
  open(p,"wb").write(base64.b64decode(b))
  print("Wrote",p)

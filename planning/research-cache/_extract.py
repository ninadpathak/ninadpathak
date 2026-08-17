import json,sys
src,dest=sys.argv[1],sys.argv[2]
raw=json.load(open(src))
txt="".join(b.get("text","") for b in raw) if isinstance(raw,list) else raw
o,j=json.JSONDecoder().raw_decode(txt,0)
key=next(iter(o))
rows=o[key]
json.dump(rows,open(dest,'w'),indent=1)
print("key:",key,"rows:",len(rows))
print("tail:",txt[j:j+300][-160:])

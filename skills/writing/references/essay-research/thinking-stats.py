# Reads thinking.tsv (hand-classified hooks, thesis snippets) and the corpus in /tmp/pg-essays/txt,
# writes thinking-stats.json. Run from this directory: python3 thinking-stats.py
import re,json,statistics as st,csv,os
from collections import Counter
TXT=os.environ.get('PG_TXT','/tmp/pg-essays/txt')
def norm(s): return re.sub(r'\s+',' ',s.replace('’',"'").replace('“','"').replace('”','"')).strip()
def words(s): return re.findall(r"[A-Za-z0-9'’-]+",s)
rows=list(csv.DictReader(open('thinking.tsv'),delimiter='\t'))
hook=Counter(r['hook'] for r in rows)
opens=Counter(r['opens_on'] for r in rows)
ret=Counter(r['ending_returns'] for r in rows)
wtt=[];missing=[]
PH={'why questions':r'\bwhy\b[^.?!]*\?','suppose':r'\bsuppose\b','imagine':r'\bimagine\b','consider':r'\bconsider\b','what if':r'\bwhat if\b','the reason':r'\bthe reason\b','because':r'\bbecause\b','which means':r'\bwhich means\b','so (sentence start)':r'(?:^|[.?!]["\')]?\s+)so\b','in other words':r'\bin other words\b','the test is':r'\bthe test (is|of)\b','or more precisely':r'\bor more precisely\b','turns out':r'\bturns? out\b','the question is':r'\bthe (real )?question (is|to ask)\b','not x but y':r'\bnot (merely|just|only) [^.]{0,60}\bbut\b','i could be wrong / i don.t know':r"\b(i could be wrong|i don't know|i'm not sure|i may be wrong)\b",'has to be / would have to':r'\b(has|have|had) to be\b|\bwould have to\b','opposite':r'\bthe opposite\b','two kinds/ways':r'\btwo (kinds|ways|sorts|types|different)\b'}
per={k:[] for k in PH}; tot={k:0 for k in PH}; W=0
for r in rows:
    t=open(f"{TXT}/{r['slug']}.txt").read().split('\n\n')
    body=[]
    for p in t[1:]:
        if re.match(r'^(Notes?|Thanks)\b',p.strip()): break
        if p.strip(): body.append(norm(p))
    full=' '.join(body); low=full.lower(); n=len(words(full)); W+=n
    i=low.find(norm(r['thesis']).lower())
    if i<0: missing.append(r['slug'])
    else: wtt.append(len(words(full[:i])))
    for k,pat in PH.items():
        c=len(re.findall(pat,low,flags=re.I)); per[k].append(c); tot[k]+=c
N=len(rows)
# per-hook-type median words to thesis
byhook={}
for r,w in zip(rows,wtt): byhook.setdefault(r['hook'],[]).append(w)
out={'scope':'106 essays read newest to oldest, August 2026 through August 2010 (Founder Control); reading stopped at Ninad\'s direction on 2026-09-05. Hook types and thesis sentences are hand-classified in thinking.tsv; counts are computed from the stripped essay text.','essays':N,'words':W,
'share_thesis_in_first_sentence':round(sum(1 for x in wtt if x<3)/len(wtt)*100,1),
'median_words_to_thesis_by_hook':{k:st.median(v) for k,v in sorted(byhook.items(),key=lambda kv:-len(kv[1]))},
'hook_type_distribution':{k:[v,round(v/N*100,1)] for k,v in hook.most_common()},
'opens_on_distribution':{k:[v,round(v/N*100,1)] for k,v in opens.most_common()},
'median_words_to_thesis':st.median(wtt),'mean_words_to_thesis':round(sum(wtt)/len(wtt)),
'quartiles_words_to_thesis':[st.quantiles(wtt,n=4)[0],st.median(wtt),st.quantiles(wtt,n=4)[2]],
'share_thesis_within_first_100_words':round(sum(1 for x in wtt if x<100)/len(wtt)*100,1),
'share_thesis_within_first_50_words':round(sum(1 for x in wtt if x<50)/len(wtt)*100,1),
'share_thesis_after_300_words':round(sum(1 for x in wtt if x>=300)/len(wtt)*100,1),
'ending_returns_to_opening':{k:[v,round(v/N*100,1)] for k,v in ret.items()},
'phrase_totals':tot,'phrase_per_100k_words':{k:round(v/W*1e5,1) for k,v in tot.items()},
'phrase_median_per_essay':{k:st.median(v) for k,v in per.items()},
'phrase_share_of_essays_with_at_least_one':{k:round(sum(1 for x in v if x)/N*100,1) for k,v in per.items()},
'thesis_not_found':missing}
json.dump(out,open('thinking-stats.json','w'),indent=1)
for k,v in out.items(): print(k,':',v)

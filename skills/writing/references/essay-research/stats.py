import re,json,statistics as st
from collections import Counter
def sents(p):
    p=re.sub(r'\s+',' ',p)
    p=re.sub(r'\b(Mr|Mrs|Dr|St|vs|No|Jr|Inc|Ltd|etc|e\.g|i\.e|U\.S|Ph\.D|Sen|Gov|Prof|Mt)\.',lambda m:m.group(0).replace('.','<DOT>'),p)
    parts=re.split(r'(?<=[.!?])["\')]?\s+(?=["\'(]?[A-Z0-9])',p)
    parts=[x.replace('<DOT>','.') for x in parts]
    return [x.strip() for x in parts if len(x.split())>0]
def words(s): return re.findall(r"[A-Za-z0-9'’-]+",s)
essays=[]
for line in open('links.tsv'):
    h,t=line.rstrip('\n').split('\t'); slug=h[:-5]
    raw=open(f'txt/{slug}.txt').read().split('\n\n')
    hdr=raw[0]; paras=[p for p in raw[1:] if p.strip()]
    ps=[sents(p) for p in paras]
    essays.append(dict(slug=slug,title=t,date=hdr.split('\n')[1] if '\n' in hdr else '',paras=paras,sents=ps))
allsents=[s for e in essays for p in e['sents'] for s in p]
wps=[len(words(s)) for s in allsents]
spp=[len(p) for e in essays for p in e['sents']]
wpp=[len(words(p)) for e in essays for p in e['paras']]
N=len(allsents); W=sum(wps)
firstw=Counter()
for s in allsents:
    w=words(s)
    if w: firstw[w[0]]+=1
Istart=sum(1 for s in allsents if re.match(r"^[\"(]?I(['’](m|ve|d|ll))?\b",s))
firsts=[e['sents'][0][0] for e in essays if e['sents']]
first_under15=sum(1 for s in firsts if len(words(s))<15)
firstlens=[len(words(s)) for s in firsts]
firstpara_words=[len(words(e['paras'][0])) for e in essays]
firstpara_sents=[len(e['sents'][0]) for e in essays]
lasts=[e['sents'][-1][-1] for e in essays if e['sents']]
lastlens=[len(words(s)) for s in lasts]
text=' '.join(allsents); low=text.lower()
def cnt(pat): return len(re.findall(pat,low))
phrases={'everyone':r'\beveryone\b','most people':r'\bmost people\b','in today\'s':r"\bin today['’]s\b","it's worth noting":r"\bit['’]s worth noting\b",'we all':r'\bwe all\b','in this essay':r'\bin this essay\b','landscape':r'\blandscape\b','delve':r'\bdelv','crucial':r'\bcrucial\b','it is important to':r'\bit is important to\b','in a world where':r'\bin a world where\b','game-changer':r'\bgame.changer','leverage (verb)':r'\bleverag','robust':r'\brobust\b','ultimately':r'\bultimately\b','at the end of the day':r'\bat the end of the day\b','needless to say':r'\bneedless to say\b','the fact that':r'\bthe fact that\b','I think':r'\bi think\b','probably':r'\bprobably\b','seems':r'\bseems?\b','I suspect':r'\bi suspect\b','of course':r'\bof course\b','for example':r'\bfor example\b','e.g.':r'\be\.g\.','you':r'\byou\b','I':r'\bi\b','we':r'\bwe\b','so ':r'^so\b|\. so\b','but ':r'^but\b|\. but\b','and ':r'^and\b|\. and\b','?':r'\?','semicolon':r';','em dash':r'—|--',"n't/'s contractions":r"\w['’](t|s|re|ve|ll|d|m)\b",'colon':r':','parentheses':r'\(','quotation':r'"'}
freq={k:cnt(v) for k,v in phrases.items()}
sent_start=Counter()
for s in allsents:
    w=words(s)
    if w: sent_start[w[0].lower()]+=1
q_para_end=sum(1 for e in essays for p in e['paras'] if p.rstrip().endswith('?'))
q_essay_end=sum(1 for e in essays if e['paras'][-1].rstrip().endswith('?'))
q_first=sum(1 for s in firsts if s.rstrip().endswith('?'))
short_sent=sum(1 for x in wps if x<=8)
long_sent=sum(1 for x in wps if x>=30)
one_sent_para=sum(1 for x in spp if x==1)
ewords=[sum(len(words(p)) for p in e['paras']) for e in essays]
out={'essays':len(essays),'sentences':N,'words':W,'paragraphs':len(spp),
'median_words_per_sentence':st.median(wps),'mean_words_per_sentence':round(W/N,1),
'median_sentences_per_paragraph':st.median(spp),'mean_sentences_per_paragraph':round(sum(spp)/len(spp),2),
'median_words_per_paragraph':st.median(wpp),
'share_sentences_starting_I':round(Istart/N*100,1),
'share_first_sentence_under_15_words':round(first_under15/len(firsts)*100,1),'median_first_sentence_words':st.median(firstlens),
'median_first_paragraph_words':st.median(firstpara_words),'median_first_paragraph_sentences':st.median(firstpara_sents),
'median_last_sentence_words':st.median(lastlens),
'share_sentences_8_words_or_fewer':round(short_sent/N*100,1),'share_sentences_30_words_or_more':round(long_sent/N*100,1),
'share_one_sentence_paragraphs':round(one_sent_para/len(spp)*100,1),
'share_paragraphs_ending_with_question':round(q_para_end/len(spp)*100,1),'essays_ending_with_question':q_essay_end,'first_sentences_that_are_questions':q_first,
'median_essay_words':st.median(ewords),
'top_first_words':sent_start.most_common(25),
'phrase_counts_total':freq,'phrase_per_100k_words':{k:round(v/W*1e5,1) for k,v in freq.items()},
'I_sentence_start_by_decade':{}}
for dec in ('199','200','201','202'):
    ss=[s for e in essays if dec in e['date'] or (dec=='199' and not e['date']) for p in e['sents'] for s in p]
    if ss: out['I_sentence_start_by_decade'][dec+'x']=(len(ss),round(sum(1 for s in ss if re.match(r"^[\"(]?I(['’](m|ve|d|ll))?\b",s))/len(ss)*100,1),st.median([len(words(s)) for s in ss]))
json.dump(out,open('stats.json','w'),indent=1)
for k,v in out.items(): print(k,':',v)
# per-essay table
with open('per_essay.tsv','w') as f:
    f.write('slug\ttitle\tdate\twords\tparas\tmed_wps\tfirst_sent_words\tfirst_sentence\tlast_sentence\n')
    for e in essays:
        ws=[len(words(s)) for p in e['sents'] for s in p]
        f.write('\t'.join([e['slug'],e['title'],e['date'],str(sum(ws)),str(len(e['paras'])),str(st.median(ws)),str(len(words(e['sents'][0][0]))),e['sents'][0][0],e['sents'][-1][-1]])+'\n')

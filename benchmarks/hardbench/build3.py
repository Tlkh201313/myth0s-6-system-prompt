#!/usr/bin/env python3
"""hardbench v3 — EDGE set: genuinely at/over one-shot ability. Solver-verified logic,
computed counting/word-problem keys. Emits questions3.json + battery3_block.txt."""
import json, itertools, hashlib
Q=[]
def add(qid,bucket,prompt,gtype,gspec): Q.append({"id":qid,"bucket":bucket,"prompt":prompt,"gtype":gtype,"gspec":gspec})

# ---------- 5-house x 3-category ZEBRA (reduced to unique, hard one-shot) ----------
def zsolve(cats, clues):
    names=list(cats); n=len(next(iter(cats.values())))
    perms={c:list(itertools.permutations(range(n))) for c in names}
    sols=[]
    for combo in itertools.product(*[perms[c] for c in names]):
        pos={}
        for ci,c in enumerate(names):
            for vi,v in enumerate(cats[c]): pos[(c,v)]=combo[ci][vi]
        if all(ev(cl,pos) for cl in clues):
            sols.append(pos)
            if len(sols)>1: return sols
    return sols
def ev(cl,pos):
    k=cl[0]
    if k=="at": return pos[cl[1]]==cl[2]
    if k=="same": return pos[cl[1]]==pos[cl[2]]
    if k=="rightof": return pos[cl[1]]==pos[cl[2]]+1
    if k=="nextto": return abs(pos[cl[1]]-pos[cl[2]])==1
    if k=="left": return pos[cl[1]]<pos[cl[2]]
def ctext(cl):
    def nm(cv): return f"the {cv[1]} {cv[0]}"
    k=cl[0]
    return {"at":lambda:f"{nm(cl[1])} is in position {cl[2]+1}",
            "same":lambda:f"{nm(cl[1])} and {nm(cl[2])} are the same house",
            "rightof":lambda:f"{nm(cl[1])} is immediately right of {nm(cl[2])}",
            "nextto":lambda:f"{nm(cl[1])} is directly next to {nm(cl[2])}",
            "left":lambda:f"{nm(cl[1])} is somewhere left of {nm(cl[2])}"}[k]()
def make_zebra(qid,cats,truth,ask_cat,ask_anchor):
    n=len(next(iter(cats.values())))
    gt=dict(truth)
    cand=[]
    cvs=[(c,v) for c in cats for v in cats[c]]
    for cv in cvs: cand.append(("at",cv,gt[cv]))
    for a in cvs:
        for b in cvs:
            if a[0]==b[0]: continue
            if gt[a]==gt[b]: cand.append(("same",a,b))
            if gt[a]==gt[b]+1: cand.append(("rightof",a,b))
            if abs(gt[a]-gt[b])==1: cand.append(("nextto",a,b))
            if gt[a]<gt[b]: cand.append(("left",a,b))
    clues=list(cand); assert len(zsolve(cats,clues))==1
    # greedy minimize (deterministic order)
    for cl in cand:
        if cl in clues:
            trial=[x for x in clues if x!=cl]
            if len(zsolve(cats,trial))==1: clues=trial
    sols=zsolve(cats,clues); assert len(sols)==1,(qid,len(sols))
    pos=sols[0]; ap=pos[ask_anchor]
    ans=next(v for v in cats[ask_cat] if pos[(ask_cat,v)]==ap)
    header=(f"There are 5 houses in a row, positions 1-5 left to right, each with a unique value "
            f"per category. Categories: " + "; ".join(f"{c} ({', '.join(cats[c])})" for c in cats)
            + ". Clues: " + "; ".join(ctext(cl) for cl in clues)
            + f". Question: {ask_anchor[1]} shares its house with which {ask_cat}? One word.")
    add(qid,"zebra5",header,"contains",{"all_any":[[ans.lower()]],"forbid":[]})

Z=[("red","green","blue","white","yellow"),("brit","swede","dane","norse","germ"),
   ("tea","milk","water","beer","coffee")]
def mk_truth(cats, perm):
    t={}
    for ci,c in enumerate(cats):
        for vi,v in enumerate(cats[c]): t[(c,v)]=perm[ci][vi]
    return t
cats5={"color":list(Z[0]),"nation":list(Z[1]),"drink":list(Z[2])}
make_zebra("z5q1",cats5,mk_truth(cats5,[(0,1,2,3,4),(2,0,3,1,4),(1,3,0,4,2)]),"drink",("nation","germ"))
make_zebra("z5q2",cats5,mk_truth(cats5,[(4,2,0,3,1),(0,3,1,4,2),(3,1,4,2,0)]),"color",("nation","dane"))
make_zebra("z5q3",cats5,mk_truth(cats5,[(1,0,3,2,4),(3,4,0,1,2),(0,2,4,3,1)]),"nation",("color","white"))
make_zebra("z5q4",cats5,mk_truth(cats5,[(2,4,1,0,3),(1,0,4,3,2),(4,3,2,1,0)]),"drink",("color","yellow"))

# ---------- 4-speaker KNIGHTS & KNAVES ----------
def ekk(st,t):
    k=st[0]
    if k=="knave": return not t[st[1]]
    if k=="knight": return t[st[1]]
    if k=="same": return t[st[1]]==t[st[2]]
    if k=="diff": return t[st[1]]!=t[st[2]]
    if k=="count": return sum(t.values())==st[1]
    if k=="atleast": return sum(t.values())>=st[1]
def rkk(st):
    k=st[0]
    return {"knave":lambda:f"{st[1]} is a knave","knight":lambda:f"{st[1]} is a knight",
            "same":lambda:f"{st[1]} and {st[2]} are the same type","diff":lambda:f"{st[1]} and {st[2]} are different types",
            "count":lambda:f"exactly {st[1]} of the four of us are knights","atleast":lambda:f"at least {st[1]} of us are knights"}[k]()
def solkk(names,stmts):
    out=[]
    for combo in itertools.product([True,False],repeat=len(names)):
        t=dict(zip(names,combo))
        if all(t[n]==ekk(stmts[n],t) for n in names): out.append(dict(t))
    return out
def opts4(x,others):
    o=others; res=[]
    for y in o: res+=[("knave",y),("knight",y)]
    res+=[("count",1),("count",2),("count",3),("atleast",2),("atleast",3),
          ("same",o[0],o[1]),("diff",o[0],o[2]),("same",o[1],o[2])]
    return res
quads=[["Ada","Ben","Cy","Deb"],["Eve","Fin","Gus","Hal"],["Ida","Jon","Kai","Liv"],["Mae","Ned","Ola","Pip"]]
kkn=0
for names in quads:
    a,b,c,d=names; found=False
    for sa in opts4(a,(b,c,d)):
        for sb in opts4(b,(a,c,d)):
            for sc in opts4(c,(a,b,d)):
                for sd in opts4(d,(a,b,c)):
                    stmts={a:sa,b:sb,c:sc,d:sd}
                    s=solkk(names,stmts)
                    if len(s)==1 and 1<=sum(s[0].values())<=3:
                        kkn+=1
                        knights=sorted(n for n in names if s[0][n])
                        text="Knights always tell the truth; knaves always lie. "+" ".join(f"{n} says: '{rkk(stmts[n])}.'" for n in names)
                        add(f"k4q{kkn}","kk4",text+" Reply with the names of ALL knights, comma-separated, or 'none'.","nameset",{"key":knights,"universe":names})
                        found=True; break
                if found: break
            if found: break
        if found: break
    assert found,names
assert kkn==4

# ---------- LONG multi-step trap word problems ----------
def wp(qid,text,val): assert float(val)==int(val),(qid,val); add(qid,"wpL",text+" Give only the final integer.","numeric",{"key":int(val),"tol":0})
# 14-step-ish
v=1000
v-=v//5      # -200 =800
v=v*3//4     # 600
v+=150       # 750
v-=v//3      # 500
v=v//2       # 250
v+=v//5      # +50 =300
v-=45        # 255
wp("wLq1","A warehouse starts with 1000 crates. Remove one fifth. Then keep three quarters of what remains. Then add 150. Then remove one third of the current amount. Then halve it. Then add one fifth of the current amount. Finally remove 45. How many crates remain?", v)
# money with percent traps
p=500
p=p*(1+10/100)  #550
p=p*(1-10/100)  #495
p=p+55          #550
p=p*(1-20/100)  #440
p=p+p//10       #+44=484
wp("wLq2","A price starts at $500. Increase by 10%. Then decrease by 10%. Then add $55. Then decrease by 20%. Then increase by one tenth of the current price. What is the final price in dollars?", p)
# age multi
# Sara is 4x Tom. In 6 yrs Sara is 2x Tom. now find Sara+Tom. 4T; 4T+6=2(T+6)->4T+6=2T+12->2T=6->T=3,S=12 sum15
wp("wLq3","Sara is 4 times as old as Tom. In 6 years, Sara will be twice as old as Tom. What is the SUM of their current ages?", 15)
# distance multi-leg
# leg1 120km@60 =2h; rest 45min; leg2 80km@40=2h; rest 15min; leg3 150km@50=3h. total minutes
t=120/60*60+45+80/40*60+15+150/50*60
wp("wLq4","A trip has three driving legs with rests between. Leg 1: 120 km at 60 km/h. Rest 45 min. Leg 2: 80 km at 40 km/h. Rest 15 min. Leg 3: 150 km at 50 km/h. What is the TOTAL elapsed time in minutes?", t)
# inventory with returns trap
n=240
n-=n*3//8     # sell 3/8=90 ->150
n-=25         # 125
n+=12         # returns 137
n=n*2         # restock double 274
n-=n//4       # give away 1/4 -> 205.5? need integer; 274//4=68 ->206
wp("wLq5","A shop has 240 items. It sells three eighths of them, then sells 25 more. Then 12 items are returned. Then a restock DOUBLES the current stock. Then one quarter of the stock (rounded down) is donated. How many items remain?", 274-274//4)

# ---------- LONG-STRING exact counting (tokenizer-hard) ----------
S1="the quick brown fox jumps over the lazy dog while the eager beaver enters the deep green river every evening before the western breeze settles"
add("cLq1","cnt",f"How many times does the letter 'e' appear in the following text? Count carefully. Text: \"{S1}\" Give only the number.","numeric",{"key":S1.count("e"),"tol":0})
S2="mississippi river assessment session possesses less stress across massachusetts businesses"
add("cLq2","cnt",f"How many times does the letter 's' appear in the following text? Text: \"{S2}\" Give only the number.","numeric",{"key":S2.count("s"),"tol":0})
S3="she sells sea shells by the sea shore and the shells she sells are surely seashells for sure"
add("cLq3","cnt",f"How many words are in the following text, and give ONLY that word count. Text: \"{S3}\"","numeric",{"key":len(S3.split()),"tol":0})

buckets={}
for q in Q: buckets[q["bucket"]]=buckets.get(q["bucket"],0)+1
blob=json.dumps(Q,indent=2,ensure_ascii=False)
h=hashlib.sha256(blob.encode()).hexdigest()[:12]
open("questions3.json","w").write(blob)
# gold + block
def goldof(q):
    g,s=q["gtype"],q["gspec"]
    if g=="numeric": return str(s["key"])
    if g=="contains": return " and ".join(grp[0] for grp in s["all_any"])
    if g=="nameset": return ", ".join(s["key"]) if s["key"] else "none"
with open("runs/_gold3.txt","w") as f:
    for q in Q: f.write(f"### {q['id']}\n{goldof(q)}\n\n")
lines=["Answer ALL questions below. For each, output '### <id>' then ONLY the final answer, following its format.",""]
for q in Q: lines+= [f"### {q['id']}", q["prompt"], ""]
open("battery3_block.txt","w").write("\n".join(lines))
open("battery3_hash.txt","w").write(h+"\n")
print("v3 questions:",len(Q),"buckets:",buckets,"hash:",h)

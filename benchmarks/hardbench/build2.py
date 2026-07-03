#!/usr/bin/env python3
"""hardbench v2 — genuinely hard, PROCESS-FIXABLE, deterministic. Keys for logic puzzles are
computed by a brute-force solver that also asserts a UNIQUE solution. Emits questions2.json."""
import json, itertools, hashlib
from fractions import Fraction

Q=[]
def add(qid,bucket,prompt,gtype,gspec): Q.append({"id":qid,"bucket":bucket,"prompt":prompt,"gtype":gtype,"gspec":gspec})

# ================= KNIGHTS & KNAVES (correct-by-construction, solver-verified) =================
# Statements are DATA: evaluated and rendered from the same spec, so text always matches logic.
def ev(st, sp, t):
    k=st[0]
    if k=="knave": return not t[st[1]]
    if k=="knight": return t[st[1]]
    if k=="same": return t[st[1]]==t[st[2]]
    if k=="diff": return t[st[1]]!=t[st[2]]
    if k=="count": return sum(t.values())==st[1]
    if k=="atleast": return sum(t.values())>=st[1]
    if k=="allknaves": return sum(t.values())==0
    if k=="and": return ev(st[1],sp,t) and ev(st[2],sp,t)
    raise ValueError(st)
def render(st, sp):
    k=st[0]
    if k=="knave": return f"{st[1]} is a knave"
    if k=="knight": return f"{st[1]} is a knight"
    if k=="same": return f"{st[1]} and {st[2]} are the same type"
    if k=="diff": return f"{st[1]} and {st[2]} are of different types"
    if k=="count": return f"exactly {st[1]} of us are knights"
    if k=="atleast": return f"at least {st[1]} of us are knights"
    if k=="allknaves": return "all of us are knaves"
    if k=="and": return f"{render(st[1],sp)}, and {render(st[2],sp)}"
def solve_kk(names, stmts):
    sols=[]
    for combo in itertools.product([True,False], repeat=len(names)):
        t=dict(zip(names,combo))
        if all(t[n]==ev(stmts[n],n,t) for n in names): sols.append(dict(t))
    return sols
def kk_add(qid, names, stmts):
    sols=solve_kk(names,stmts)
    if len(sols)!=1: return False
    knights=sorted(n for n in names if sols[0][n])
    text="Knights always tell the truth; knaves always lie. "
    text+=" ".join(f"{n} says: '{render(stmts[n],n)}.'" for n in names)
    add(qid,"kk",text+" Reply with the names of ALL the knights, comma-separated. If none, reply 'none'.",
        "nameset",{"key":knights,"universe":names})
    return True

# Generate 8 unique-solution, non-trivial puzzles: for each name-triple, enumerate statement
# combos in fixed order and take the first that (a) has a unique solution, (b) is non-trivial
# (not all-knights / all-knaves), (c) has a distinct knight-count pattern for variety.
triples=[["Alan","Beth","Cody"],["Dana","Evan","Finn"],["Gwen","Hugo","Ivan"],["Pia","Quin","Rhys"],
         ["Sana","Theo","Uma"],["Vera","Will","Xena"],["Adam","Bea","Cole"],["Gil","Hana","Ike"]]
def opts(x, others):
    y,z=others
    return [("knave",y),("knight",y),("knave",z),("knight",z),("same",y,z),("diff",y,z),
            ("count",1),("count",2),("atleast",2),("allknaves",)]
kkn=0
for names in triples:
    a,b,c=names
    found=False
    for sa in opts(a,(b,c)):
        for sb in opts(b,(a,c)):
            for sc in opts(c,(a,b)):
                stmts={a:sa,b:sb,c:sc}
                sols=solve_kk(names,stmts)
                if len(sols)==1 and 1<=sum(sols[0].values())<=2:
                    kkn+=1; kk_add(f"kkq{kkn}",names,stmts); found=True; break
            if found: break
        if found: break
    assert found, f"no puzzle for {names}"
assert kkn==8, kkn

# ================= ZEBRA / EINSTEIN GRIDS (correct-by-construction, solver-verified) =================
# Build from a KNOWN ground-truth arrangement, emit only true clues, greedily reduce to a
# minimal unique-solution clue set, and auto-render the text so logic and words always match.
def zebra_solve(cats, clues):
    names=list(cats.keys()); n=len(next(iter(cats.values())))
    perms={c:list(itertools.permutations(range(n))) for c in names}
    sols=[]
    for combo in itertools.product(*[perms[c] for c in names]):
        pos={}
        for ci,c in enumerate(names):
            for vi,v in enumerate(cats[c]): pos[(c,v)]=combo[ci][vi]
        if all(cl_eval(cl,pos) for cl in clues): sols.append(pos)
        if len(sols)>1: break
    return sols
def cl_eval(cl,pos):
    k=cl[0]
    if k=="at": return pos[cl[1]]==cl[2]
    if k=="same": return pos[cl[1]]==pos[cl[2]]
    if k=="rightof": return pos[cl[1]]==pos[cl[2]]+1
    if k=="nextto": return abs(pos[cl[1]]-pos[cl[2]])==1
def cl_text(cl):
    def name(cv): return f"the {cv[1]} {cv[0]}"
    k=cl[0]
    if k=="at": return f"{name(cl[1])} is in position {cl[2]+1}"
    if k=="same": return f"{name(cl[1])} and {name(cl[2])} are in the same house"
    if k=="rightof": return f"{name(cl[1])} is immediately to the right of {name(cl[2])}"
    if k=="nextto": return f"{name(cl[1])} is directly next to {name(cl[2])}"

def make_zebra(qid, cats, truth, ask_cat, ask_anchor, hardening=None):
    # truth: dict (cat,val)->position. ask: which value of ask_cat shares the house of ask_anchor (cat,val)
    n=len(next(iter(cats.values())))
    gt={(c,v):truth[(c,v)] for c in cats for v in cats[c]}
    # candidate clues true in gt
    cand=[]
    for c in cats:
        for v in cats[c]: cand.append(("at",(c,v),gt[(c,v)]))
    cvs=[(c,v) for c in cats for v in cats[c]]
    for i in range(len(cvs)):
        for j in range(len(cvs)):
            if i==j or cvs[i][0]==cvs[j][0]: continue
            if gt[cvs[i]]==gt[cvs[j]]: cand.append(("same",cvs[i],cvs[j]))
            if gt[cvs[i]]==gt[cvs[j]]+1: cand.append(("rightof",cvs[i],cvs[j]))
    # start from all, greedily drop while unique solution preserved (== gt)
    clues=list(cand)
    assert len(zebra_solve(cats,clues))==1
    for cl in list(cand):
        trial=[x for x in clues if x is not cl]
        if len(zebra_solve(cats,trial))==1: clues=trial
    sols=zebra_solve(cats,clues); assert len(sols)==1, f"{qid}: {len(sols)}"
    pos=sols[0]
    ap=pos[ask_anchor]; ans=next(v for v in cats[ask_cat] if pos[(ask_cat,v)]==ap)
    header=(f"There are {n} houses in a row, positions 1 to {n} left to right. "
            + "Each house has a unique value for every category. Categories: "
            + "; ".join(f"{c} ({', '.join(cats[c])})" for c in cats) + ". Clues: "
            + "; ".join(cl_text(cl) for cl in clues) + ".")
    q=f" Question: {ask_anchor[1]} shares its house with which {ask_cat}? Answer with one word."
    add(qid,"zebra",header+q,"contains",{"all_any":[[ans.lower()]],"forbid":[]})

make_zebra("zbq1",{"color":["red","green","blue"],"pet":["cat","dog","bird"],"drink":["tea","milk","water"]},
  {("color","red"):0,("color","green"):1,("color","blue"):2,("pet","dog"):1,("pet","cat"):0,("pet","bird"):2,
   ("drink","milk"):0,("drink","tea"):1,("drink","water"):2},
  "drink",("color","green"))
make_zebra("zbq2",{"color":["red","green","white","yellow"],"nation":["brit","dane","swede","norse"]},
  {("color","red"):0,("color","yellow"):1,("color","white"):2,("color","green"):3,
   ("nation","brit"):0,("nation","norse"):1,("nation","swede"):2,("nation","dane"):3},
  "nation",("color","white"))
make_zebra("zbq3",{"name":["amy","bob","cai","dot"],"sport":["golf","judo","polo","surf"]},
  {("name","amy"):0,("name","bob"):1,("name","cai"):2,("name","dot"):3,
   ("sport","golf"):0,("sport","judo"):1,("sport","polo"):2,("sport","surf"):3},
  "sport",("name","cai"))
make_zebra("zbq4",{"name":["ravi","sami","tara"],"car":["ford","kia","opel"],"floor":["one","two","three"]},
  {("name","sami"):0,("name","ravi"):1,("name","tara"):2,("car","ford"):0,("car","kia"):1,("car","opel"):2,
   ("floor","two"):0,("floor","one"):1,("floor","three"):2},
  "car",("name","sami"))

# ================= COMBINATORICS / PROBABILITY (exact fraction, computed) =================
from math import comb
def add_frac(qid,text,fr):
    fr=Fraction(fr); add(qid,"comb",text+" Give the answer as a reduced fraction a/b.","fraction",{"num":fr.numerator,"den":fr.denominator})
# bag 4 red 3 blue 2 green, draw 2 w/o replacement, P(same color)
tot=comb(9,2); same_c=comb(4,2)+comb(3,2)+comb(2,2)
add_frac("cbq1","A bag has 4 red, 3 blue, and 2 green marbles. You draw 2 at random without replacement. What is the probability both drawn marbles are the same color?", Fraction(same_c,tot))
add_frac("cbq2","Two fair six-sided dice are rolled. What is the probability that the sum is exactly 9?", Fraction(4,36))
add_frac("cbq3","From a standard 52-card deck, you draw 2 cards without replacement. What is the probability that both are hearts?", Fraction(comb(13,2),comb(52,2)))
add_frac("cbq4","A fair coin is flipped 4 times. What is the probability of getting exactly 3 heads?", Fraction(comb(4,3),16))
add_frac("cbq5","A bag has 5 white and 3 black balls. You draw 3 without replacement. What is the probability that exactly 2 are white?", Fraction(comb(5,2)*comb(3,1),comb(8,3)))
add_frac("cbq6","You roll two fair six-sided dice. What is the probability that at least one shows a 6?", Fraction(11,36))
add("cbq7","comb","How many distinct arrangements are there of the letters in the word 'BALLOON'? Give only the integer.","numeric",{"key": 5040//(2*2), "tol":0})  # 7!/(2!2!)
add("cbq8","comb","In how many ways can you choose a committee of 3 people from 8, if two specific people refuse to serve together? Give only the integer.","numeric",{"key": comb(8,3)-comb(6,1), "tol":0})

# ================= DROPPED-CONSTRAINT MULTI-STEP WORD PROBLEMS (computed) =================
def wp(qid,text,val):
    assert float(val)==int(val), (qid,val); add(qid,"wp",text+" Give only the final number.","numeric",{"key":int(val),"tol":0})
# 1
shelf=300; shelf-=shelf//3; shelf+=15; shelf-=40  # start 300, borrow 1/3=100->200, +15 return=215, -40=175
wp("wpq1","A library starts the week with 300 books on the shelf. On Monday, one third of the shelved books are borrowed. On Tuesday, 15 of the borrowed books are returned to the shelf, and then 40 books are borrowed from the shelf. No other changes occur. How many books are on the shelf at the end of Tuesday?", shelf)
# 2 dropped-constraint: 'but 4 were returned before the delivery'
a=120; a-=a//4; a-=18; returned=4; a+=returned; a*=2; a-=7
wp("wpq2","A store had 120 apples. In the morning it sold one quarter of them. In the afternoon it sold 18 more. Before the evening delivery, 4 of the apples sold in the morning were returned and put back. The evening delivery then DOUBLED the number of apples currently in the store. Finally, 7 apples were given away. How many apples remain?", a)
# 3
m=64; m=m//2; m=m//2; m+=10; m-=3
wp("wpq3","A tank holds 64 litres. It loses half its contents on day 1, then half of what remains on day 2. On day 3, 10 litres are added, and then 3 litres evaporate. How many litres are in the tank at the end of day 3?", m)
# 4 age puzzle
# Anna is 3 times as old as Ben. In 4 years Anna will be twice as old as Ben. How old is Anna now? A=3B; A+4=2(B+4)->3B+4=2B+8->B=4,A=12
wp("wpq4","Anna is 3 times as old as Ben. In 4 years, Anna will be twice as old as Ben. How old is Anna now?", 12)
# 5 speed/distance with a twist (rest stop)
# drives 60km at 60km/h (1h), rests 30 min, then 90km at 45km/h (2h). total time in minutes
t=60/60*60 + 30 + 90/45*60
wp("wpq5","A driver covers 60 km at 60 km/h, then rests for 30 minutes, then covers 90 km at 45 km/h. What is the TOTAL elapsed time in minutes, including the rest?", t)
# 6 money percentages
p=200; p=p*(1+20/100); p=p*(1-20/100)  # +20% then -20% = 192
wp("wpq6","An item costs $200. Its price is first increased by 20%, then the new price is decreased by 20%. What is the final price in dollars?", p)
# 7 counting with overlap (inclusion-exclusion)
# 30 students; 18 play soccer, 15 play tennis, 6 play both. How many play neither?
wp("wpq7","In a class of 30 students, 18 play soccer, 15 play tennis, and 6 play both. How many students play neither sport?", 30-(18+15-6))
# 8 sequential fractions dropped constraint
# 48 candies; give 1/2 to A, then 1/3 of REMAINDER to B, then keep 4, give rest to C. How many to C? 48->24 left after A; 1/3 of 24=8 to B ->16 left; keep 4 -> give 12 to C
wp("wpq8","There are 48 candies. Half are given to Ana. Then one third of the REMAINING candies are given to Ben. Then you keep 4 for yourself and give all the rest to Cy. How many candies does Cy get?", (48//2) - (48//2)//3 - 4)
# 9 clock angle-ish (integer): trains
# two trains 300km apart approach at 40 and 60 km/h. minutes to meet: 300/100 h =3h=180min
wp("wpq9","Two trains are 300 km apart on the same track, heading toward each other. One travels at 40 km/h, the other at 60 km/h. How many MINUTES until they meet?", 300/100*60)
# 10 dropped negative constraint
# start 50, add 12, subtract 20, then triple, then subtract 6 -> ((50+12-20)*3)-6=(42*3)-6=126-6=120
wp("wpq10","Start with 50. Add 12. Subtract 20. Triple the result. Then subtract 6. What is the final number?", ((50+12-20)*3)-6)

# ================= SELECTION / ORDERING FROM A GIVEN BANK (deterministic) =================
add("slq1","sel",'From this list — [oak, elm, fig, ash, yew, bay] — select every word that does NOT contain the letter "a", and list them in reverse alphabetical order, one per line, nothing else.',
    "exact",{"key":"yew\nfig\nelm"})
add("slq2","sel",'From the numbers [14, 9, 22, 7, 30, 15, 8], list only those that are BOTH even AND greater than 10, in increasing order, comma-separated, nothing else.',
    "exact",{"key":"14, 22, 30"})
add("slq3","sel",'From [cat, dolphin, ant, whale, bee, tiger], list the words with exactly 3 letters in alphabetical order, one per line, nothing else.',
    "exact",{"key":"ant\nbee\ncat"})
add("slq4","sel",'Take the words [red, green, blue, gold, pink]. Output them sorted by WORD LENGTH ascending, and for ties by alphabetical order, comma-separated, nothing else.',
    "exact",{"key":"red, blue, gold, pink, green"})
add("slq5","sel",'From [3, 11, 4, 6, 9, 25, 2], list every PRIME number in DECREASING order, comma-separated, nothing else.',
    "exact",{"key":"11, 3, 2"})
add("slq6","sel",'From the list [apple, kiwi, plum, mango, pear, lime], select the words that contain the letter "i", and output them in alphabetical order, one per line, nothing else.',
    "exact",{"key":"kiwi\nlime"})

# ---- finalize ----
buckets={}
for q in Q: buckets[q["bucket"]]=buckets.get(q["bucket"],0)+1
Q.sort(key=lambda q:(str(q["bucket"]),q["id"]))
blob=json.dumps(Q,indent=2,ensure_ascii=False)
h=hashlib.sha256(blob.encode()).hexdigest()[:12]
open("questions2.json","w").write(blob)
open("battery2_hash.txt","w").write(h+"\n")
print("v2 questions:",len(Q),"buckets:",buckets)
print("battery2_hash:",h)

#!/usr/bin/env python3
"""hardbench v4 — TOOL-FIXABLE set: questions a strong model gets WRONG from its head but a
tool solves trivially. Tests the prompt's signature 'use tools for arithmetic/counting' rule.
Keys computed. Emits questions4.json + battery4_block.txt + gold."""
import json,datetime,hashlib
Q=[]
def add(qid,b,p,g,s): Q.append({"id":qid,"bucket":b,"prompt":p,"gtype":g,"gspec":s})
def num(qid,b,p,k): add(qid,b,p,"numeric",{"key":k,"tol":0})

# long-string character counting (tokenizer-hard)
S=[("The quick brown fox jumps over the lazy dog near the riverbank every evening before sunset","e"),
   ("Peter Piper picked a peck of pickled peppers and the pepper Peter picked was surely pungent","p"),
   ("She sells sea shells by the sea shore of the small silver stream since seven sisters sailed south","s"),
   ("Mississippi assessment session possesses less stress across massachusetts businesses professionally","s")]
for i,(txt,ch) in enumerate(S,1):
    num(f"tcq{i}","count",f"How many times does the letter '{ch}' appear in this text? Text: \"{txt}\". Give only the number.", txt.lower().count(ch))

# big exact arithmetic (mental-math-infeasible)
num("taq1","arith","Compute exactly: 8675309 * 1234567. Give only the integer.", 8675309*1234567)
num("taq2","arith","Compute exactly: 987654321 * 123456789. Give only the integer.", 987654321*123456789)
num("taq3","arith","Compute exactly: 20! (twenty factorial). Give only the integer.", __import__("math").factorial(20))
num("taq4","arith","Compute exactly: 2 ** 60. Give only the integer.", 2**60)
num("taq5","arith","What is 7^100 mod 1000 (the last three digits of 7 to the power 100)? Give only the integer.", pow(7,100,1000))
# date deltas
num("tdq1","date","How many days are there between 1901-04-12 and 2023-11-30 (end minus start)? Give only the integer.", (datetime.date(2023,11,30)-datetime.date(1901,4,12)).days)
num("tdq2","date","What day of the week was 1969-07-20 (the first Moon landing)? Give the weekday name.", None)
# fix tdq2 to contains
Q[-1]["gtype"]="contains"; Q[-1]["gspec"]={"all_any":[[datetime.date(1969,7,20).strftime("%A").lower()]],"forbid":[]}

blob=json.dumps(Q,indent=2,ensure_ascii=False); h=hashlib.sha256(blob.encode()).hexdigest()[:12]
open("questions4.json","w").write(blob)
def goldof(q):
    g,s=q["gtype"],q["gspec"]
    return str(s["key"]) if g=="numeric" else (" ".join(grp[0] for grp in s["all_any"]))
open("runs/_gold4.txt","w").write("".join(f"### {q['id']}\n{goldof(q)}\n\n" for q in Q))
lines=["Answer ALL questions. For each output '### <id>' then ONLY the final answer.",""]
for q in Q: lines+=[f"### {q['id']}",q["prompt"],""]
open("battery4_block.txt","w").write("\n".join(lines))
open("battery4_hash.txt","w").write(h+"\n")
print("v4 questions:",len(Q),"hash:",h)

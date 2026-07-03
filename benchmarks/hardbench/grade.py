#!/usr/bin/env python3
"""Deterministic grader. Parses an agent answer file split by '### <qid>' headers and
grades each question by its typed grader. Usage: python3 grade.py <answers_file> [--json]"""
import json, re, sys, io, contextlib

COUNTRIES = set("""chile peru egypt fiji cyprus sweden turkey mexico greece belgium congo benin
niger morocco lesotho comoros kosovo tuvalu yemen oman djibouti germany denmark finland norway
iceland ireland poland portugal spain italy france china japan brazil bolivia colombia ecuador
uruguay venezuela kenya nigeria uganda sudan chad mali togo ghana guinea senegal zimbabwe zambia
mozambique lebanon jordan israel iraq iran syria kuwait qatar bhutan nepal laos vietnam thailand
myanmar cambodia mongolia russia ukraine belarus romania bulgaria serbia croatia slovenia slovakia
hungary austria switzerland netherlands luxembourg monaco malta cuba jamaica haiti honduras panama
guatemala nicaragua paraguay argentina""".split())
# no-'a' subset is validated at runtime by the grader (letter check), COUNTRIES gates realness.

def norm(s): return re.sub(r"\s+"," ",s.strip())
def low(s): return norm(s).lower()

def find_number(text):
    t = text.replace(",", "")
    m = re.findall(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?", t)
    return m  # list of numeric strings

def g_numeric(ans, spec):
    key = float(spec["key"]); tol = float(spec["tol"])
    nums = find_number(ans)
    if not nums: return False
    # accept if ANY number in the answer matches (models often restate); but prefer the last.
    for ns in [nums[-1]] + nums:
        try:
            v = float(ns)
        except: continue
        if abs(v-key) <= tol + 1e-9: return True
        if key==int(key) and abs(v-int(key))<=tol+1e-9: return True
    return False

def g_contains(ans, spec):
    t = low(ans)
    for grp in spec["all_any"]:
        if not any(low(x) in t for x in grp): return False
    for f in spec.get("forbid", []):
        if low(f) in t: return False
    return True

def g_exact(ans, spec):
    return low(ans).rstrip(".") == low(spec["key"]).rstrip(".")

def g_pairs(ans, spec):
    t = low(ans)
    lines = [l for l in ans.splitlines() if l.strip()]
    for name, attrs in spec["pairs"].items():
        line = next((l.lower() for l in lines if name in l.lower()), None)
        if line is None: return False
        if not all(a in line for a in attrs): return False
    return True

def g_no_letter_lines(ans, spec):
    n=spec["n"]; letter=spec["letter"].lower(); any_word=spec.get("any_word",False)
    lines=[l.strip() for l in ans.splitlines() if l.strip()]
    lines=[re.sub(r"^[\-\*\d\.\)\s]+","",l) for l in lines]  # strip bullets/numbering
    lines=[l for l in lines if l]
    if len(lines)!=n: return False
    for l in lines:
        core=re.sub(r"[^a-z ]","",l.lower())
        if letter in core: return False
        if not any_word and core.strip() not in COUNTRIES: return False
        if not core.strip(): return False
    return True

def g_starts_with(ans, spec):
    toks=[t.strip() for t in norm(ans).split(spec["sep"]) if t.strip()]
    if len(toks)!=spec["n"]: return False
    return all(re.sub(r"[^a-z]","",t.lower()).startswith(spec["letter"]) and re.sub(r"[^a-z]","",t) for t in toks)

def g_countdown(ans, spec):
    seq=[str(i) for i in range(spec["start"], spec["stop"]-1, -1)]
    got=re.sub(r"\s","",norm(ans))
    return got in (",".join(seq), ",".join(seq)+".", " ".join(seq))

def g_sorted_lines(ans, spec):
    lines=[l.strip() for l in ans.splitlines() if l.strip()]
    lines=[re.sub(r"^[\-\*\d\.\)\s]+","",l).strip() for l in lines]
    lines=[l for l in lines if l]
    if len(lines)!=spec["n"]: return False
    low_l=[l.lower() for l in lines]
    return all(re.fullmatch(r"[a-z ]+",l) for l in low_l) and low_l==sorted(low_l)

def extract_code(text):
    m=re.search(r"```(?:python)?\s*(.*?)```", text, re.S)
    return m.group(1) if m else text

def g_code(ans, spec):
    from code_tests import TESTS
    fn=spec["fn"]; tests=TESTS[fn]
    src=extract_code(ans)
    ns={}
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(src, ns)
    except Exception:
        return False
    # find the callable: the one matching arg count / or any defined function
    cand=[v for k,v in ns.items() if callable(v) and not k.startswith("__")]
    if not cand: return False
    # prefer a function that passes; try each candidate
    for f in cand:
        ok=True
        try:
            for args, exp in tests:
                with contextlib.redirect_stdout(io.StringIO()):
                    if f(*args)!=exp: ok=False; break
        except Exception:
            ok=False
        if ok: return True
    return False

def g_fraction(ans, spec):
    from fractions import Fraction
    target=Fraction(spec["num"], spec["den"])
    t=ans.replace(",", "")
    m=re.search(r"(-?\d+)\s*/\s*(\d+)", t)
    if m:
        try:
            if Fraction(int(m.group(1)), int(m.group(2)))==target: return True
        except: pass
    # also accept exact decimal
    for ns in find_number(t):
        try:
            if abs(float(ns)-float(target))<1e-6: return True
        except: pass
    return False

def g_nameset(ans, spec):
    key=set(n.lower() for n in spec["key"]); uni=spec["universe"]
    t=low(ans)
    if not key and ("none" in t or not any(n.lower() in t for n in uni)): return True
    knights=set()
    for n in uni:
        nl=n.lower()
        if nl in t and not re.search(re.escape(nl)+r"[^.]{0,20}knave", t):
            knights.add(nl)
    return knights==key

GRADERS={"numeric":g_numeric,"contains":g_contains,"exact":g_exact,"pairs":g_pairs,
 "no_letter_lines":g_no_letter_lines,"starts_with":g_starts_with,"countdown":g_countdown,
 "sorted_lines":g_sorted_lines,"code":g_code,"fraction":g_fraction,"nameset":g_nameset}

def parse_answers(text):
    out={}
    parts=re.split(r"(?mi)^\s*#{2,3}\s*([A-Za-z][A-Za-z0-9]*q\d+)\s*$", text)
    # parts: [pre, qid, body, qid, body, ...]
    for i in range(1,len(parts),2):
        qid=parts[i].lower(); body=parts[i+1] if i+1<len(parts) else ""
        out[qid]=body.strip()
    return out

def grade_file(path, qfile="questions.json"):
    Q={q["id"]:q for q in json.load(open(qfile))}
    text=open(path, encoding="utf-8", errors="replace").read()
    ans=parse_answers(text)
    res={}
    for qid,q in Q.items():
        a=ans.get(qid.lower(),"")
        ok=bool(a) and GRADERS[q["gtype"]](a, q["gspec"])
        res[qid]={"bucket":q["bucket"],"pass":ok,"answered":bool(a)}
    return res

if __name__=="__main__":
    path=sys.argv[1]
    qfile=next((a.split("=")[1] for a in sys.argv if a.startswith("--q=")), "questions.json")
    res=grade_file(path, qfile)
    npass=sum(1 for r in res.values() if r["pass"])
    if "--json" in sys.argv:
        print(json.dumps(res))
    else:
        for qid in sorted(res):
            print(f"{qid} b{res[qid]['bucket']} {'PASS' if res[qid]['pass'] else ('----' if res[qid]['answered'] else 'MISS')}")
        print(f"TOTAL {npass}/{len(res)}")

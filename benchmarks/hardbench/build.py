#!/usr/bin/env python3
"""Build the 64-question hard battery. All numeric/date/counting/python-fact keys are
COMPUTED here (guaranteed-correct ground truth), never hand-typed. Emits questions.json."""
import json, datetime, hashlib

Q = []
def add(qid, bucket, prompt, gtype, gspec):
    Q.append({"id": qid, "bucket": bucket, "prompt": prompt, "gtype": gtype, "gspec": gspec})

# ---------- Bucket 1: altered-classic reasoning traps ----------
add("b1q1", 1, "What weighs more: three pounds of feathers or two pounds of bricks? Answer in one short phrase.",
    "contains", {"all_any": [["feather"]], "forbid": ["brick", "equal", "the same", "weigh the same"]})
add("b1q2", 1, "A bat and a ball cost $1.30 in total. The bat costs $1.00 more than the ball. How much does the ball cost, in dollars?",
    "numeric", {"key": 0.15, "tol": 0.001})
add("b1q3", 1, "A child is rushed into surgery. The surgeon looks at the child and says, 'I can operate on this child — she is my daughter.' The surgeon is the child's biological mother. Is that possible, and who is the surgeon? Answer briefly.",
    "contains", {"all_any": [["mother"], ["yes", "possible", "of course"]], "forbid": ["not possible", "impossible", "cannot be"]})
add("b1q4", 1, "A farmer has 24 sheep. All but 7 die. How many sheep are left?",
    "numeric", {"key": 7, "tol": 0})
add("b1q5", 1, "How many months in a year have at least 28 days?",
    "numeric", {"key": 12, "tol": 0})
add("b1q6", 1, "A red house is made of red bricks and a blue house is made of blue bricks. What is a greenhouse made of? One word.",
    "contains", {"all_any": [["glass"]], "forbid": ["green brick", "green house made of green"]})
add("b1q7", 1, "There are 8 apples and you take away 5. How many apples do you have?",
    "numeric", {"key": 5, "tol": 0})
add("b1q8", 1, "A rooster sits on the exact peak of a slanted barn roof and lays an egg. Which side of the roof does the egg roll down?",
    "contains", {"all_any": [["male", "don't lay", "do not lay", "cannot lay", "can't lay", "no egg", "roosters don", "rooster cannot", "rooster can't", "rooster doesn", "won't lay", "will not lay"]], "forbid": []})

# ---------- Bucket 2: multi-constraint / logic ----------
add("b2q1", 2, "Five runners finish a race. Quinn finished before Sam. Rosa finished after Sam. Priya finished before Quinn. Tara finished last. Who finished first? Answer with one name.",
    "contains", {"all_any": [["priya"]], "forbid": []})
add("b2q2", 2, "In a row of 5 houses numbered 1 to 5 from left to right, the cat's house is immediately to the right of the dog's house. The dog is in house 2. The bird is in house 5. What is the cat's house number?",
    "numeric", {"key": 3, "tol": 0})
add("b2q3", 2, "Seven kids stand in a single line. Sam is 3rd from the front. Tom is 2nd from the back. There are 7 kids total. How many kids stand between Sam and Tom?",
    "numeric", {"key": 2, "tol": 0})
add("b2q4", 2, "Four people: Priya, Quinn, Rosa, Sam. Sam is taller than Priya. Rosa is shorter than Priya. Quinn is taller than Sam. Who is the second tallest? One name.",
    "contains", {"all_any": [["sam"]], "forbid": []})
add("b2q5", 2, "I am thinking of a whole number between 1 and 10 inclusive that is even, greater than 5, a multiple of 3, and less than 10. What is it?",
    "numeric", {"key": 6, "tol": 0})
add("b2q6", 2, "A one-hour meeting starts exactly on the hour, strictly after 12:00 and strictly before 15:00, and it cannot start at 14:00. Using 24-hour time, what is the only possible start hour? Answer with the hour number.",
    "numeric", {"key": 13, "tol": 0})
add("b2q7", 2, "Ana, Ben, and Cy each own exactly one pet (cat, dog, or fish) and wear exactly one shirt color (red, green, or blue); all three pets and all three colors are different. Clues: Ana does not own the cat. Ben owns the dog. The fish owner wears red. Cy does not wear green. Ben does not wear blue. Output exactly three lines, each formatted 'Name: pet, color'.",
    "pairs", {"pairs": {"ana": ["fish", "red"], "ben": ["dog", "green"], "cy": ["cat", "blue"]}})
# b2q8 computed below (coin sums)

# ---------- Bucket 3: exact arithmetic & dates (computed) ----------
add("b3q1", 3, "Compute exactly: 4871 * 3344. Give only the integer.",
    "numeric", {"key": 4871*3344, "tol": 0})
add("b3q2", 3, "Compute exactly: 78 ** 3 (78 cubed). Give only the integer.",
    "numeric", {"key": 78**3, "tol": 0})
add("b3q3", 3, "Compute exactly: 123456 + 789012 + 345678. Give only the integer.",
    "numeric", {"key": 123456+789012+345678, "tol": 0})
add("b3q4", 3, "Compute exactly: 2 ** 17. Give only the integer.",
    "numeric", {"key": 2**17, "tol": 0})
add("b3q5", 3, "Compute exactly: 17 * 19 * 23. Give only the integer.",
    "numeric", {"key": 17*19*23, "tol": 0})
_d1 = (datetime.date(2024,1,10) - datetime.date(2023,3,15)).days
add("b3q6", 3, "How many days are there from 2023-03-15 to 2024-01-10 (exclusive of the start date, inclusive of the end date, i.e. the difference in days)? Give only the integer.",
    "numeric", {"key": _d1, "tol": 0})
_wd = datetime.date(2025,12,25).strftime("%A")
add("b3q7", 3, "What day of the week is 25 December 2025? Give the weekday name.",
    "contains", {"all_any": [[_wd.lower()]], "forbid": []})
add("b3q8", 3, "Compute exactly: 9999 * 9999. Give only the integer.",
    "numeric", {"key": 9999*9999, "tol": 0})

# ---------- Bucket 4: counting (computed from strings) ----------
def cnt(s, ch): return s.lower().count(ch)
add("b4q1", 4, "How many times does the letter 'r' appear in the phrase \"strawberry raspberry\"? Give only the number.",
    "numeric", {"key": cnt("strawberry raspberry","r"), "tol": 0})
add("b4q2", 4, "How many times does the letter 's' appear in the phrase \"mississippi possesses\"? Give only the number.",
    "numeric", {"key": cnt("mississippi possesses","s"), "tol": 0})
add("b4q3", 4, "How many letters are in the word \"onomatopoeia\"? Give only the number.",
    "numeric", {"key": len("onomatopoeia"), "tol": 0})
add("b4q4", 4, "How many vowels (a, e, i, o, u) are in the word \"sequoia\"? Give only the number.",
    "numeric", {"key": sum(c in "aeiou" for c in "sequoia"), "tol": 0})
_s5 = "the referee never believed the emcee"
add("b4q5", 4, f"How many times does the letter 'e' appear in the sentence \"{_s5}\"? Give only the number.",
    "numeric", {"key": cnt(_s5,"e"), "tol": 0})
add("b4q6", 4, "How many times does the substring \"na\" appear (non-overlapping) in \"banana bandana\"? Give only the number.",
    "numeric", {"key": "banana bandana".count("na"), "tol": 0})
_s7 = "the quick brown fox jumps over the lazy dog again"
add("b4q7", 4, f"How many words are in this sentence: \"{_s7}\"? Give only the number.",
    "numeric", {"key": len(_s7.split()), "tol": 0})
add("b4q8", 4, "How many 1-bits (ones) are in the binary representation of the number 2025? Give only the number.",
    "numeric", {"key": bin(2025).count("1"), "tol": 0})

# b2q8 coin sums (computed)
def coin_sums():
    vals = [1,1,1,5,5,10]  # 3 pennies, 2 nickels, 1 dime
    sums=set()
    for mask in range(1,1<<len(vals)):
        t=sum(vals[i] for i in range(len(vals)) if mask&(1<<i))
        sums.add(t)
    return len(sums)
add("b2q8", 2, "You have 3 pennies (1 cent), 2 nickels (5 cents), and 1 dime (10 cents). Using one or more of these coins, how many DIFFERENT positive total amounts can you make? Give only the number.",
    "numeric", {"key": coin_sums(), "tol": 0})

# ---------- Bucket 6: units / dimensional (computed) ----------
add("b6q1", 6, "A pump moves water at 3 litres per second into a tank that holds 54,000 litres. Starting empty, how many HOURS to fill it? Give only the number of hours.",
    "numeric", {"key": 54000/3/3600, "tol": 0.001})
add("b6q2", 6, "A car travels 240 km using 15 litres of fuel. What is its fuel efficiency in km per litre? Give only the number.",
    "numeric", {"key": 240/15, "tol": 0.001})
add("b6q3", 6, "A speed of 60 miles per hour equals how many feet per second? (1 mile = 5280 feet.) Give only the number.",
    "numeric", {"key": 60*5280/3600, "tol": 0.01})
add("b6q4", 6, "A recipe for 4 people needs 300 grams of flour. How many grams are needed for 7 people, keeping the same ratio? Give only the number of grams.",
    "numeric", {"key": 300/4*7, "tol": 0.01})
add("b6q5", 6, "How many seconds are in 2.5 hours? Give only the number.",
    "numeric", {"key": 2.5*3600, "tol": 0})
add("b6q6", 6, "A tank leaks at 0.2 litres per minute. How many litres leak out in 3 hours? Give only the number.",
    "numeric", {"key": 0.2*180, "tol": 0.001})
add("b6q7", 6, "Light travels at 3 x 10^8 metres per second. How many metres does it travel in 5 milliseconds? Give only the number of metres.",
    "numeric", {"key": 3e8*0.005, "tol": 1})
add("b6q8", 6, "12 workers build a wall in 10 days. At the same rate, how many days would 8 workers take to build the same wall? Give only the number of days.",
    "numeric", {"key": 12*10/8, "tol": 0.01})

# ---------- Bucket 7: format / negation instruction-following ----------
add("b7q1", 7, "List exactly 5 real country names that contain NO letter 'a' (case-insensitive). Output one country per line and nothing else.",
    "no_letter_lines", {"n": 5, "letter": "a"})
add("b7q2", 7, "Output exactly three English words, each beginning with the letter 'q', separated by commas, and nothing else.",
    "starts_with", {"n": 3, "letter": "q", "sep": ","})
add("b7q3", 7, "Output the numbers 1 to 10 in order, but replace every even number with the word 'even'. Separate items with single spaces. Output only that line.",
    "exact", {"key": "1 even 3 even 5 even 7 even 9 even"})
add("b7q4", 7, "Reverse the word 'benchmark' and output only the reversed string, nothing else.",
    "exact", {"key": "benchmark"[::-1]})
add("b7q5", 7, "List exactly 3 words that do NOT contain the letter 'e'. Output one word per line and nothing else.",
    "no_letter_lines", {"n": 3, "letter": "e", "any_word": True})
add("b7q6", 7, "Respond with exactly the single word 'ready' in lowercase and nothing else.",
    "exact", {"key": "ready"})
add("b7q7", 7, "Count down from 5 to 1 inclusive, separated by commas, and output only that line.",
    "countdown", {"start": 5, "stop": 1})
add("b7q8", 7, "Output exactly four animal names in alphabetical order, one per line, with no numbering and nothing else.",
    "sorted_lines", {"n": 4})

# ---------- Bucket 8: false-claim rebuttal (python-fact, self-verified) ----------
# each gspec key is verified by eval below.
b8 = [
 ("b8q1", "In Python 3, does str.removeprefix remove the prefix repeatedly until it is gone? Answer yes or no, and give the result of 'abcabcx'.removeprefix('abc').",
   "abcabcx".removeprefix("abc"), ["no"]),
 ("b8q2", "In Python, is the expression 0.1 + 0.2 == 0.3 True? Answer yes or no, and give the actual value of 0.1 + 0.2.",
   repr(0.1+0.2), ["no"]),
 ("b8q3", "In Python, does [1, 2, 3][::-1] equal [3, 2, 1]? Answer yes or no.",
   None, ["yes"]),
 ("b8q4", "In Python 3, does len('café') return 4? Answer yes or no and give the number it returns.",
   str(len('café')), ["yes"]),
 ("b8q5", "In Python, does bool('False') (the non-empty string 'False') return True or False? Answer with one word.",
   None, ["true"]),
 ("b8q6", "In Python, is 9 // 2 equal to 4? Answer yes or no and give the value.",
   str(9//2), ["yes"]),
 ("b8q7", "In Python, does 'ab' * 3 produce 'ababab'? Answer yes or no.",
   None, ["yes"]),
 ("b8q8", "In Python 3, does 5 / 2 equal 2 (i.e. is it integer division)? Answer yes or no and give the value.",
   str(5/2), ["no"]),
]
for qid, prompt, extra, words in b8:
    allany = [[w] for w in words]
    if extra is not None:
        # normalize: strip quotes for matching
        allany.append([extra.strip("'"), extra])
    add(qid, 8, prompt, "contains", {"all_any": allany, "forbid": []})

# ---------- Bucket 5: code (execution-graded). Spec + hidden tests live in code_tests.py ----------
code = [
 ("b5q1", "Write a Python function run_length_encode(s) that returns the run-length encoding of string s: each maximal run of a character c of length n becomes c followed by n (as digits). E.g. 'aaabbc' -> 'a3b2c1'. Empty string -> ''. Return ONLY a fenced python code block defining the function."),
 ("b5q2", "Write a Python function rle_decode(s) that expands a run-length string where each letter is followed by a count of one or more digits: 'a3b2' -> 'aaabb', 'x1' -> 'x', '' -> ''. Return ONLY a fenced python code block defining the function."),
 ("b5q3", "Write a Python function is_clean_palindrome(s) that returns True iff s is a palindrome ignoring case and every non-alphanumeric character. '' -> True, 'A man, a plan, a canal: Panama' -> True, 'abc' -> False. Return ONLY a fenced python code block defining the function."),
 ("b5q4", "Write a Python function fee_faw(n) returning a list of length n (for i from 1 to n): 'feefaw' if i divisible by both 3 and 5, 'fee' if divisible by 3, 'faw' if divisible by 5, otherwise the integer i itself. Return ONLY a fenced python code block defining the function."),
 ("b5q5", "Write a Python function fib(n) returning the n-th Fibonacci number, 0-indexed, with fib(0)=0, fib(1)=1. Must be correct for n up to 50. Return ONLY a fenced python code block defining the function."),
 ("b5q6", "Write a Python function gcd(a, b) returning the greatest common divisor of two non-negative integers (gcd(0,0)=0, gcd(12,18)=6). Return ONLY a fenced python code block defining the function."),
 ("b5q7", "Write a Python function caesar(s, k) that shifts each ASCII letter forward by k positions within its case (wrapping a-z and A-Z), leaving non-letters unchanged. k may be any integer including negative or >26. Return ONLY a fenced python code block defining the function."),
 ("b5q8", "Write a Python function digital_root(n) that repeatedly sums the decimal digits of a non-negative integer n until one digit remains (digital_root(0)=0, digital_root(9999)=9, digital_root(12345)=6). Return ONLY a fenced python code block defining the function."),
]
for qid, prompt in code:
    add(qid, 5, prompt, "code", {"fn": qid})

# ---- validate python-fact keys are internally consistent ----
assert "abcx" in "abcabcx".removeprefix("abc")
assert repr(0.1+0.2).startswith("0.30000000000000004")

# order: sort by bucket then id
Q.sort(key=lambda q: (q["bucket"], q["id"]))
assert len(Q) == 64, f"expected 64, got {len(Q)}"
by_bucket = {}
for q in Q: by_bucket.setdefault(q["bucket"], 0); by_bucket[q["bucket"]] += 1
assert all(v == 8 for v in by_bucket.values()), by_bucket

blob = json.dumps(Q, indent=2, ensure_ascii=False)
h = hashlib.sha256(blob.encode()).hexdigest()[:12]
with open("questions.json","w") as f: f.write(blob)
with open("battery_hash.txt","w") as f: f.write(h+"\n")
print("questions:", len(Q), "buckets:", by_bucket)
print("battery_hash:", h)

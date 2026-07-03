"""Hidden boundary-test suites for the code bucket. Each maps fn-name -> list of (args_tuple, expected)."""
def fib_ref(n):
    a,b=0,1
    for _ in range(n): a,b=b,a+b
    return a
TESTS = {
 "b5q1": [(("",), ""), (("a",), "a1"), (("aaabbc",), "a3b2c1"), (("abc",), "a1b1c1"),
          (("aaaaaaaaaa",), "a10"), (("xxYY",), "x2Y2")],
 "b5q2": [(("",), ""), (("a3b2",), "aaabb"), (("x1",), "x"), (("a10",), "a"*10),
          (("z2y3",), "zzyyy")],
 "b5q3": [(("",), True), (("abc",), False), (("A man, a plan, a canal: Panama",), True),
          (("ab_a",), True), (("Was it a car or a cat I saw?",), True), (("0P",), False)],
 "b5q4": [((1,), [1]), ((3,), [1,2,"fee"]), ((5,), [1,2,"fee",4,"faw"]),
          ((15,), [1,2,"fee",4,"faw","fee",7,8,"fee","faw",11,"fee",13,14,"feefaw"]),
          ((0,), [])],
 "b5q5": [((0,), 0), ((1,), 1), ((2,), 1), ((10,), 55), ((20,), 6765), ((50,), fib_ref(50))],
 "b5q6": [((0,0), 0), ((12,18), 6), ((18,12), 6), ((17,5), 1), ((100,10), 10), ((0,7), 7), ((7,0), 7)],
 "b5q7": [(("abc",1), "bcd"), (("xyz",1), "yza"), (("ABC",1), "BCD"),
          (("Hello, World!",13), "Uryyb, Jbeyq!"), (("abc",-1), "zab"), (("abc",27), "bcd")],
 "b5q8": [((0,), 0), ((9999,), 9), ((12345,), 6), ((10,), 1), ((99,), 9), ((38,), 2)],
}

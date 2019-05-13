class TestClass:
    def __init__(self, a):
        self.a = a

def tc_returner():
    return TestClass(5)
tc = TestClass(2)
tcr = tc_returner()

def const():
    return 5-3

def add(x, y):
    return x + y

def printn(s, n):
    for _ in range(n):
        print(s)

def is_even(n):
    if n==0:
        return True
    else:
        return is_odd(n-1)
def is_odd(n):
    if n==0:
        return False
    else:
        return is_even(n-1)

def str_float_int_or_bool(n):
    if n == 0:
        return 'Nice'
    elif n == 2:
        return 3.14
    elif n == 3:
        return 17355
    else:
        return is_even(n)

s = str_float_int_or_bool(0)
f = str_float_int_or_bool(2)
i = str_float_int_or_bool(3)
b = str_float_int_or_bool(1)
t = const()
a,b = [3,4]
x = 1
y = 2.0
z = x + y
large = 128
s = 'Hello' 
s2 = 'world'
s3 =  s + s2 + ' '
s4 = s3 * 3
boo = True
lean = boo or boo
bool_and = boo and lean
b1 = False and boo
b2 = not b1
b3 = (b2 and b1) or (True and (b2 or False))
if x > 1:
    w = 3
else:
    w = 4
q = add(z, y)
while x < 5:
    x = x + 1
    large = large / 2

e = is_even(10)
o = is_odd(11)

printn('ha', q) 

i1 = [1,2,3]
def iter_fn():
    return list(range(10))

d1 = {1:'test', 'test':i1}
s1 = {3, 4, 5}
i2 = iter_fn()
print(q)
print(x,y,z)

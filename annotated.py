class TestClass:
    def __init__(self, a):
        self.a = a

def tc_returner() -> <class 'TestClass'>:
    return TestClass(5)
tc = TestClass(2) # type: <class 'TestClass'>
tcr = tc_returner() # type: <class 'TestClass'>

def const() -> int:
    return 5-3

def add(x: float,y: float) -> float:
    return x + y

def printn(s: str,n: float) -> None:
    for _ in range(n):
        print(s)

def is_even(n: int) -> bool:
    if n==0:
        return True
    else:
        return is_odd(n-1)
def is_odd(n: int) -> bool:
    if n==0:
        return False
    else:
        return is_even(n-1)

def str_float_int_or_bool(n: int) -> OR(bool,int,str,float):
    if n == 0:
        return 'Nice'
    elif n == 2:
        return 3.14
    elif n == 3:
        return 17355
    else:
        return is_even(n)

s = str_float_int_or_bool(0) # type: OR(bool,int,str,float)
f = str_float_int_or_bool(2) # type: OR(bool,int,str,float)
i = str_float_int_or_bool(3) # type: OR(bool,int,str,float)
b = str_float_int_or_bool(1) # type: OR(bool,int,str,float)
t = const() # type: int
a,b = [3,4] # type: (int,int)
x = 1 # type: int
y = 2.0 # type: float
z = x + y # type: float
large = 128 # type: int
s = 'Hello'  # type: str
s2 = 'world' # type: str
s3 =  s + s2 + ' ' # type: str
s4 = s3 * 3 # type: str
boo = True # type: bool
lean = boo or boo # type: bool
bool_and = boo and lean # type: bool
b1 = False and boo # type: bool
b2 = not b1 # type: bool
b3 = (b2 and b1) or (True and (b2 or False)) # type: bool
if x > 1:
    w = 3 # type: int
else:
    w = 4 # type: int
q = add(z, y) # type: float
while x < 5:
    x = x + 1 # type: int
    large = large / 2 # type: float

e = is_even(10) # type: bool
o = is_odd(11) # type: bool

printn('ha', q) 

i1 = [1,2,3] # type: iter
def iter_fn() -> iter:
    return list(range(10))

d1 = {1:'test', 'test':i1} # type: dict
s1 = {3, 4, 5} # type: set
i2 = iter_fn() # type: iter
print(q)
print(x,y,z)


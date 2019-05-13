from collections import defaultdict
from enum import Enum
from copy import copy
import ast
import flow

if False:
    print = lambda *s,**k: None

class OrType:
    def __init__(self, a, b):
        self.subtypes = set()
        if isinstance(a, OrType):
            self.subtypes = self.subtypes.union(a.subtypes)
        else:
            self.subtypes.add(a)
        if isinstance(b, OrType):
            self.subtypes = self.subtypes.union(b.subtypes)
        else:
            self.subtypes.add(b)

    def __repr__(self, *args, **kwargs):
        return 'OR({})'.format(self.subtypes)

class ClassType:
    def __init__(self, c):
        self.type = c
    def __repr__(self, *args, **kwargs):
        return '<class \'{}\'>'.format(self.type)
    def __hash__(self):
        return hash(self.type)
    def __eq__(self, other):
        if isinstance(other, ClassType):
            return hash(self) == hash(other)
        else:
            return False

class TypeElement(Enum):
    BOT = None
    TOP = 0
    INT = int
    FLOAT = float
    COMPLEX = complex
    STR = str
    BOOL = bool
    BYTES = bytes
    OR_TYPE = OrType
    ITER = iter
    CLASS_TYPE = ClassType
    NONE = 1
    FUNCTION = 2
    DICT = dict

def _TypeElement_parser(cls, value):
    if isinstance(value, ClassType):
        return TypeElement.CLASS_TYPE
    elif isinstance(value, OrType):
        return TypeElement.OR_TYPE
    else:
        return super(TypeElement, cls).__new__(cls, value)

setattr(TypeElement, '__new__', _TypeElement_parser)
def str_from_TypeElement(te):
    if isinstance(te, OrType):
        return 'OR({})'.format(te.subtypes)
    else:
        return TypeElement(te).name

class TypeElementLattice(flow.Lattice):
    def top():
        return TypeElement.TOP
    def bot():
        return TypeElement.BOT
    def merge(a, b, *extra):
        at = TypeElement(a)
        bt = TypeElement(b)
        if TypeElement.TOP in [at,bt]:
            ret = TypeElement.TOP
        elif TypeElement.BOT == at:
            ret = b
        elif TypeElement.BOT == bt:
            ret = a
        elif at == bt:
            ret = a
        elif TypeElement.FLOAT in (at,bt) and TypeElement.INT in (at,bt):
            ret = TypeElement.FLOAT
        elif a != b:
            ret = OrType(a,b)
        else:
            print('Error in merge, exiting: {}, {}'.format(a,b))
            exit()

        if len(extra) > 0:
            return TypeElementLattice.merge(ret, *args)
        return ret

builtin_types = {
        'abs' : lambda x: x,
        'all' : lambda x: bool,
        'any' : lambda x: bool,
        'ascii' : lambda x: str,
        'bin' : lambda x: str,
        'bool' : lambda x: bool,
        'bytes' : lambda x: bytes,
        'callable' : lambda x: bool,
        'chr' : lambda x: str,
        'classmethod' : lambda x : TypeElement.FUNCTION,
        'complex' : lambda x: complex,
        'delattr' : lambda x: TypeElement.NONE,
        'dict' : lambda x: dict,
        'dir' : lambda x: iter,
        'divmod' : lambda x: iter,
        'enumerate' : lambda x: iter,
        'eval' : lambda x: TypeElement.TOP,
        'exec' : lambda x: TypeElement.TOP,
        'exit' : lambda x: TypeElement.BOT,
        'filter' : lambda x: iter,
        'format' : lambda x: str,
        'getattr' : lambda x: TypeElement.TOP ,
        'globals' : lambda x: dict ,
        'hasattr' : lambda x: bool ,
        'hash' : lambda x: int ,
        'help' : lambda x: TypeElement.NONE,
        'hex' : lambda x:  str,
        'id' : lambda x:  int,
        'input' : lambda x: str,
        'int' : lambda x:  int,
        'isinstance' : lambda x:  bool,
        'issubclass' : lambda x:  bool,
        'iter' : lambda x:  iter,
        'len' : lambda x:  int,
        'license' : lambda x: TypeElement.NONE ,
        'list' : lambda x:  iter,
        'locals' : lambda x:  dict,
        'map' : lambda x:  iter,
        'max' : lambda x:  TypeElementLattice.merge(*x) if len(x) == 2  else TypeElement.TOP,
        'memoryview' : lambda x: TypeElement.TOP,
        'min' : lambda x:  TypeElementLattice.merge(*x) if len(x) == 2  else TypeElement.TOP,
        'next' : lambda x: TypeElement.TOP,
        'object' : lambda x: ClassType('object'),
        'oct' : lambda x: str ,
        'open' : lambda x: TypeElement.TOP,
        'ord' : lambda x: int,
        'pow' : lambda x: TypeElementLattice.merge(*x),
        'print' : lambda x: TypeElement.TOP ,
        'property' : lambda x: ClassType('property'),
        'quit' : lambda x: TypeElement.BOT ,
        'range' : lambda x: iter ,
        'repr' : lambda x:  str,
        'reversed' : lambda x:  iter,
        'round' : lambda x:  int,
        'set' : lambda x:  ClassType('set'),
        'setattr' : lambda x: TypeElement.NONE,
        'slice' : lambda x:  ClassType('slice'),
        'sorted' : lambda x:  iter,
        'staticmethod' : lambda x: TypeElement.FUNCTION,
        'str' : lambda x: str,
        'sum' : lambda x: TypeElementLattice.merge(*x),
        'super' : lambda x: TypeElementLattice.TOP, # uhh
        'tuple' : lambda x:  iter,
        'type' : lambda x:  TypeElementLattice.TOP,
        'vars' : lambda x:  dict,
        'zip' : lambda x:  iter,
        }

pretty_types = {TypeElement.TOP : 'Any',
                TypeElement.BOT : 'None',
                TypeElement.INT : 'int',
                TypeElement.FLOAT: 'float',
                TypeElement.COMPLEX : 'complex',
                TypeElement.STR : 'str',
                TypeElement.BOOL : 'bool',
                TypeElement.BYTES : 'bytes',
                TypeElement.ITER : 'iter',
                TypeElement.NONE : 'None',
                TypeElement.DICT : 'dict',
                ClassType('set'): 'set'
                }
def convert_type(t):
    if not (isinstance(t, ClassType) or
            isinstance(t, OrType)):
        t = TypeElement(t)
        if pretty_types.get(t):
            t = pretty_types[t]
    elif isinstance(t, ClassType):
        if pretty_types.get(t):
            t = pretty_types[t]
    elif isinstance(t, OrType):
        subtypes = [convert_type(st) for st in t.subtypes]
        t = 'OR({})'.format(','.join(subtypes))
    return t
class LatticeDict(defaultdict):
    def __repr__(self, *args, **kwargs):
        s = '{'
        s += ', '.join(['{} : {}'.format(k,str_from_TypeElement(v)) for k,v in self.items()])
        s += '}'
        return s
    def __eq__(self, other):
        if not isinstance(other, LatticeDict):
            return False
        for key in set(self.keys()).union(set(other.keys())):
            if TypeElement(self.get(key)) != TypeElement(other.get(key)):
                return False
        return True

    def __hash__(self):
        return hash(tuple(sorted([(k,TypeElement(v)) for k,v in self.items() if not TypeElement(v).value is None])))
class TypeLattice(flow.Lattice):
    def top(self):
        return LatticeDict(TypeElementLattice.top)
    def bot(self):
        return LatticeDict(TypeElementLattice.bot)
    def merge(self, a, b):
        if a is None:
            return b
        if b is None:
            return a
        if TypeElementLattice.top in [a.default_factory, b.default_factory]:
            return self.top()
        
        new_element = self.bot()
        for var in set(a.keys()).union(set(b.keys())):
            new_element[var] = TypeElementLattice.merge(a[var], b[var])

        return new_element



def is_iter(val):
    return (isinstance(val, ast.List) or
            isinstance(val, ast.Tuple))
class TypeFlow(flow.ForwardFlow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lattice = TypeLattice()

    def initial_flow(self, lattice):
        return lattice.bot()
    
    def get_type(self, cur_flow, expr, calls=None):
        if calls is None:
            calls = set()
        if isinstance(expr, ast.Num):
            return type(expr.n)
        elif isinstance(expr, ast.Str):
            return type(expr.s)
        elif isinstance(expr, ast.NameConstant):
            return type(expr.value)
        elif isinstance(expr, ast.Call):
            # do stuff when interprocedural done
            func_id = expr.func.id
            calls.add(func_id)
            if not self.inter_anal is None: 
                if func_id in self.inter_anal.fn_ids:
                    fn_def = self.inter_anal.fn_ids[func_id]
                    args = fn_def.args.args
                    kwargs = fn_def.args.kwarg
                    
                    in_flow = self.lattice.bot()
                    for arg,val in zip(args, expr.args):
                        in_flow[arg.arg] = self.get_type(cur_flow, val, calls=calls)
                    callee_ctx = self.inter_anal.get_ctx(func_id, self.ctx, in_flow)
                    out_flow = self.inter_anal.results_for(callee_ctx, in_flow)
                    self.inter_anal.callers[callee_ctx].add(self.ctx)

                    return out_flow['return']
                else:
                    # it is a class or a builtin
                    if func_id in builtin_types:
                        return builtin_types[func_id](expr.args)
                    elif func_id in self.class_names:
                        return ClassType(func_id)
        elif isinstance(expr, ast.BinOp):
            lh = expr.left
            rh = expr.right
            op = expr.op
            lh_type = self.get_type(cur_flow, lh, calls=calls)
            rh_type = self.get_type(cur_flow, rh, calls=calls)
            
            types = (TypeElement(lh_type), TypeElement(rh_type))
            if isinstance(op, ast.Add) or isinstance(op, ast.Sub):
                return TypeElementLattice.merge(*types)
            elif isinstance(op, ast.Mult):
                if TypeElement.STR in types and TypeElement.INT in types:
                    return TypeElement.STR
                else:
                    return TypeElementLattice.merge(*types)
            elif isinstance(op, ast.Div):
                return TypeElement.FLOAT
            else:
                print('Error in BinOp: {} {} {}'.format(lh_type, op, rh_type))
                exit()
        elif isinstance(expr, ast.BoolOp):
            # this isn't correct, see: True or 5, False or 5
            return TypeElement.BOOL
        elif isinstance(expr, ast.UnaryOp):
            if isinstance(expr.op, ast.Not):
                return TypeElement.BOOL
            else:
                print('Unknown UnaryOp {}, exiting'.format(epxr.op))
                exit()
        elif isinstance(expr, ast.Name):
            return cur_flow[expr.id]
        elif isinstance(expr, ast.List) or isinstance(expr, ast.Tuple):
            return TypeElement.ITER
        elif isinstance(expr, ast.Dict):
            return TypeElement.DICT
        elif isinstance(expr, ast.Set):
            return ClassType('set')
        else:
            print(expr)
            print(dir(expr))
            try:
                print(type(expr.value))
            except AttributeError:
                print('No value field')
            return TypeElement.TOP

    def update_type(self, cur_flow, var_id, val, calls=None):
        rh_type = self.get_type(cur_flow, val, calls=calls)
        if TypeElement(rh_type) == TypeElement.BOT:
            print('Found BOT, exiting, line {}'.format(val.lineno))
            exit()
        cur_flow[var_id] =  rh_type

    def flow_through(self, in_flow, ins, calls=None):
        out_flow = copy(in_flow)
#        print('Instruction: {} line: {}\nflow: {}'.format(ins,ins.lineno, out_flow))
        print(ins, ins.lineno)
        if isinstance(ins, ast.Assign):
            if self.lines:
                print('{}'.format(self.lines[ins.lineno-1]))
            val = ins.value
            for var in ins.targets:
                if is_iter(var):
                    var_elts = var.elts
                    if isinstance(val, ast.Call):
                        val_elts = [(i,val) for i in range(len(ins.targets))]
                    elif is_iter(val):
                        val_elts = val.elts
                    else:
                        print('Tuple assignment error')
                    for var_elt,val_elt in zip(var_elts, val_elts):
                        self.update_type(out_flow, var_elt.id, val_elt, calls=calls)
                else:
                    self.update_type(out_flow, var.id, val, calls=calls)
        elif isinstance(ins, ast.Expr):
            if isinstance(ins.value, ast.Call):
                expr = ins.value
                func_id = ins.value.func.id
                calls.add(func_id)
                if not self.inter_anal is None: 
                    if func_id in self.inter_anal.fn_ids:
                        fn_def = self.inter_anal.fn_ids[func_id]
                        args = fn_def.args.args
                        kwargs = fn_def.args.kwarg
                        
                        new_in_flow = self.lattice.bot()
                        for arg,val in zip(args, expr.args):
                            new_in_flow[arg.arg] = self.get_type(in_flow, val, calls=calls)
                        callee_ctx = self.inter_anal.get_ctx(func_id, self.ctx, new_in_flow)
                        out_flow = self.inter_anal.results_for(callee_ctx, new_in_flow)
                        self.inter_anal.callers[callee_ctx].add(self.ctx)

        elif isinstance(ins, ast.Return):
            ret_type = self.get_type(out_flow, ins.value, calls=calls)
            new_ret = copy(out_flow)
            new_ret['return'] = ret_type
            self.ret = self.lattice.merge(self.ret, new_ret)
        else:
            pass #print(ins)
        print()

        return out_flow



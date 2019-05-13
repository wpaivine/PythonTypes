from copy import copy
import collections
import ast
import util

if True:
    print = lambda *s,**k: None

def is_instruction(node):
    return not (isinstance(node,ast.FunctionDef) or
                isinstance(node,ast.ClassDef) or
                isinstance(node,ast.Call))

def is_expandable(node):
    return (isinstance(node,ast.If) or
            isinstance(node,ast.While) or
            isinstance(node,ast.FunctionDef) or
            isinstance(node,ast.ClassDef))


class Lattice:
    def top(self):
        return None
    def bot(self):
        return None
    def merge(self, a, b):
        return None

def build_cfg(body, preds=None, succs=None, last_nodes=None, line_lookup=None):
    if preds is None:
        preds = dict()
    if succs is None:
        succs = dict()
    if last_nodes is None:
        last_nodes = []
    class_names = set()
    found_entry = False
    needs_expanding = set()
    for node in body:
        print('Analyzing line: {}'.format(node.lineno))
        if not line_lookup is None:
            line_lookup[node.lineno] = node
        if is_instruction(node):
            print('Line is an instruction: {}'.format(node))
            if last_nodes != []:
                if preds.get(node) is None:
                    preds[node] = set()
                for last_node in last_nodes:
                    if succs.get(last_node) is None:
                        succs[last_node] = set()
                    succs[last_node].add(node)
                    preds[node].add(last_node)
            if not found_entry:
                entry = node
                found_entry = True
            if is_expandable(node):
                last_nodes = [node]
                print('Expanding {} on line {}'.format(node, node.lineno))
                if isinstance(node, ast.If):
                    _, _, ient, ilns, ine,_ = build_cfg(node.body,preds,succs,
                            last_nodes,line_lookup)
                    _, _, eent, elns, ene,_ = build_cfg(node.orelse,preds,succs,
                            last_nodes,line_lookup)
                    last_nodes = ilns + elns
                elif isinstance(node, ast.While):
                    _, _, ent, lns, ne,_ = build_cfg(node.body,preds,succs,

                            last_nodes,line_lookup)
                    
                    last_nodes = lns
                    for last_node in last_nodes:
                        if succs.get(last_node) is None:
                            succs[last_node] = set()
                        succs[last_node].add(node)
                        preds[node].add(last_node)

            else:
                last_nodes = [node]
        else:
            if is_expandable(node):
                needs_expanding.add(node)
                print('Need to expand {} on line {}'.format(node, node.lineno))
    for last_node in last_nodes:
        if succs.get(last_node) is None:
            succs[last_node] = set()
    
    fn_defs = dict()
    for node in needs_expanding:
        if isinstance(node, ast.FunctionDef):
            _,_, fn_entry, _,_,_ = build_cfg(node.body, preds, succs, [], line_lookup)
            fn_defs[node] = fn_entry
        elif isinstance(node, ast.ClassDef):
            class_names.add(node.name)
        else:
            print('Ignoring expandable node {} on line {}'.format(node, node.lineno))

    return (preds, succs, entry, last_nodes, fn_defs, class_names)

class ForwardFlow:
    def __init__(self, contents, cfg=None, interprocedural=None):
        self.inter_anal = interprocedural
        if type(contents) == str:
            self.lines = contents.split('\n')
            contents = ast.parse(contents)
            self.parse_tree = contents
            self.body = contents.body
        else:
            self.lines = None
            self.body = contents
        self.analysis_result = util.dotdict()
        self.line_lookup = dict()
        if cfg is None:
            self.preds, self.succs, self.entry, _, self.defs, self.class_names = build_cfg(self.body,
                    line_lookup=self.line_lookup)
            print('Built CFG')
        else:
            self.preds, self.succs, self.entry, _, self.defs,self.class_names = cfg
    
    def initial_flow(self, lattice):
        return lattice.top()

    def flow_through(self, in_flow, node, calls=None):
        return copy(in_flow)
    
    def results_for(self, ctx, flow_input):
        assert not self.inter_anal is None
        res_out = self.inter_anal.results[ctx].output
        res_in = self.inter_anal.results[ctx].input

        if res_out != self.lattice.bot() and res_in == self.lattice.merge(flow_input,
                res_in):
            return res_out

        self.inter
    def run_analysis(self):
        res = self.analysis_result
        lat = self.lattice
        res.initial_flow = self.initial_flow(lat)

        ins_inputs = dict()
        outputs = dict()
        self.outputs=outputs
        self.ret = lat.bot()
        if self.body == []:
            return
        for node in self.body:
            ins_inputs[node] = lat.bot()
        preds = self.preds
        succs = self.succs
        defs = self.defs

        ins_inputs[self.body[0]] = self.initial_flow(lat)
        worklist = collections.deque([self.entry])
        
        while len(worklist) > 0:
            instruction = worklist.pop()
            in_flow = lat.bot()
            if not preds.get(instruction) is None:
                print('Preds to line {} is: '.format(instruction.lineno), end='')
                for predecessor in preds[instruction]:
                    print('{} '.format(predecessor.lineno),end='')
                    pred_output = outputs.get(predecessor) or lat.bot()
                    in_flow = lat.merge(in_flow, pred_output)
                print()
            else:
                print('Initial flow found, line no: {}'.format(instruction.lineno))
                in_flow = self.initial_flow(lat)
            res.calls = set()
            new_output = self.flow_through(in_flow, instruction, calls=res.calls)
            if new_output != outputs.get(instruction):
                outputs[instruction] = new_output
                for next_inst in succs[instruction]:
                    worklist.appendleft(next_inst)
        

        res.flow_states = outputs

        def var_lookup(line_no, var_name):
            ins = self.line_lookup[line_no]
            return res.flow_states[ins][var_name]

        res.var_lookup = var_lookup
        return res


        


import collections
import ast
import intraprocedural
import flow

if True:
    print = lambda *s,**k: None
class Context:
    fn = None
    flow_input = None
    def __init__(self, fn, flow_input, func_id=''):
        self.fn = fn
        self.func_id = func_id
        self.flow_input = flow_input

    def __hash__(self):
        return hash((self.func_id, self.flow_input))

    def __eq__(self, other):
        if isinstance(other, Context):
            return hash(self) == hash(other)
        return False

class Summary:
    flow_input = None
    flow_output = None
    def __init__(self, flow_input, flow_output):
        self.flow_input = flow_input
        self.flow_output = flow_output

class Interprocedural:
    def __init__(self, contents):
        if type(contents) == str:
            self.lines = contents.split('\n')
            contents = ast.parse(contents)
        else:
            self.lines = None

        self.parse_tree = contents
        self.body = contents.body

        self.line_lookup = dict()
        self.lattice = intraprocedural.TypeLattice()
        self.intraprocedural_analysis = intraprocedural.TypeFlow

        self.preds, self.succs, self.entry, self.last_nodes, \
            self.defs, self.class_names = flow.build_cfg(self.body, line_lookup=self.line_lookup)

        self.fn_ids = {d.name:d for d in self.defs}
        self.worklist = collections.deque()
        self.analyzing = collections.deque()
        self.results = dict()
        self.callers = collections.defaultdict(set)
        self.intra_analyses = set()
        
    
    def analyze_program(self):
        main_ctx = Context(self.body, self.lattice.bot())
        self.worklist = collections.deque([main_ctx])
        
        self.results[main_ctx] = Summary(self.lattice.bot(), self.lattice.bot())
        while self.worklist:
            ctx = self.worklist.pop()
            self.analyze(ctx, self.results[ctx].flow_input)
        return self.results
    
    def analyze(self, ctx, flow_input):
        if ctx.func_id:
            print('Analyzing {}'.format(ctx.func_id))
        else:
            print('Analyzing main body')
        flow_output = self.results[ctx].flow_output
        self.analyzing.appendleft(ctx)

        new_flow_output = self.intraprocedural(ctx, flow_input)
        self.analyzing.pop()
        
        merged = self.lattice.merge(new_flow_output, flow_output) 
        if merged != flow_output:
            self.results[ctx] = Summary(flow_input, merged)
            for c in self.callers[ctx]:
                self.worklist.appendleft(c)

        if ctx.func_id:
            print('Done analyzing {}'.format(ctx.func_id))
        else:
            print('Done analyzing main body')
        return new_flow_output


    def intraprocedural(self, ctx, flow_input):
        if ctx.func_id != '':
            entry = self.defs[self.fn_ids[ctx.func_id]]
        else:
            entry = self.entry
        cfg = (self.preds, self.succs, entry, self.last_nodes, self.defs, self.class_names)
        intra_analysis = self.intraprocedural_analysis(ctx.fn,
                interprocedural=self,cfg=cfg)
        intra_analysis.ctx = ctx
        
        def initial_flow(lat):
            return flow_input

        intra_analysis.initial_flow = initial_flow
        res = intra_analysis.run_analysis()

        self.intra_analyses.add(intra_analysis)
        # get output flow
        if ctx.func_id == '':
            flow_output = None
        else:
            flow_output = intra_analysis.ret
        return flow_output

    def results_for(self, ctx, flow_input):
        if self.results.get(ctx) is None:
            self.results[ctx] = Summary(self.lattice.bot(), self.lattice.bot())
        res_out = self.results[ctx].flow_output    
        res_in = self.results[ctx].flow_input
        
        if res_out != self.lattice.bot() and res_in == self.lattice.merge(flow_input,res_in):
            return res_out
        
        self.results[ctx].input = self.lattice.merge(res_in, flow_input)
        if len(self.analyzing) > 100: # change if more than 100 functions in prog
            exit()
        if ctx in self.analyzing:
            return self.lattice.bot()
        else:
            return self.analyze(ctx, self.results[ctx].input)

    def get_ctx(self, func_id, calling_ctx, in_flow):
        return Context(self.fn_ids[func_id].body, in_flow, func_id=func_id)

    def get_line_flow(self, lineno):
        if not self.line_lookup.get(lineno):
            return
        line_flow = self.lattice.bot()
        node = self.line_lookup[lineno]
        if isinstance(node, ast.FunctionDef):
            for intra_analysis in self.intra_analyses:
                if intra_analysis.ctx.func_id == node.name:
                    line_flow = self.lattice.merge(line_flow,
                            intra_analysis.initial_flow(intra_analysis.lattice))

        else:
            for intra_analysis in self.intra_analyses:
                analysis_flow = intra_analysis.outputs.get(node)
                if analysis_flow:
                    line_flow = self.lattice.merge(line_flow, analysis_flow)
        
        return line_flow

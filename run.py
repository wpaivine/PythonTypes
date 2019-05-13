import ast
import flow
import intraprocedural
import interprocedural
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("filename", help="the python file to parse")
parser.add_argument('-a', '--annotate', help='output annotations to file')
args = parser.parse_args()

with open(args.filename, 'r') as f:
    contents = f.read()

print('Analyzing {}'.format(args.filename))
parsed = ast.parse(contents)
analysis = interprocedural.Interprocedural(contents)

analysis_result = analysis.analyze_program()

convert_type = intraprocedural.convert_type
print('='* 50)
print('Results:')
for ctx in analysis_result:
    if ctx.func_id == '':
        name = 'main body'
    else:
        name = ctx.func_id
    
    print('Function: {}'.format(name))
    print('Argument types: {}'.format(ctx.flow_input))
    return_val = convert_type(analysis_result[ctx].flow_output['return'])
    print('Return value: {}'.format(return_val))
    print()
print('='* 50)

def get_assign_type(i,target):
    if isinstance(target, ast.Name):
        return_val = analysis.get_line_flow(i)[target.id]
        return str(convert_type(return_val))
    elif isinstance(target, ast.Tuple):
        return '({})'.format(','.join([get_assign_type(i, sub_target) for sub_target in target.elts]))
if args.annotate:
    print('Appending annotations to file: {}'.format(args.annotate))
    annotated = ''
    for i,line in enumerate(analysis.lines):
        i += 1
        if analysis.line_lookup.get(i):
            stmt = analysis.line_lookup[i]
            if isinstance(stmt, ast.Assign):
                annotated += line

                target = stmt.targets[0] # pick out the first var for looking up
                annotated += ' # type: {}'.format(get_assign_type(i,target))

            elif isinstance(stmt, ast.FunctionDef):
                fn_args = line[line.index('(')+1:line.rindex(')')].replace(' ','').split(',')
                fn_name = stmt.name
                line_flow = analysis.get_line_flow(i)
                fn_def = line[:line.index('(')]
                annotated_args = ','.join(['{}: {}'.format(arg,convert_type(line_flow[arg])) for arg in fn_args
                    if arg])

                
                return_flow = analysis.lattice.bot()

                for ctx in analysis_result:
                    if ctx.func_id == fn_name:
                        return_flow = analysis.lattice.merge(return_flow,
                                analysis_result[ctx].flow_output)
                return_val_type = convert_type(return_flow['return'])

                annotated += '{}({}) -> {}:'.format(fn_def,annotated_args,return_val_type)
            else:
                annotated += line
        else:
            annotated += line


        annotated += '\n'


    with open(args.annotate, 'w') as f:
        f.write(annotated)

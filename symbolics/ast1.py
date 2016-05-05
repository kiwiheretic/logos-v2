import ast
import sys
import sympy

class SymVars:
    """ Repository for sympy symbols (eg: x,y,z etc to keep
    them clashing with local vars"""
    pass

class MyNodeVisitor(ast.NodeVisitor):

    def initvars(self, var_prefix = None):
        self.symbol_vars = set()
        self.var_prefix = var_prefix

    def visit(self, tree):
        self.result = None
        super(MyNodeVisitor, self).visit(tree)

    def visit_children(self, node):
        for subnode in ast.iter_child_nodes(node):
            self.visit(subnode)

    def brackets_required(self, op, node):
        if type(node) != ast.BinOp: return False
        if op == '*' or op == '/':
            if type(node.op) in [ast.Add, ast.Sub]:
                return True
            else:
                return False
        elif op == '**':
            return True
        else:
            return False

    def visit_Module(self, node):
        self.visit_children(node)

    def visit_Expr(self, node):
        self.visit_children(node)

    def visit_Name(self, node):
        if node.id in ['pi', 'E', 'sqrt', 'sin', 'cos', 'tan', 'asin', 'acos', 
                'atan', 'sinh', 'cosh', 'tanh', 'asinh', 'acosh', 'atanh',
                'atan2', 'log', 'ln', 'exp', 'diff', 'integrate', 'simplify', 
                'factor', 'expand', 'collect', 'apart', 'trigsimp', 'expand_trig',
                'cancel', 'powsimp', 'expand_log']:
            node.valuestr = 'sympy.'+node.id
        else:
            if self.var_prefix:
                node.valuestr = self.var_prefix + node.id
            else:
                node.valuestr = node.id
            self.symbol_vars.add(node.id)
        self.result = node.valuestr

    def visit_Num(self, node):
        node.valuestr = str(node.n)
        self.result = node.valuestr

    def visit_Call(self, node):
        self.visit_children(node)
        arglist = [x.valuestr for x in node.args ]
        node.valuestr = node.func.valuestr + "(" + ", ".join(arglist) + ")"
        self.result = node.valuestr

    def visit_UAdd(self,node):
        pass

    def visit_USub(self,node):
        pass

    def visit_UnaryOp(self, node):
        #if type(node.operand) in [ast.BinOp, ast.Name, ast.Num, ast.Call]:
        self.visit_children(node)
        if type(node.op) == ast.USub:
            prefix = "-"
        elif type(node.op) == ast.UAdd:
            prefix = "+"
        else:
            raise SyntaxError("AST invalid unary op")
        #if hasattr(node.operand,'valuestr'):
        node.valuestr = prefix +"("+ node.operand.valuestr+")"
        self.result = node.valuestr

    def visit_BinOp(self, node):
        print "**", node
        if type(node.op) == ast.Add:
            opstr = '+'
        elif type(node.op) == ast.Sub:
            opstr = "-"
        elif type(node.op) == ast.Mult:
            opstr = '*'
        elif type(node.op) == ast.Div:
            opstr = '/'
        elif type(node.op) == ast.Pow:
            opstr = '**'
        else:
            opstr = '???'
        node.opstr = opstr
        # Don't visit ast.Add, ast.Sub, ast.Mult, ast.Div
        # underneath ast.BinOp nodes.
        self.visit(node.left)
        self.visit(node.right)
        left = getattr(node.left, 'valuestr', "?")
        right = getattr(node.right, 'valuestr', "?")
        if self.brackets_required(opstr, node.left):
            left = "("+left+")"
        if self.brackets_required(opstr, node.right):
            right = "("+right+")"

        print left + opstr + right
        if opstr == "/" and type(node.left)==ast.Num and type(node.right) == ast.Num:
            node.valuestr="sympy.Rational("+left+","+right+")"
        else:
            node.valuestr = left + opstr + right
        self.result = node.valuestr


    def generic_visit(self, node):
        print node
        raise SyntaxError('Logos AST Disallowed Syntax')

def run_tests():
    nv = MyNodeVisitor()
    s = "(x+3)*(x-4)+x + 3/4 +sin(pi/4)"

    tree = ast.parse(s)

    nv.initvars()
    nv.visit(tree)
    print "result = ",nv.result
    assert(nv.result == "(x+3)*(x-4)+x+sympy.Rational(3,4)+sympy.sin(sympy.pi/4)")
    print "symbols used : " + str(nv.symbol_vars)

    # Test unary

    s = "-(x+3)"

    tree = ast.parse(s)

    nv.initvars()
    nv.visit(tree)
    print "result = ",nv.result
    assert(nv.result == "-(x+3)")
    s = '2**(3*(4+2))'

    tree = ast.parse(s)

    nv.visit(tree)
    print "result = ",nv.result
    assert(nv.result == s.replace(" ",""))

    s = 'import os; os.command("rm -fr /")'
    print s
    tree = ast.parse(s)

    try:
        nv.visit(tree)
    except SyntaxError, err:
        print err.msg
        print "Expected Syntax error occurred - Pass"
    else:
        print "** Fail ****"

    s = '2*((3*4)+2)'

    tree = ast.parse(s)

    nv.visit(tree)
    print "result = ",nv.result
    assert(nv.result == "2*(3*4+2)")

def long_calc():
    from sympy import integrate, sin, exp
    s = "integrate(sin(a*x)*exp(-x*x),x)"
    a,x = sympy.symbols('a x')
    print eval(s)

def subprocess_test():
    from subprocess import Popen, PIPE
    import os
    import signal
    from time import sleep
    s = os.path.join(os.getcwd(), 'subprocess.sh')
    p = Popen(s, bufsize=1, stdout=PIPE, shell=True, preexec_fn=os.setsid)
    print p.stdout
    sleep(10)
    print "killing subprocess"
    # kill based on http://stackoverflow.com/questions/4789837/how-to-terminate-a-python-subprocess-launched-with-shell-true
    os.killpg(os.getpgid(p.pid), signal.SIGTERM) 
    sleep(5)

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        if sys.argv[1] == 'tests':
            run_tests()
            sys.exit()
        elif sys.argv[1] == 'long-calc':
            long_calc()
            sys.exit()
        elif sys.argv[1] == 'subprocess':
            subprocess_test()
            sys.exit()


    symvars = SymVars()
    nv = MyNodeVisitor()
    s = raw_input(' --> ')
    while s != 'quit' and s != 'q':
        try:
            tree = ast.parse(s)
            nv.initvars(var_prefix = "symvars.")
            nv.visit(tree)
            print "result = ",nv.result
            print "symbols used : " + str(nv.symbol_vars)
            for v in nv.symbol_vars:
                if not hasattr(symvars, v):
                    setattr(symvars, v, sympy.symbols(v))
            try:
                print eval(nv.result)
            except TypeError:
                print "TypeError"
        except SyntaxError, e:
            print "SyntaxError " + e.msg

        s = raw_input(' --> ')

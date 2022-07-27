from fim_lexer import Literals
from fim_lexer import Keywords


class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


class Interpreter(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser
        self.GLOBAL_SCOPE = {}

    def interpret(self):
        tree = self.parser.parse()
        return self.visit(tree)

    def visit_BinOp(self, node):
        if node.op.name == Keywords.ADDITION:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.name == Keywords.SUBTRACTION:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.name == Keywords.MULTIPLICATION:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.name == Keywords.DIVISION:
            return self.visit(node.left) / self.visit(node.right)
        elif node.op.name == Keywords.GREATER_THAN:
            return self.visit(node.left) > self.visit(node.right)
        elif node.op.name == Keywords.LESS_THAN:
            return self.visit(node.left) < self.visit(node.right)
        elif node.op.name == Keywords.GREATER_THAN_OR_EQUAL:
            return self.visit(node.left) >= self.visit(node.right)
        elif node.op.name == Keywords.LESS_THAN_OR_EQUAL:
            return self.visit(node.left) <= self.visit(node.right)
        elif node.op.name == Keywords.EQUAL:
            return self.visit(node.left) == self.visit(node.right)
        elif node.op.name == Keywords.NOT_EQUAL:
            return self.visit(node.left) != self.visit(node.right)
        elif node.op.name == Keywords.AND:
            left = self.visit(node.left)
            right = self.visit(node.right)
            if type(left) == float and type(right) == float:
                return left + right
            else:
                return left and right
        elif node.op.name == Keywords.OR:
            return self.visit(node.left) or self.visit(node.right)
        elif node.op.name == Keywords.XOR:
            return self.visit(node.left) ^ self.visit(node.right)

    def visit_UnaryOp(self, node):
        op = node.op.name
        if op == Keywords.NOT:
            return not(self.visit(node.expr))

    def visit_Number(self, node):
        return float(node.value)

    def visit_String(self, node):
        return node.value

    def visit_Char(self, node):
        return node.value

    def visit_Bool(self, node):
        return node.value

    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def visit_StatementList(self, node):
        for child in node.children:
            self.visit(child)

    def visit_NoOp(self, node):
        pass

    def visit_Assign(self, node):
        var_name = node.left.value
        if var_name in self.GLOBAL_SCOPE:
            self.GLOBAL_SCOPE[var_name] = self.visit(node.right)

    def visit_VariableDeclaration(self, node):
        var_name = node.left.value
        if var_name in self.GLOBAL_SCOPE:
            raise NameError(repr(var_name))
        else:
            self.GLOBAL_SCOPE[var_name] = self.visit(node.right)

    def visit_Var(self, node):
        var_name = node.value
        val = self.GLOBAL_SCOPE.get(var_name)
        if val is None:
            raise NameError(repr(var_name))
        else:
            return val

    def visit_Print(self, node):
        res = self.visit(node.expr)
        # if res is float and can be int, convert it
        if type(res) == float\
                and int(res) == float(res):
            res = int(res)
        print(res)

from fim_lexer import Literals
from fim_lexer import Keywords
from environment import Environment
import operator


class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


def stringify(obj):
    # if res is float and can be int, convert it to int
    if type(obj) == float and int(obj) == float(obj):
        return str(int(obj))
    if obj is None:
        return "nothing"
    if obj is True:
        return "true"
    if obj is False:
        return "false"
    return str(obj)


class Interpreter(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser
        self.environment = Environment()

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
            return not (self.visit(node.expr))

    def visit_Number(self, node):
        return float(node.value)

    def visit_String(self, node):
        return node.value

    def visit_Char(self, node):
        return node.value

    def visit_Bool(self, node):
        return node.value

    def visit_Null(self, node):
        return node.value

    def visit_Compound(self, node):
        self.execute_compound(node.children, Environment(self.environment))

    def execute_compound(self, statements, environment):
        previous_env = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.visit(statement)
        finally:
            self.environment = previous_env

    def visit_If(self, node):
        if self.visit(node.condition):
            self.visit(node.then_branch)
        elif node.else_branch is not None:
            self.visit(node.else_branch)

    def visit_While(self, node):
        while self.visit(node.condition):
            self.visit(node.body)

    def visit_StatementList(self, node):
        for child in node.children:
            self.visit(child)

    def visit_NoOp(self, node):
        pass

    def visit_Assign(self, node):
        var_name = node.left.value
        self.environment.assign(var_name, self.visit(node.right))

    def visit_VariableDeclaration(self, node):
        var_name = node.left.value
        self.environment.define(var_name, self.visit(node.right))

    def visit_Var(self, node):
        var_name = node.value
        val = self.environment.get(var_name)
        return val

    def visit_Increment(self, node):
        var_name = node.token.value
        self.environment.modify(var_name, operator.add, 1)

    def visit_Decrement(self, node):
        var_name = node.token.value
        self.environment.modify(var_name, operator.sub, 1)

    def visit_Print(self, node):
        res = self.visit(node.expr)
        print(stringify(res))

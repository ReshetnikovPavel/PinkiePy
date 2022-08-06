from fim_lexer import Literals
from fim_lexer import Keywords
from environment import Environment
import fim_callable
from node_visitor import NodeVisitor
import operator


class Interpreter(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser
        self.globals = Environment()
        self.environment = self.globals
        self.locals = {}

    def interpret(self, tree):
        return self.visit(tree)

    def resolve(self, node, depth):
        self.locals[node] = depth

    def visit_BinOp(self, node):
        if node.op.type == Keywords.ADDITION:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == Keywords.SUBTRACTION:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == Keywords.MULTIPLICATION:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == Keywords.DIVISION:
            return self.visit(node.left) / self.visit(node.right)
        elif node.op.type == Keywords.GREATER_THAN:
            return self.visit(node.left) > self.visit(node.right)
        elif node.op.type == Keywords.LESS_THAN:
            return self.visit(node.left) < self.visit(node.right)
        elif node.op.type == Keywords.GREATER_THAN_OR_EQUAL:
            return self.visit(node.left) >= self.visit(node.right)
        elif node.op.type == Keywords.LESS_THAN_OR_EQUAL:
            return self.visit(node.left) <= self.visit(node.right)
        elif node.op.type == Keywords.EQUAL:
            return self.visit(node.left) == self.visit(node.right)
        elif node.op.type == Keywords.NOT_EQUAL:
            return self.visit(node.left) != self.visit(node.right)
        elif node.op.type == Keywords.AND:
            left = self.visit(node.left)
            right = self.visit(node.right)
            if type(left) == float and type(right) == float:
                return left + right
            else:
                return left and right
        elif node.op.type == Keywords.OR:
            return self.visit(node.left) or self.visit(node.right)
        elif node.op.type == Keywords.XOR:
            return self.visit(node.left) ^ self.visit(node.right)

    def visit_UnaryOp(self, node):
        op = node.op.type
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

    def visit_DoWhile(self, node):
        while True:
            self.visit(node.body)
            if not self.visit(node.condition):
                break

    def visit_StatementList(self, node):
        for child in node.children:
            self.visit(child)

    def visit_NoOp(self, node):
        pass

    def visit_Assign(self, node):
        value = self.visit(node.right)
        distance = self.locals.get(node)
        if distance is not None:
            self.environment.assign_at(distance, node.left.value, value)
        else:
            self.globals.assign(node.left.value, value)

        return value

    def visit_VariableDeclaration(self, node):
        var_name = node.left.value
        self.environment.define(var_name, self.visit(node.right))

    def visit_Var(self, node):
        val = self.lookup_variable(node.token, node)
        if isinstance(val, fim_callable.FimCallable):
            return val.call(self, [])
        return val

    def lookup_variable(self, token, node):
        distance = self.locals.get(node)
        if distance is not None:
            return self.environment.get_at(distance, token.value)
        else:
            return self.globals.get(token.value)

    def visit_FunctionCall(self, node):
        function_name = node.name.value
        function = self.environment.get(function_name)

        arguments = []
        for argument in node.arguments:
            arguments.append(self.visit(argument))

        if len(arguments) != function.arity():
            raise RuntimeError("Function '{}' expected {} arguments, got {}".format(function_name, function.arity(), len(arguments)))

        if isinstance(function, fim_callable.FimCallable):
            return function.call(self, arguments)
        else:
            raise RuntimeError("{} is not a function".format(function_name))

    def visit_Return(self, node):
        value = None
        if node.value is not None:
            value = self.visit(node.value)
        raise fim_callable.FimReturn(value)

    def visit_Increment(self, node):
        var_name = node.variable.value
        self.environment.modify(var_name, operator.add, 1)

    def visit_Decrement(self, node):
        var_name = node.variable.value
        self.environment.modify(var_name, operator.sub, 1)

    def visit_Print(self, node):
        res = self.visit(node.expr)
        print(stringify(res))

    def visit_Function(self, node):
        fim_function = fim_callable.FimFunction(node, self.environment)
        self.environment.define(node.name, fim_function)


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

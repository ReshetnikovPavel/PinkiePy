import re
from fim_lexer import Literals


class AST:
    pass


class Root(AST):
    def __init__(self, children):
        self.children = children


class Compound(AST):
    def __init__(self):
        self.children = []


class Assign(AST):
    def __init__(self, left, right):
        self.left = left
        self.right = right


class Print(AST):
    def __init__(self, expr):
        self.expr = expr


class Var(AST):
    def __init__(self, token):
        self.token = token

    @property
    def value(self):
        return self.token.value

    def __repr__(self):
        return f"Var({self.token})"


class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class UnaryOp(AST):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr


class Number(AST):
    def __init__(self, token):
        self.token = token

    @property
    def value(self):
        return self.token.value


class Char(AST):
    def __init__(self, token):
        self.token = token

    @property
    def value(self):
        if self.token.value[0] == "'" and self.token.value[-1] == "'":
            return self.token.value[1:-1]
        return self.token.value


class Bool(AST):
    def __init__(self, token):
        self.token = token

    @property
    def value(self):
        if self.token.type == Literals.TRUE:
            return True
        elif self.token.type == Literals.FALSE:
            return False
        else:
            raise NameError(repr(self.token.type))


class Null(AST):
    def __init__(self, token):
        self.token = token
        self.value = None


class String(AST):
    def __init__(self, token):
        self.token = token

    @property
    def value(self):
        if self.token.value[0] in ['"', '”', '“']\
                and self.token.value[-1] in ['"', '”', '“']:
            return self.token.value[1:-1]
        return self.token.value

    def __iter__(self):
        return iter(self.value)


class NoOp(AST):
    pass


class Class(AST):
    def __init__(self, name, superclass, implementations, body, methods, fields, programmer):
        self.name = name
        self.superclass = superclass
        self.implementations = implementations
        self.body = body
        self.methods = methods
        self.fields = fields
        self.programmer = programmer


class Interface(AST):
    def __init__(self, name, methods, programmer):
        self.name = name
        self.methods = methods
        self.programmer = programmer

    def __str__(self):
        raise Exception("Cannot print interface")


class Get(AST):
    def __init__(self, object, name, has_parameters):
        self.object = object
        self.name = name
        self.has_parameters = has_parameters


class Set(AST):
    def __init__(self, object, name, value):
        self.object = object
        self.name = name
        self.value = value


class Function(AST):
    def __init__(self, name, return_type, params, body, is_main):
        self.token = name
        self.name = name
        self.return_type = return_type
        self.params = params
        self.body = body
        self.is_main = is_main


class Return(AST):
    def __init__(self, value):
        self.value = value


class FunctionCall(AST):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


class Read(AST):
    def __init__(self, variable):
        self.variable = variable


class Prompt(AST):
    def __init__(self, read_node, expr):
        self.read_node = read_node
        self.expr = expr


class VariableDeclaration(AST):
    def __init__(self, left, op, right, is_const=False):
        self.left = left
        self.token = self.op = op
        self.right = right
        self.is_const = is_const


class Increment(AST):
    def __init__(self, variable, value=1):
        self.variable = variable
        self.value = value


class Decrement(AST):
    def __init__(self, variable):
        self.variable = variable


class If(AST):
    def __init__(self, condition, then_branch, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch


class Switch(AST):
    def __init__(self, variable, cases, default):
        self.variable = variable
        self.cases = cases
        self.default = default


class While(AST):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body


class DoWhile(AST):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body


class Import(AST):
    def __init__(self, name):
        self.name = name


class Array(AST):
    def __init__(self, name, type, elements=None):
        self.name = name
        self.type = type
        self.elements = elements


class ArrayElementAssignment(AST):
    def __init__(self, left, right, index=None):
        self.left = left
        self.right = right
        if index is None:
            self.index = self._separate_index()
        else:
            self.index = index
        self.array_name = self._separate_array_name()
        self.left.token.value = self.array_name

    def _separate_index(self):
        m = re.search(r'\d+$', self.left.token.value)
        return int(m.group()) if m else None

    def _separate_array_name(self):
        return re.sub(r'\s+\d+$', '', self.left.value)


class ArrayElement(AST):
    def __init__(self, name, index):
        self.name = name
        self.index = index


class For(AST):
    def __init__(self, init, to_value, body):
        self.init = init
        self.to_value = to_value
        self.body = body


class ForIter(AST):
    def __init__(self, init, iterable, body):
        self.init = init
        self.iterable = iterable
        self.body = body

import copy
from fim_lexer import Literals, Token, Keywords, Block, Suffix


class AST:
    pass


class Root(AST):
    def __init__(self, children):
        self.children = children

    @property
    def line(self):
        return self.children[0].line


class Compound(AST):
    def __init__(self):
        self.children = []

    @property
    def line(self):
        return self.children[0].line


class Assign(AST):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    @property
    def line(self):
        return self.left.token.line


class Print(AST):
    def __init__(self, expr):
        self.expr = expr

    @property
    def line(self):
        return self.expr.line


class Var(AST):
    def __init__(self, token):
        self.token = token

    @property
    def value(self):
        return self.token.value

    @property
    def line(self):
        return self.token.line

    def __repr__(self):
        return f"Var({self.token})"


class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

    @property
    def line(self):
        return self.left.line


class UnaryOp(AST):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr

    @property
    def line(self):
        return self.expr.line


class Number(AST):
    def __init__(self, token):
        self.token = token

    @property
    def value(self):
        return self.token.value

    @property
    def line(self):
        return self.token.line


class Char(AST):
    def __init__(self, token):
        self.token = token

    @property
    def value(self):
        if self.token.value[0] == "'" and self.token.value[-1] == "'":
            return self.token.value[1:-1]
        return self.token.value

    @property
    def line(self):
        return self.token.line


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

    @property
    def line(self):
        return self.token.line


class Null(AST):
    def __init__(self, token):
        self.token = token
        self.value = None

    @property
    def line(self):
        return self.token.line


class String(AST):
    def __init__(self, token):
        self.token = token

    @property
    def value(self):
        if self.token.value[0] in ['"', '”', '“'] \
                and self.token.value[-1] in ['"', '”', '“']:
            return self.token.value[1:-1]
        return self.token.value

    @property
    def line(self):
        return self.token.line

    def __iter__(self):
        return iter(self.value)


class NoOp(AST):
    pass


class Class(AST):
    def __init__(self,
                 name,
                 superclass,
                 implementations,
                 body,
                 methods,
                 fields,
                 programmer):
        self.name = name
        self.superclass = superclass
        self.implementations = implementations
        self.body = body
        self.methods = methods
        self.fields = fields
        self.programmer = programmer

    @property
    def line(self):
        return self.name.line

    def __repr__(self):
        return f'<class {self.name.value}>'


class Interface(AST):
    def __init__(self, name, methods, programmer):
        self.name = name
        self.methods = methods
        self.programmer = programmer

    def __str__(self):
        raise Exception("Cannot print interface")

    @property
    def line(self):
        return self.name.line


class Get(AST):
    def __init__(self, object, name, has_parameters):
        self.object = object
        self.name = name
        self.has_parameters = has_parameters

    @property
    def value(self):
        return self.name.value

    @property
    def line(self):
        return self.name.line


class Set(AST):
    def __init__(self, object, name, value):
        self.object = object
        self.name = name
        self.value = value

    @property
    def line(self):
        return self.name.line


class Function(AST):
    def __init__(self, name, return_type, params, body, is_main):
        self.token = name
        self.name = name
        self.return_type = return_type
        self.params = params
        self.body = body
        self.is_main = is_main

    @property
    def line(self):
        return self.name.line


class Return(AST):
    def __init__(self, value):
        self.value = value

    @property
    def line(self):
        return self.value.line


class FunctionCall(AST):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

    @property
    def line(self):
        return self.name.line


class Read(AST):
    def __init__(self, variable):
        self.variable = variable

    @property
    def line(self):
        return self.variable.line


class Prompt(AST):
    def __init__(self, read_node, expr):
        self.read_node = read_node
        self.expr = expr

    @property
    def line(self):
        return self.expr.line


class VariableDeclaration(AST):
    def __init__(self, left, op, right, is_const=False):
        self.left = left
        self.token = self.op = op
        self.right = right
        self.is_const = is_const

    @property
    def line(self):
        return self.left.line


class Increment(AST):
    def __init__(self, variable, value=1):
        self.variable = variable
        self.value = value

    @property
    def line(self):
        return self.variable.line


class Decrement(AST):
    def __init__(self, variable, value=1):
        self.variable = variable
        self.value = value

    @property
    def line(self):
        return self.variable.line


class If(AST):
    def __init__(self, condition, then_branch, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    @property
    def line(self):
        return self.condition.line


class Switch(AST):
    def __init__(self, variable, cases, default):
        self.variable = variable
        self.cases = cases
        self.default = default

    @property
    def line(self):
        return self.variable.line


class While(AST):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    @property
    def line(self):
        return self.condition.line


class DoWhile(AST):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    @property
    def line(self):
        return self.condition.line


class Import(AST):
    def __init__(self, name):
        self.name = name

    @property
    def line(self):
        return self.name.line


class Array(AST):
    def __init__(self, name, type, elements=None):
        self.name = name
        self.type = type
        self.elements = elements

    @property
    def line(self):
        return self.name.line


class ArrayElementAssignment(AST):
    def __init__(self, left, index, right):
        self.left = left
        self.index = index
        self.right = right

    @property
    def array_name(self):
        return self.left.token.value

    @property
    def line(self):
        return self.left.line


class ArrayElement(AST):
    def __init__(self, name, index):
        self.name = name
        self.index = index

    @property
    def line(self):
        return self.name.line


class For(AST):
    def __init__(self, init, to_value, body):
        self.init = init
        self.to_value = to_value
        self.body = body
        self.body.children.append(Increment(self.init.left))
        self.condition = BinOp(
            copy.copy(self.init.left),
            Token('', Keywords.LESS_THAN_OR_EQUAL,
                  Block.NONE, Suffix.NONE,
                  self.to_value.token.start, self.to_value.token.end),
            self.to_value)

    @property
    def line(self):
        return self.init.line


class ForIter(AST):
    def __init__(self, init, iterable, body):
        self.init = init
        self.iterable = iterable
        self.body = body

    @property
    def line(self):
        return self.init.line

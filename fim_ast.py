class AST:
    pass


class Compound(AST):
    def __init__(self):
        self.children = []


class Assign(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Print(AST):
    def __init__(self, expr):
        self.expr = expr


class Var(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


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
        self.value = float(token.value)


class Char(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value
        if token.value[0] == "'" and token.value[-1] == "'":
            self.value = token.value[1:-1]


class String(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value
        if token.value[0] in ['"', '”', '“']\
                and token.value[-1] in ['"', '”', '“']:
            self.value = token.value[1:-1]

class NoOp(AST):
    pass

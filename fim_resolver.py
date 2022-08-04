from node_visitor import NodeVisitor
from enum import Enum


class FunctionType(Enum):
    NONE = 0,
    FUNCTION = 1,


class Resolver(NodeVisitor):
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.scopes = [{}]
        self.current_function = FunctionType.NONE

    def visit_Compound(self, compound):
        self.begin_scope()
        self.resolve_statements(compound.children)
        self.end_scope()

    def resolve_statements(self, children):
        for child in children:
            self.resolve_statement(child)

    def resolve_statement(self, statement):
        self.visit(statement)

    def resolve_expression(self, expression):
        self.visit(expression)

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def visit_VariableDeclaration(self, statement):
        self.declare(statement.left.value)
        if statement.right:
            self.resolve_expression(statement.right)
        self.define(statement.left.value)

    def declare(self, name):
        if len(self.scopes) == 0:
            return
        scope = self.scopes[-1]
        if name in scope:
            self.interpreter.error(name, "Variable with this name already declared in this scope.")
        scope[name] = False

    def define(self, name):
        if len(self.scopes) == 0:
            return
        scope = self.scopes[-1]
        scope[name] = True

    def visit_Var(self, expression):
        if len(self.scopes) != 0 and self.scopes[-1].get(expression.value) is False:
            self.interpreter.error(expression.token, "Cannot read local variable in its own initializer.")

        self.resolve_local(expression, expression.value)

    def resolve_local(self, expression, name):
        for i, scope in enumerate(reversed(self.scopes)):
            if name in scope:
                self.interpreter.resolve(expression, len(self.scopes) - 1 - i)
                return
        raise Exception(name, "Undefined variable '%s'." % name)

    def visit_Assign(self, expression):
        self.resolve_expression(expression.value)
        self.resolve_local(expression, expression.name)

    def visit_Function(self, statement):
        self.declare(statement.name)
        self.define(statement.name)
        self.resolve_function(statement, FunctionType.FUNCTION)

    def resolve_function(self, statement, function_type):
        enclosingFunction = self.current_function
        self.current_function = function_type

        self.begin_scope()
        for param in statement.params:
            self.declare(param)
            self.define(param)
        self.resolve_statements(statement.body.children)
        self.end_scope()
        self.current_function = enclosingFunction

    def visit_If(self, statement):
        self.resolve_expression(statement.condition)
        self.resolve_statements(statement.then_branch)
        if statement.else_branch:
            self.resolve_statements(statement.else_branch)

    def visit_Print(self, expression):
        self.resolve_expression(expression.expr)

    def visit_Return(self, statement):
        if self.current_function == FunctionType.NONE:
            self.interpreter.error(statement.token, "Cannot return from top-level code.")

        if statement.value:
            self.resolve_expression(statement.value)

    def visit_While(self, statement):
        self.resolve_expression(statement.condition)
        self.resolve_statements(statement.body)

    def visit_DoWhile(self, statement):
        self.resolve_statements(statement.body)
        self.resolve_expression(statement.condition)

    def visit_BinOp(self, expression):
        self.resolve_expression(expression.left)
        self.resolve_expression(expression.right)

    def visit_FunctionCall(self, expression):
        self.resolve_expression(expression.name)
        for arg in expression.arguments:
            self.resolve_expression(arg)

    def visit_Number(self, node):
        pass

    def visit_String(self, node):
        pass

    def visit_Char(self, node):
        pass

    def visit_Bool(self, node):
        pass

    def visit_Null(self, node):
        pass

    def visit_UnaryOp(self, expression):
        self.resolve_expression(expression.right)

    def visit_Increment(self, expression):
        self.resolve_expression(expression)

    def visit_NoOp(self, node):
        pass
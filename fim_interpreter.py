import copy
import special_words

import fim_ast
from fim_lexer import Literals
from fim_lexer import Keywords, Token
from fim_callable import FimClass, FimCallable
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

    def reset(self):
        self.globals = Environment()
        self.environment = self.globals
        self.locals = {}

    def interpret(self, tree):
        for variable in self.globals._values.values():
            if isinstance(variable, fim_ast.AST):
                self.visit(variable)
        return self.visit(tree)

    def resolve(self, node, depth):
        self.locals[node] = depth

    def set_builtin_globals(self):
        self.globals.define(
            special_words.base_class_name, FimClass(special_words.base_class_name, None, {}, {}))

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
        elif node.op.type == Keywords.CONCAT:
            left = self.visit(node.left)
            right = self.visit(node.right)
            return stringify(left) + stringify(right)

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

    def visit_Root(self, node):
        for declaration in node.children:
            if isinstance(declaration, fim_ast.Class):
                continue
            self.visit(declaration)

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
        distance = self.locals.get(node.left)
        if distance is not None:
            self.environment.assign_at(distance, node.left.token, value)
        else:
            try:
                instance = self.environment.get(special_words.this)
                instance.set(node.left, value)
            except NameError:
                self.globals.assign(node.left, value)

        return value

    def visit_VariableDeclaration(self, node):
        var_name = node.left.value
        self.environment.define(var_name, self.visit(node.right))

    def visit_Var(self, node):
        val = self.lookup_variable(node.token, node)
        if isinstance(val, fim_callable.FimCallable) and val.arity() == 0:
            return val.call(self, [])
        return val

    def lookup_variable(self, token, node):
        distance = self.locals.get(node)
        if distance is not None:
            return self.environment.get_at(distance, token.value)
        else:
            try:
                instance = self.environment.get(special_words.this)
                res = instance.get(token)
                # if isinstance(res, fim_callable.FimCallable):
                #     return FunctionWrapper(res)
                return res
            except (NameError, RuntimeError):
                return self.globals.get(token.value)

    def visit_FunctionCall(self, node):
        function = self.visit(node.name)
        # if isinstance(function, FunctionWrapper):
        #     function = function.function

        arguments = []
        for argument in node.arguments:
            arguments.append(self.visit(argument))

        if len(arguments) != function.arity():
            raise RuntimeError("Function '{}' expected {} arguments, got {}".format(node, function.arity(), len(arguments)))

        if isinstance(function, fim_callable.FimCallable):
            return function.call(self, arguments)
        else:
            raise RuntimeError("{} is not a function".format(node))

    def visit_Return(self, node):
        value = None
        if node.value is not None:
            value = self.visit(node.value)
        raise fim_callable.FimReturn(value)

    def visit_Increment(self, node):
        distance = self.locals.get(node.variable)
        self.environment.modify_at(distance, node.variable.token, operator.add, 1)

    def visit_Decrement(self, node):
        distance = self.locals.get(node.variable)
        self.environment.modify_at(distance, node.variable.token, operator.sub, 1)

    def visit_Print(self, node):
        res = self.visit(node.expr)
        print(stringify(res))

    def visit_Read(self, node):
        line = input()
        self.visit_Assign(fim_ast.Assign(
            node.variable,
            fim_ast.String(
                Token(line, Literals.STRING, None, None, None, None))))

    def visit_Function(self, node):
        self.environment.declare(node.name)
        fim_function = fim_callable.FimFunction(node, self.environment)
        self.environment.assign(node.name, fim_function)

    def visit_Class(self, node):
        superclass = self.lookup_variable(node.superclass.token, node.superclass)

        if isinstance(superclass, fim_ast.AST):
            superclass = self.visit(superclass)

        if not isinstance(superclass, FimClass):
            raise RuntimeError("{} is not a class".format(superclass))

        #   I use assign because it was defined as fim_ast.Class in resolver
        self.environment.assign(node.name, None)

        methods = {}
        main_method_token = None
        for method in node.methods:
            function = fim_callable.FimFunction(method, self.environment)
            methods[method.token.value] = function
            if method.is_main:
                main_method_token = function.declaration.token

        fields = {}
        for field in node.fields:
            fields[field.left.value] = self.visit(field.right)

        fim_class = FimClass(node.name.value, superclass, methods, fields)
        self.environment.assign(node.name, fim_class)

        if main_method_token is not None:
            instance = fim_class.call(self, [])
            instance.get(main_method_token).call(self, [])

    def visit_Interface(self, node):
        pass

    def visit_Get(self, node):
        obj = self.visit(node.object)
        if isinstance(obj, fim_callable.FimInstance):
            field = obj.get(node.name)
            if isinstance(field, FimCallable) and not node.has_parameters:
                return field.call(self, [])
            return field
        raise RuntimeError("{} only instances have properties".format(obj))

    def visit_Set(self, node):
        obj = self.visit(node.object)
        if isinstance(obj, fim_callable.FimInstance):
            value = self.visit(node.value)
            obj.set(node.name, value)
            return value
        raise RuntimeError("{} only instances have properties".format(obj))

    def visit_Switch(self, node):
        cases = {}
        for case, body in node.cases.items():
            cases[self.visit(case)] = body
        variable_value = self.visit(node.variable)
        if variable_value in cases:
            self.visit(cases[variable_value])
        else:
            self.visit(node.default)

    def visit_Import(self, node):
        pass


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


# class FunctionWrapper:
#     def __init__(self, function):
#         self.function = function

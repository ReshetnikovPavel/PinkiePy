import special_words

import fim_ast
import utility
from fim_lexer import Keywords, Literals, Token
from fim_callable import FimClass, FimCallable
from fim_exception import FimRuntimeException
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
        for variable in self.globals.values():
            if isinstance(variable, fim_ast.AST):
                self.visit(variable)
        return self.visit(tree)

    def resolve(self, node, depth):
        self.locals[node] = depth

    def set_builtin_globals(self):
        self.globals.define(
            special_words.base_class_name,
            FimClass(special_words.base_class_name, None, {}, {}))
        self.define_builtin_types()

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        try:
            if node.op.type == Keywords.ADDITION:
                return left + right
            elif node.op.type == Keywords.SUBTRACTION:
                return left - right
            elif node.op.type == Keywords.MULTIPLICATION:
                return left * right
            elif node.op.type == Keywords.DIVISION:
                return left / right
            elif node.op.type == Keywords.GREATER_THAN:
                return left > right
            elif node.op.type == Keywords.LESS_THAN:
                return left < right
            elif node.op.type == Keywords.GREATER_THAN_OR_EQUAL:
                return left >= right
            elif node.op.type == Keywords.LESS_THAN_OR_EQUAL:
                return left <= right
            elif node.op.type == Keywords.EQUAL:
                return left == right
            elif node.op.type == Keywords.NOT_EQUAL:
                return left != right
            elif node.op.type == Keywords.AND:
                if type(left) == float and type(right) == float:
                    return left + right
                else:
                    return left and right
            elif node.op.type == Keywords.OR:
                return left or right
            elif node.op.type == Keywords.XOR:
                return left ^ right
            elif node.op.type == Keywords.CONCAT:
                return stringify(left) + stringify(right)
            elif node.op.type == Keywords.MODULO:
                return left % right
            else:
                raise FimRuntimeException(node.op,
                                          f"Unknown operator: {node.op}")
        except TypeError:
            raise FimRuntimeException(
                node.op,
                f'Cannot perform operation {node.op.value}'
                f' with {stringify(left)} and {stringify(right)}')

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

    def visit_For(self, node):
        self.visit(node.init)
        body = node.body
        self.visit(fim_ast.While(node.condition, body))

    def visit_ForIter(self, node):
        self.visit(node.init)
        for i in iter(self.visit(node.iterable)):
            self.environment.assign(node.init.left, i)
            self.visit(node.body)

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
            except FimRuntimeException:
                self.globals.assign(node.left, value)

        return value

    def visit_VariableDeclaration(self, node):
        var_name = node.left.value
        self.environment.define(var_name, self.visit(node.right))

    def visit_Var(self, node):
        val = self.lookup_variable(node.token, node)
        if hasattr(node, 'index'):
            if utility.is_float_and_int(node.index):
                index = int(node.index)
            else:
                raise FimRuntimeException(
                    node.token,
                    f"index {node.index} must be an integer")
            return val.elements[index]

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
                return res
            except FimRuntimeException:
                return self.globals.get(token.value)

    def visit_FunctionCall(self, node):
        function = self.visit(node.name)

        arguments = []
        for argument in node.arguments:
            arguments.append(self.visit(argument))

        if len(arguments) != function.arity():
            raise FimRuntimeException(
                node.name,
                f"Function '{node}' expected {function.arity()}"
                f" arguments, got {len(arguments)}")

        if isinstance(function, fim_callable.FimCallable):
            return function.call(self, arguments)
        else:
            raise FimRuntimeException(node.name, f"{node} is not a function")

    def visit_Return(self, node):
        value = None
        if node.value is not None:
            value = self.visit(node.value)
        raise fim_callable.FimReturn(value)

    def visit_Increment(self, node):
        distance = self.locals.get(node.variable)
        if isinstance(node.value, int):
            value = node.value
        else:
            value = self.visit(node.value)
        if distance is None:
            self.environment.modify(node.variable.token, operator.add, value)
        else:
            self.environment.modify_at(
                distance, node.variable.token, operator.add, value)

    def visit_Decrement(self, node):
        distance = self.locals.get(node.variable)
        if distance is None:
            self.environment.modify(node.variable.token, operator.sub, 1)
        else:
            self.environment.modify_at(
                distance, node.variable.token, operator.sub, 1)

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
        superclass = self.lookup_variable(
            node.superclass.token, node.superclass)

        if isinstance(superclass, fim_ast.AST):
            superclass = self.visit(superclass)

        if not isinstance(superclass, FimClass):
            raise FimRuntimeException(node.superclass.token,
                                      f"{superclass} is not a class")

        #   I use assign because it was defined as fim_ast.Class in resolver
        self.environment.assign(node.name, None)

        methods = {}
        main_method_token = None
        for method in node.methods.values():
            function = fim_callable.FimFunction(method, self.environment)
            methods[method.token.value] = function
            if method.is_main:
                main_method_token = function.declaration.token

        fields = {}
        for field in node.fields.values():
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
        if isinstance(obj, fim_callable.FimArray):
            array = self.visit(node.object)
            index = self.visit(node.name)
            if utility.is_float_and_int(index):
                index = int(index)
            else:
                raise FimRuntimeException(node.name,
                                          f"Index {index} must be an integer")
            return array.elements[index]
        if isinstance(obj, fim_callable.FimInstance):
            field = obj.get(node.name)
            if isinstance(field, FimCallable) and not node.has_parameters:
                return field.call(self, [])
            return field
        raise FimRuntimeException(
            node.object.token,
            f"{node.object.token} only instances or arrays have properties")

    def visit_Set(self, node):
        obj = self.visit(node.object)
        if isinstance(obj, fim_callable.FimInstance):
            value = self.visit(node.value)
            obj.set(node.name, value)
            return value
        raise FimRuntimeException(
            node.object.token,
            f"{node.object.token} only instances have properties")

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

    def visit_Array(self, node):
        array_name = node.name.value
        elements = []
        if isinstance(node.elements, fim_ast.BinOp):
            bin_op = node.elements
            while isinstance(bin_op, fim_ast.BinOp):
                elements.append(self.visit(bin_op.right))
                bin_op = bin_op.left

        self.environment.define(array_name, fim_callable.FimArray(elements))

    def visit_ArrayElementAssignment(self, node):
        array = self.lookup_variable(node.left.token, node.left)

        if not isinstance(node.index, int):
            index = self.visit(node.index)
            if utility.is_float_and_int(index):
                index = int(index)
            node.index = index

        if node.index >= len(array.elements):
            array.elements.extend(
                [None] * (node.index - len(array.elements) + 1))
        array.elements[node.index] = self.visit(node.right)

    def define_builtin_types(self):
        builtin_types = [
            'number', 'a number', 'the number',
            'letter', 'a letter', 'the letter',
            'character', 'a character', 'the character',
            'sentence', 'phrase', 'quote', 'word', 'name',
            'a sentence', 'a phrase', 'a quote', 'a word', 'a name',
            'the sentence', 'the phrase', 'the quote', 'the word', 'the name',
            'logic', 'the logic', 'argument', 'an argument', 'the argument']

        for name in builtin_types:
            self.environment.define(name, None)


def stringify(obj):
    # if res is float and can be int, convert it to int
    if utility.is_float_and_int(obj):
        return str(int(obj))
    if obj is None:
        return "nothing"
    if obj is True:
        return "true"
    if obj is False:
        return "false"
    return str(obj)

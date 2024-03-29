import contextlib
from pathlib import Path

import special_words
from fim_exception import FimResolverException
from fim_interpreter import Interpreter
from fim_lexer import Lexer, Literals
from fim_parser import Parser
from node_visitor import NodeVisitor
from enum import Enum
import re
import utility


def interpret(program):
    lexer = Lexer(program)
    lexer.lex()
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    tree = parser.parse()
    resolver = Resolver(interpreter)
    resolver.resolve(tree)
    interpreter.interpret(tree)

    return interpreter.globals, interpreter.locals


class FunctionType(Enum):
    NONE = 0
    FUNCTION = 1
    METHOD = 2


class ClassType(Enum):
    NONE = 0
    CLASS = 1


class Resolver(NodeVisitor):
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.scopes = []
        self.scopes_for_typechecking = []
        self.globals_for_typechecking = {}
        self.current_function = FunctionType.NONE
        self.current_class = None
        self.interpreter.set_builtin_globals()
        self.main_was_initialized = False
        self.interfaces_to_be_checked = {}
        self.builtin_type_names = {
            Literals.NUMBER:
                r'^(?:(?:a )|(?:the ))?number',
            Literals.CHAR:
                r'^(?:(?:a )|(?:the ))?(?:(?:letter)|(?:character))',
            Literals.STRING:
                r'^(?:(?:a )|(?:the ))?'
                r'(?:(?:sentence)|(?:phrase)|(?:quote)|(?:word)|(?:name))',
            Literals.BOOL:
                r'^(?:(?:(?:the )?logic)|(?:(?:an )|(?:the ))?argument)'}
        self.new_type_names = {}
        for type_name, regex in self.builtin_type_names.items():
            self.builtin_type_names[type_name] = re.compile(regex)

    def visit_Compound(self, node):
        with self.scope():
            self.resolve_statements(node.children)

    @contextlib.contextmanager
    def scope(self):
        self._begin_scope()
        yield
        self._end_scope()

    def _begin_scope(self):
        self.scopes.append({})
        self.scopes_for_typechecking.append({})

    def _end_scope(self):
        self.scopes.pop()
        self.scopes_for_typechecking.pop()

    def visit_Root(self, node):
        self.resolve_statements(node.children)

    def resolve_statements(self, statements):
        for statement in statements:
            self.visit(statement)

    def resolve(self, node):
        if isinstance(node, list):
            self.resolve_statements(node)
            return
        self.visit(node)

    def visit_VariableDeclaration(self, node):
        self.declare(node.left)
        if node.right is not None:
            type = self.visit(node.right)
            self.set_type(node.left.token, type)
        self.define(node.left)

    def declare(self, name):
        if len(self.scopes) == 0:
            return
        scope = self.scopes[-1]
        if name.value in scope:
            raise FimResolverException(name,
                                       f"{name.value} is already defined")
        scope[name.value] = False

    def define(self, name):
        if len(self.scopes) == 0:
            return
        scope = self.scopes[-1]
        scope[name.value] = True

    def set_type(self, name, type):
        if len(self.scopes_for_typechecking) == 0:
            self.globals_for_typechecking[name.value] = type
            return
        scope = self.scopes_for_typechecking[-1]
        scope[name.value] = type

    def visit_Var(self, node):
        array_name = utility.separate_array_name(node.value)
        array_index = utility.separate_index(node.value)
        if array_index is not None:
            if len(self.scopes) == 0:
                is_defined = array_name in self.interpreter.globals \
                             or array_name in self.globals_for_typechecking
            else:
                is_defined = self.scopes[-1].get(array_name)
            if is_defined \
                    and isinstance(self.get_type(array_name), tuple) \
                    and self.get_type(array_name)[0] == Literals.ARRAY:
                node.token.value = array_name
                node.index = array_index
                self.resolve_local(node, node.token)
                variable_type, variable_token = self.typecheck(node.token)
                return variable_type[1]

        variable_type, variable_token = self.typecheck(node.token)
        node.token = variable_token

        if not self.is_in_scopes(node.value):
            raise FimResolverException(node.token,
                                       f"{node.value} is not defined")

        self.resolve_local(node, node.token)

        return variable_type

    def is_in_scopes(self, name):
        for scope in self.scopes:
            if name in scope and scope[name] is True:
                return True

        if any(map(lambda x: name in x,
                   (self.interpreter.globals, self.globals_for_typechecking))):
            return True

        if self.current_class is not None:
            if name in self.current_class.fields \
                    or name in self.current_class.methods:
                return True
        return False

    def typecheck(self, token):
        variable_type, variable_token = self.separate_type(token)
        if not self.is_instance(variable_type, variable_token):
            raise FimResolverException(
                token,
                f"{variable_token.value}"
                f" is not an instance of {variable_type}")
        return variable_type, variable_token

    def resolve_local(self, node, name):
        for i in reversed(range(len(self.scopes))):
            if name.value in self.scopes[i]:
                self.interpreter.resolve(node, len(self.scopes) - 1 - i)
                return

    def get_type(self, name):
        for i in reversed(range(len(self.scopes_for_typechecking))):
            if name in self.scopes_for_typechecking[i]:
                return self.scopes_for_typechecking[i][name]

        if self.current_class is not None \
                and name in map(lambda x: x.name.value,
                                self.current_class.methods.values()):

            return_type_token = self.current_class.methods[name].return_type
            if return_type_token is not None:
                return_type, token = self.separate_type(return_type_token)
                return return_type

        if name in self.globals_for_typechecking:
            return self.globals_for_typechecking[name]
        return None

    def visit_Assign(self, node):
        self.resolve(node.right)
        self.resolve_local(node.left, node.left.token)

    def visit_Class(self, node):
        self.declare(node.name)
        self.define(node.name)

        self.interpreter.globals.define(node.name.value, node)

        if node.name.value == node.superclass.token.value:
            raise FimResolverException(node.name,
                                       "A class cannot inherit from itself")
        self.resolve(node.superclass)

        self._handle_class_interface_implementations(node)
        self.resolve_class_body(node)

    def _handle_class_interface_implementations(self, node):
        for interface_token in node.implementations:
            if interface_token.value in self.interpreter.globals:
                self.check_interface(
                    self.interpreter.globals.get(interface_token.value), node)
            elif interface_token.value in self.interfaces_to_be_checked:
                self.interfaces_to_be_checked[interface_token.value].append(
                    node)
            else:
                self.interfaces_to_be_checked[interface_token.value] = [node]

    def resolve_class_body(self, node):
        with self.scope():
            self.scopes[-1][special_words.this] = True
            self.current_class = node

            for method in node.methods.values():
                declaration = FunctionType.METHOD
                self.resolve_function(method, declaration)

            for field in node.fields.values():
                self.resolve(field)

            self.current_class = None

    def visit_Get(self, node):
        type = self.get_type(node.object.value)
        if isinstance(type, tuple) and type[0] == Literals.ARRAY:
            self.resolve(node.name)
        self.resolve(node.object)

    def visit_Set(self, node):
        self.resolve(node.value)
        self.resolve(node.object)

    def visit_Function(self, node):
        self.declare(node.token)
        self.define(node.token)
        self.set_type(node.token, node.return_type)
        self.resolve_function(node, FunctionType.FUNCTION)

    def resolve_function(self, node, function_type):
        if node.is_main:
            if self.main_was_initialized:
                raise FimResolverException(
                    node.token,
                    f"Cannot have more than one main function")
            self.main_was_initialized = True

        enclosing_function = self.current_function
        self.current_function = function_type

        with self.scope():
            self.resolve_function_parameters(node)
            self.resolve(node.body)
        self.current_function = enclosing_function

    def resolve_function_parameters(self, node):
        for param in node.params:
            variable_type, variable_token = self.separate_type(param)
            param = variable_token
            self.set_type(param, variable_type)
            self.declare(param)
            self.define(param)

    def visit_If(self, node):
        self.resolve(node.condition)
        self.resolve(node.then_branch)
        if node.else_branch is not None:
            self.resolve(node.else_branch)

    def visit_Print(self, node):
        self.resolve(node.expr)

    def visit_Return(self, node):
        if self.current_function == FunctionType.NONE:
            raise FimResolverException(
                node.value,
                f"Cannot return from top-level code")

        if node.value is not None:
            self.resolve(node.value)

    def visit_While(self, node):
        self.resolve(node.condition)
        self.resolve(node.body)

    def visit_DoWhile(self, node):
        self.resolve(node.body)
        self.resolve(node.condition)

    def visit_For(self, node):
        variable_type, variable_token = self.separate_type(
            node.init.left.token)
        node.token = variable_token
        self.set_type(node.init.left.token, variable_type)
        self.resolve(node.init)
        self.resolve(node.condition)
        self.resolve(node.body)

    def visit_ForIter(self, node):
        variable_type, variable_token = self.separate_type(
            node.init.left.token)
        node.token = variable_token
        self.set_type(node.init.left.token, variable_type)
        self.resolve(node.init)
        self.resolve(node.iterable)
        type = self.get_type(node.iterable.token.value)
        if isinstance(type, tuple) and type[0] == Literals.ARRAY:
            if type[1] != variable_type:
                raise FimResolverException(
                    node.iterable.token,
                    f"{node.init.left.token.value}"
                    f" is not an instance of {type[1]}")
        self.resolve(node.body)

    def visit_Increment(self, node):
        self.resolve(node.variable)
        if not isinstance(node.value, int):
            self.resolve(node.value)

    def visit_Decrement(self, node):
        self.resolve(node.variable)

    def visit_String(self, node):
        variable_type, variable_token = self.typecheck(node.token)
        node.token = variable_token
        return variable_type

    def visit_Char(self, node):
        variable_type, variable_token = self.typecheck(node.token)
        node.token = variable_token
        return variable_type

    def visit_Number(self, node):
        variable_type, variable_token = self.typecheck(node.token)
        node.token = variable_token
        return variable_type

    def visit_BinOp(self, node):
        self.resolve(node.left)
        self.resolve(node.right)

    def visit_FunctionCall(self, node):
        self.resolve(node.name)

        for arg in node.arguments:
            self.resolve(arg)

    def visit_UnaryOp(self, node):
        self.resolve(node.expr)

    def visit_NoOp(self, node):
        pass

    def visit_Bool(self, node):
        variable_type, variable_token = self.typecheck(node.token)
        node.token = variable_token
        return variable_type

    def visit_Null(self, node):
        pass

    def visit_Read(self, node):
        self.resolve(node.variable)

    def visit_Interface(self, node):
        self.interpreter.globals.define(node.name.value, node)
        if node.name.value in self.interfaces_to_be_checked:
            for fim_class in self.interfaces_to_be_checked[node.name.value]:
                self.check_interface(node, fim_class)

    @staticmethod
    def check_interface(interface, fim_class):
        for method in interface.methods:
            if method.name.value not in map(lambda m: m.name.value,
                                            fim_class.methods.values()):
                raise FimResolverException(
                    interface.name,
                    f"{fim_class.name.value}"
                    f" does not implement {method.name.value}")

    def visit_Switch(self, node):
        self.resolve(node.variable)
        for case_condition, body in node.cases.items():
            self.resolve(case_condition)
            self.resolve(body)
        if node.default is not None:
            self.resolve(node.default)

    @staticmethod
    def find_module_path(module_name):
        for path in Path().rglob(f'{module_name}{special_words.extension}'):
            return path.absolute()

    def visit_Import(self, node):
        program_file_path = self.find_module_path(node.name.value)
        if program_file_path is None:
            raise FimResolverException(
                node.name,
                f"Cannot find module {node.name.value}")

        with program_file_path.open('r') as program_file:
            program = program_file.read()
            imported_globals, imported_locals = interpret(program)
            imported_class = self.make_class_from_env(
                imported_globals, node.name.value)

            if imported_class is None:
                raise FimResolverException(
                    node.name,
                    f"Cannot find class {node.name.value}"
                    f" in module {node.name.value}")

            self.interpreter.globals.define(node.name.value, imported_class)
            for name, info in imported_locals.items():
                self.interpreter.locals[name] = info

    @staticmethod
    def make_class_from_env(env, class_name):
        methods = {}
        fields = {}
        for key, value in env.items():
            if isinstance(value, FunctionType):
                methods[key] = value
            elif key == special_words.base_class_name:
                continue
            #   if the name of module is the same as the name of class,
            #   then we import only this class
            #   to make import work kinda like on wikia page
            elif key == class_name:
                return env.get(key)
            else:
                fields[key] = value

        #   res = fim_callable.FimClass(class_name, None, methods, fields)
        #   return res
        return None

    def separate_type(self, token):
        for type_name, regex in self.builtin_type_names.items():
            match = re.match(regex, token.value)
            if match:
                value = str.removeprefix(token.value, match.group(0)).strip()
                if value == "" or value == 'nothing':
                    token.value = str.removesuffix(token.value, value).strip()
                    token.type = type_name
                    return type_name, token
                token.value = value
                return type_name, token
        # for name in self.interpreter.globals._values:
        #     if isinstance(self.interpreter.globals._values.get(name),
        #                   fim_callable.FimClass):
        #         if token.value.startswith(name):
        #             value = str.removeprefix(token.value, name).strip()
        #             if value == "":
        #                 return None, token
        #             token.value = value
        #             return name, token
        return self.get_type(token.value), token

    def is_instance(self, type, token):
        if type is None:
            return True
        if token.type != Literals.ID:
            token_type = Literals.BOOL \
                if token.type in (Literals.TRUE, Literals.FALSE) \
                else token.type
            return type == token_type
        else:
            return type == self.get_type(token.value)

    def visit_Array(self, node):
        self.declare(node.name.token)
        self.define(node.name.token)
        self.resolve_local(node, node.name.token)
        possible_type_names = self.get_possible_array_type_names(
            node.type.token)
        type = node.type.token.value
        for possible_type_name in possible_type_names:
            for key, regex in self.builtin_type_names.items():
                if re.match(regex, possible_type_name):
                    type = key
                    self.set_type(node.name.token, (Literals.ARRAY, type))
                    return
        raise FimResolverException(
            node.type.token,
            f"Cannot make array of this type: {type}")

    @staticmethod
    def get_possible_array_type_names(type_token):
        possible_type_names = []
        type = type_token.value
        if type.endswith('es'):
            possible_type_names.append(type[:-2])
        if type.endswith('s'):
            possible_type_names.append(type[:-1])
        else:
            raise FimResolverException(
                type_token,
                f"Array type should be in plural form: {type}")

        return possible_type_names

    def visit_ArrayElementAssignment(self, node):
        expected_type = self.get_type(node.array_name)
        if expected_type[0] != Literals.ARRAY:
            raise FimResolverException(
                node.array_name,
                f"{node.array_name} is not an array")
        right_type = self.visit(node.right)
        self.visit(node.left)
        if not isinstance(node.index, int):
            self.visit(node.index)
        if right_type is None:
            right_type = node.right.token.type
        if expected_type[1] != right_type:
            raise FimResolverException(
                node.right.token,
                f"Expected {expected_type} but got {right_type}")

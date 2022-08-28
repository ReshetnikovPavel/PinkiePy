import unittest

import fim_ast
import fim_exception
from fim_callable import FimFunction
from fim_interpreter import Interpreter
from fim_lexer import Lexer, Literals, Keywords, Token
from fim_parser import Parser
from fim_resolver import Resolver
from fim_callable import FimClass, FimInstance
from environment import Environment


class Base(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser(self.lexer)
        self.interpreter = Interpreter(self.parser)
        self.resolver = Resolver(self.interpreter)

    def set_up_program(self, program):
        self.lexer.set_source(program)
        self.lexer.lex()
        self.parser.parse()

    def tearDown(self):
        pass


class InterpreterTests(Base):
    def testResolve(self):
        expr = fim_ast.Var(Token(Literals.ID, 'a', None, None, None, None))
        self.interpreter.resolve(expr, 4)
        self.assertTrue(self.interpreter.locals[expr] == 4)

    def testVisitVar(self):
        token = Token(Literals.ID, 'a', None, None, None, None)
        expr = fim_ast.Var(token)
        distance = 4
        self.interpreter.locals[expr] = distance
        self.interpreter.environment.define(token.value, "Hello World!")
        for i in range(distance):
            self.interpreter.environment = Environment(
                self.interpreter.environment)
        res = self.interpreter.visit_Var(expr)
        self.assertTrue(res == "Hello World!")

    def testVisitVarNoInfoAboutScope(self):
        token = Token(Literals.ID, 'a', None, None, None, None)
        expr = fim_ast.Var(token)
        self.interpreter.globals.define(token.value, "Hello World!")
        res = self.interpreter.visit_Var(expr)
        self.assertTrue(res == "Hello World!")

    def testVisitVarIsFunctionSoItShouldBeCalled(self):
        token = Token(Literals.ID, 'a', None, None, None, None)
        expr = fim_ast.Var(token)
        distance = 4
        self.interpreter.locals[expr] = distance

        function_body = fim_ast.Compound()
        function_body.children.append(
            fim_ast.Return(
                fim_ast.Number(
                    Token(1, Literals.NUMBER, None, None, None, None))))
        function_declaration = fim_ast.Function(
            token, None, [], function_body, False)
        function = FimFunction(
            function_declaration, self.interpreter.environment)

        self.interpreter.environment.define(token.value, function)
        for i in range(distance):
            self.interpreter.environment = Environment(
                self.interpreter.environment)
        res = self.interpreter.visit_Var(expr)
        self.assertTrue(res == 1)

    def testLookUpVariable(self):
        token = Token(Literals.ID, 'a', None, None, None, None)
        expr = fim_ast.Var(token)
        distance = 4
        self.interpreter.locals[expr] = distance
        self.interpreter.environment.define(token.value, "Hello World!")
        for i in range(distance):
            self.interpreter.environment = Environment(
                self.interpreter.environment)
        res = self.interpreter.lookup_variable(token, expr)
        self.assertTrue(res == "Hello World!")

    def testLookUpVariableNoInfoAboutScope(self):
        token = Token(Literals.ID, 'a', None, None, None, None)
        expr = fim_ast.Var(token)
        self.interpreter.globals.define(token.value, "Hello World!")
        res = self.interpreter.lookup_variable(token, expr)
        self.assertTrue(res == "Hello World!")

    def testVisitAssign(self):
        token = Token(Literals.ID, 'a', None, None, None, None)
        expr = fim_ast.Assign(
            fim_ast.Var(token),
            fim_ast.String(
                Token('after', Literals.STRING, None, None, None, None)))
        distance = 4
        self.interpreter.locals[expr] = distance
        self.interpreter.environment.define(token.value, "before")
        for i in range(distance):
            self.interpreter.environment = Environment(
                self.interpreter.environment)
        res = self.interpreter.visit_Assign(expr)
        self.assertTrue(res == "after")

    def testVisitClass(self):
        body = fim_ast.Compound()
        body.children = [fim_ast.NoOp()]
        ast_class = fim_ast.Class(
            Token('A', Literals.ID, None, None, None, None),
            fim_ast.Var(Token(
                'Princess Celestia', Literals.ID, None, None, None, None)),
            [],
            body,
            {},
            {},
            Token('Programmer Name', Literals.ID, None, None, None, None))
        self.interpreter.environment.define(ast_class.name.value, ast_class)
        self.interpreter.visit_Class(ast_class)
        self.assertTrue('A' in self.interpreter.environment._values)
        self.assertTrue(isinstance(self.interpreter.environment._values['A'],
                                   FimClass))
        self.assertTrue(self.interpreter.environment._values['A'].name == 'A')

    def testVisitGet(self):
        pony = Token('Pony', Literals.ID, None, None, None, None)
        applejack = Token('Applejack', Literals.ID, None, None, None, None)
        hat = Token('hat', Literals.ID, None, None, None, None)
        instance = FimInstance(
            fim_ast.Class(pony, None, [], fim_ast.Compound(), [], [], None), {})
        self.interpreter.environment.define(pony.value, instance)
        self.interpreter.environment.get('Pony').fields['hat'] = \
            fim_ast.String(Token('value', Literals.ID, None, None, None, None))
        self.interpreter.visit_VariableDeclaration(
            fim_ast.VariableDeclaration(applejack, None, fim_ast.Var(pony)))

        get = fim_ast.Get(fim_ast.Var(applejack), hat, [])
        res = self.interpreter.visit_Get(get)

        self.assertTrue(res.value == 'value')

    def testVisitGetIfNoField(self):
        pony = Token('Pony', Literals.ID, None, None, None, None)
        applejack = Token('Applejack', Literals.ID, None, None, None, None)
        hat = Token('hat', Literals.ID, None, None, None, None)
        instance = FimInstance(
            fim_ast.Class(pony, None, [], fim_ast.Compound(), [], [], None), {})
        self.interpreter.environment.define(pony.value, instance)

        self.interpreter.visit_VariableDeclaration(
            fim_ast.VariableDeclaration(applejack, None, fim_ast.Var(pony)))

        get = fim_ast.Get(fim_ast.Var(applejack), hat, False)
        with self.assertRaises(Exception):
            self.interpreter.visit_Get(get)

    def testVisitSet(self):
        pony = Token('Pony', Literals.ID, None, None, None, None)
        applejack = Token('Applejack', Literals.ID, None, None, None, None)
        hat = Token('hat', Literals.ID, None, None, None, None)
        instance = FimInstance(
            fim_ast.Class(pony, None, [], fim_ast.Compound(), [], [], None), {})
        self.interpreter.environment.define(pony.value, instance)

        self.interpreter.visit_VariableDeclaration(
            fim_ast.VariableDeclaration(applejack, None, fim_ast.Var(pony)))

        set = fim_ast.Set(fim_ast.Var(applejack),
                          hat,
                          fim_ast.String(Token(
                              'value', Literals.ID, None, None, None, None)))
        res = self.interpreter.visit_Set(set)

        self.assertTrue(res == 'value')
        self.assertTrue(
            self.interpreter.environment.get('Pony').fields['hat'] == 'value')

    def testClassMethods(self):
        body = fim_ast.Compound()
        method = fim_ast.Function(
            fim_ast.Var(Token('func', Literals.ID, None, None, None, None)),
            [],
            [],
            fim_ast.Compound(),
            False)
        body.children = [method]
        ast_class = fim_ast.Class(
            Token('A', Literals.ID, None, None, None, None),
            fim_ast.Var(Token(
                'Princess Celestia', Literals.ID, None, None, None, None)),
            [],
            body,
            {'func': method},
            {},
            Token('Programmer Name', Literals.ID, None, None, None, None))
        self.interpreter.environment.define(ast_class.name.value, ast_class)
        self.interpreter.visit_Class(ast_class)
        self.interpreter.environment._values['A'].methods['func'] = method

    def testClassSuperclassPrincessCelestia(self):
        self.assertTrue(
            isinstance(self.interpreter.globals.get('Princess Celestia'),
                       FimClass))
        ast_class = fim_ast.Class(
            Token('A', Literals.ID, None, None, None, None),
            fim_ast.Var(Token('Princess Celestia', Literals.ID, None, None, None, None)),
            [],
            fim_ast.Compound(),
            {},
            {},
            Token('Programmer Name', Literals.ID, None, None, None, None))
        self.interpreter.environment.define(ast_class.name.value, ast_class)
        self.interpreter.visit_Class(ast_class)
        self.assertTrue(
            self.interpreter
            .environment
            ._values['A']
            .superclass
            .name == 'Princess Celestia')

    def testClassInheritFromNotAClass(self):
        self.interpreter.globals.define('A', 'I am totally not a class')
        ast_class = fim_ast.Class(
            Token('B', Literals.ID, None, None, None, None),
            fim_ast.Var(Token('A', Literals.ID, None, None, None, None)),
            [],
            fim_ast.Compound(),
            [],
            [],
            Token('Programmer Name', Literals.ID, None, None, None, None))
        with self.assertRaises(fim_exception.FimRuntimeException):
            self.interpreter.visit_Class(ast_class)







if __name__ == '__main__':
    unittest.main()


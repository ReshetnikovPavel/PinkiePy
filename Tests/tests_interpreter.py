import unittest

import fim_ast
from fim_callable import FimFunction
from fim_interpreter import Interpreter
from fim_lexer import Lexer, Literals, Keywords, Token
from fim_parser import Parser
from fim_resolver import Resolver
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
        function_declaration = fim_ast.Function(token, None, [], function_body, False)
        function = FimFunction(function_declaration, self.interpreter.environment)

        self.interpreter.environment.define(token.value, function)
        for i in range(distance):
            self.interpreter.environment = Environment(self.interpreter.environment)
        res = self.interpreter.visit_Var(expr)
        self.assertTrue(res == 1)

    def testLookUpVariable(self):
        token = Token(Literals.ID, 'a', None, None, None, None)
        expr = fim_ast.Var(token)
        distance = 4
        self.interpreter.locals[expr] = distance
        self.interpreter.environment.define(token.value, "Hello World!")
        for i in range(distance):
            self.interpreter.environment = Environment(self.interpreter.environment)
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
            Token('is now', Keywords.ASSIGN, None, None, None, None),
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



if __name__ == '__main__':
    unittest.main()


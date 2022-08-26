import copy
import unittest

import fim_ast
from fim_interpreter import Interpreter
from fim_lexer import Keywords
from fim_lexer import Lexer
from fim_lexer import Literals
from fim_lexer import Token
from fim_parser import Parser
from fim_resolver import Resolver, ResolverException
from node_visitor import NodeVisitor


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


class ResolverTests(Base):
    def testInit(self):
        interpreter = Interpreter(self.parser)
        resolver = Resolver(interpreter)
        self.assertTrue(resolver.interpreter is interpreter)
        self.assertTrue(isinstance(resolver, NodeVisitor))

    def testVisitCompoundStatement(self):
        compound = fim_ast.Compound()
        compound.children = [fim_ast.NoOp(), fim_ast.NoOp(), fim_ast.NoOp()]
        scopes_before = copy.copy(self.resolver.scopes)
        self.resolver.visit_Compound(compound)
        scopes_after = copy.copy(self.resolver.scopes)
        self.assertTrue(scopes_before == scopes_after)

    def testBeginScope(self):
        scopes_number_before = len(self.resolver.scopes)
        self.resolver.begin_scope()
        scopes_number_after = len(self.resolver.scopes)
        self.assertTrue(scopes_number_after == scopes_number_before + 1)
        self.assertTrue(isinstance(self.resolver.scopes[-1], dict))

    def testEndScope(self):
        scope = {'a': True}
        self.resolver.scopes.append(scope)
        self.resolver.scopes_for_typechecking.append({'a': None})
        scopes_number_before = len(self.resolver.scopes)
        self.resolver.end_scope()
        scopes_number_after = len(self.resolver.scopes)
        self.assertTrue(scopes_number_after == scopes_number_before - 1)
        self.assertFalse(scope in self.resolver.scopes)

    def testVarDeclarationScope(self):
        self.resolver.begin_scope()
        self.resolver.visit_VariableDeclaration(fim_ast.VariableDeclaration(
            fim_ast.Var(Token('a', Literals.ID, None, None, None, None)),
            Token('is', Keywords.EQUAL, None, None, None, None),
            fim_ast.String(
                Token('"a"', Literals.STRING, None, None, None, None))))
        self.assertTrue(self.resolver.scopes[-1]['a'] is True)

    def testVarDeclarationNoScope(self):
        self.resolver.visit_VariableDeclaration(fim_ast.VariableDeclaration(
            fim_ast.Var(Token('a', Literals.ID, None, None, None, None)),
            Token('is', Keywords.EQUAL, None, None, None, None),
            fim_ast.String(
                Token('"a"', Literals.STRING, None, None, None, None))))
        self.assertTrue(len(self.resolver.scopes) == 0)

    def testDeclareScopesNotEmpty(self):
        self.resolver.begin_scope()
        self.resolver.declare(Token('a', Literals.ID, None, None, None, None))
        self.assertTrue('a' in self.resolver.scopes[-1])
        self.assertTrue(self.resolver.scopes[-1]['a'] is False)

    def testDeclareScopesEmpty(self):
        scopes_before = copy.deepcopy(self.resolver.scopes)
        self.resolver.declare(Token('a', Literals.ID, None, None, None, None))
        self.assertTrue(len(scopes_before) == 0)
        self.assertTrue(len(self.resolver.scopes) == 0)
        self.assertEqual(self.resolver.scopes, scopes_before)

    def testDeclareVariableAlreadyExists(self):
        self.resolver.begin_scope()
        self.resolver.declare(Token('a', Literals.ID, None, None, None, None))
        with self.assertRaises(ResolverException):
            self.resolver.declare(
                Token('a', Literals.ID, None, None, None, None))

    def testDefineScopesNotEmpty(self):
        self.resolver.begin_scope()
        self.resolver.define(Token('a', Literals.ID, None, None, None, None))
        self.assertTrue('a' in self.resolver.scopes[-1])
        self.assertTrue(self.resolver.scopes[-1]['a'] is True)

    def testDefineScopesEmpty(self):
        scopes_before = copy.deepcopy(self.resolver.scopes)
        self.resolver.define(Token('a', Literals.ID, None, None, None, None))
        self.assertTrue(len(scopes_before) == 0)
        self.assertTrue(len(self.resolver.scopes) == 0)
        self.assertEqual(self.resolver.scopes, scopes_before)

    def testVisitVariableExprGood(self):
        self.resolver.begin_scope()
        self.resolver.scopes[-1]['a'] = True
        node = fim_ast.Var(Token('a', Literals.ID, None, None, None, None))
        self.resolver.visit_Var(node)
        self.assertTrue(self.interpreter.locals[node] == 0,
                        f'locals[node] is {self.interpreter.locals[node]}')

    def testVisitVariableExprGoodBecauseEmpty(self):
        self.resolver.scopes = []
        fim_ast.Var(Token('a', Literals.ID, None, None, None, None))
        self.assertTrue(self.resolver.scopes == [])

    def testVisitVariableExprBadBecauseNotDefined(self):
        self.resolver.begin_scope()
        node = fim_ast.Var(Token('a', Literals.ID, None, None, None, 0))
        self.resolver.declare(Token('a', Literals.ID, None, None, None, 0))
        with self.assertRaises(ResolverException):
            self.resolver.visit_Var(node)

    def testResolveLocalLast0(self):
        self.resolver.begin_scope()
        self.resolver.scopes[-1]['a'] = True
        node = fim_ast.Var(Token('a', Literals.ID, None, None, None, None))
        self.resolver.resolve_local(node, node.token)
        self.assertTrue(self.interpreter.locals[node] == 0,
                        f'locals[node] is {self.interpreter.locals[node]}')

    def testResolveLocalLast3(self):
        for i in range(3):
            self.resolver.begin_scope()
        self.resolver.scopes[-1]['a'] = True
        node = fim_ast.Var(Token('a', Literals.ID, None, None, None, None))
        self.resolver.resolve_local(node, node.token)
        self.assertTrue(self.interpreter.locals[node] == 0,
                        f'locals[node] is {self.interpreter.locals[node]}')

    def testResolveLocal2(self):
        for i in range(3):
            self.resolver.begin_scope()
        self.resolver.scopes[0]['a'] = True
        node = fim_ast.Var(Token('a', Literals.ID, None, None, None, None))
        self.resolver.resolve_local(node, node.token)
        self.assertTrue(self.interpreter.locals[node] == 2,
                        f'locals[node] is {self.interpreter.locals[node]}')

    def testVisitAssign(self):
        self.resolver.begin_scope()
        self.resolver.visit_VariableDeclaration(fim_ast.VariableDeclaration(
            fim_ast.Var(Token('a', Literals.ID, None, None, None, None)),
            Token('is', Keywords.EQUAL, None, None, None, None),
            fim_ast.String(
                Token('"a"', Literals.STRING, None, None, None, None))))
        var_node = fim_ast.Var(Token('a', Literals.ID, None, None, None, None))
        assign_node = fim_ast.Assign(
            var_node,
            fim_ast.String(
                Token('"a"', Literals.STRING, None, None, None, None)))
        self.resolver.visit_Assign(assign_node)
        self.assertTrue(self.interpreter.locals[var_node] == 0,
                        f'locals[node] is {self.interpreter.locals[var_node]}')

    def testFunction(self):
        self.resolver.begin_scope()
        compound = fim_ast.Compound()
        compound.children = [fim_ast.NoOp()]
        self.resolver.visit_Function(fim_ast.Function(
            fim_ast.Var(Token('a', Literals.ID, None, None, None, None)),
            [],
            [], compound, False))
        self.assertTrue('a' in self.resolver.scopes[-1])
        self.assertTrue(self.resolver.scopes[-1]['a'] is True)

    def testReturnOutsideOfFunction(self):
        with self.assertRaises(ResolverException):
            self.resolver.visit_Return(fim_ast.Return(
                fim_ast.String(
                    Token('"a"', Literals.STRING, None, None, None, None))))

    def testVisitClass(self):
        self.resolver.begin_scope()
        body = fim_ast.Compound()
        body.children = [fim_ast.NoOp()]
        self.resolver.visit_Class(fim_ast.Class(
            Token('A', Literals.ID, None, None, None, None),
            fim_ast.Var(
                Token('Princess Celestia', Literals.ID, None, None, None,
                      None)),
            [],
            body,
            {},
            {},
            Token('Programmer Name', Literals.ID, None, None, None, None)))
        self.assertTrue('A' in self.resolver.scopes[-1])
        self.assertTrue(self.resolver.scopes[-1]['A'] is True)

    def testSuperclassIsTheSameAsClass(self):
        self.resolver.begin_scope()
        body = fim_ast.Compound()
        body.children = [fim_ast.NoOp()]
        with self.assertRaises(ResolverException):
            self.resolver.visit_Class(fim_ast.Class(
                Token('A', Literals.ID, None, None, None, None),
                fim_ast.Var(Token('A', Literals.ID, None, None, None, None)),
                [],
                body,
                [],
                [],
                Token('Programmer Name', Literals.ID, None, None, None, None)))


class TypeCheckerTests(Base):

    def assertConversion(self, string, type, value):
        token = Token(string, Literals.NUMBER, None, None, None, None)
        res_type, token = self.resolver.separate_type(token)
        self.assertTrue(res_type == type, token.value == value)

    def testConvertLiteralsOrNamesToTypes(self):
        self.assertConversion('the number 99', Literals.NUMBER, '99')
        self.assertConversion('the letter ‘T’.', Literals.CHAR, '‘T’')
        self.assertConversion('the word "adorable"', Literals.STRING,
                              '"adorable"')
        self.assertConversion('99', None, '99')
        self.assertConversion('the number', Literals.NUMBER, 'the number')

    def testVariableDeclaration(self):
        self.resolver.begin_scope()
        self.resolver.visit_VariableDeclaration(fim_ast.VariableDeclaration(
            fim_ast.Var(Token('a', Literals.ID, None, None, None, None)),
            Token('is', Keywords.EQUAL, None, None, None, None),
            fim_ast.Number(
                Token('the number 1', Literals.NUMBER, None, None, None,
                      None))))
        self.assertTrue(
            self.resolver.scopes_for_typechecking[-1]['a'] == Literals.NUMBER)

    def testVariableDeclaration2(self):
        self.resolver.begin_scope()
        self.resolver.visit_VariableDeclaration(fim_ast.VariableDeclaration(
            fim_ast.Var(Token('a', Literals.ID, None, None, None, None)),
            Token('is', Keywords.EQUAL, None, None, None, None),
            fim_ast.Number(
                Token('the number 1', Literals.NUMBER, None, None, None,
                      None))))
        self.resolver.visit_VariableDeclaration(fim_ast.VariableDeclaration(
            fim_ast.Var(Token('b', Literals.ID, None, None, None, None)),
            Token('is', Keywords.EQUAL, None, None, None, None),
            fim_ast.Number(
                Token('the number a', Literals.ID, None, None, None,
                      None))))
        self.assertTrue(
            self.resolver.scopes_for_typechecking[-1]['b'] == Literals.NUMBER)

    def testFunctionDeclaration3(self):
        self.resolver.begin_scope()
        self.resolver.visit_Function(fim_ast.Function(
            fim_ast.Var(Token('a', Literals.ID, None, None, None, None)),
            Literals.NUMBER,
            [],
            fim_ast.Compound(),
            False))
        self.resolver.visit_VariableDeclaration(fim_ast.VariableDeclaration(
            fim_ast.Var(Token('b', Literals.ID, None, None, None, None)),
            Token('is', Keywords.EQUAL, None, None, None, None),
            fim_ast.Number(
                Token('the number a', Literals.ID, None, None, None,
                      None))))
        self.assertTrue(
            self.resolver.scopes_for_typechecking[-1]['b'] == Literals.NUMBER)


if __name__ == '__main__':
    unittest.main()

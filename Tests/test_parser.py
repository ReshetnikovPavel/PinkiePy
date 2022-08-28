import unittest

import fim_ast
from fim_lexer import Lexer, Literals, Keywords, Token
from fim_parser import Parser


class Base(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser(self.lexer)

    def tearDown(self):
        pass


class ParserTests(Base):
    def testVariable(self):
        self.parser.lexer.tokens = [
            Token('a', Literals.ID, None, None, None, None)]
        self.parser.current_token = self.lexer.get_next_token()
        res = self.parser.variable()
        self.assertTrue(res.value == 'a')
        self.assertTrue(isinstance(res, fim_ast.Var))

    def testVariableIfItIsGetFromObject(self):
        self.parser.lexer.tokens = [
            Token('Applejack', Literals.ID, None, None, None, None),
            Token('`s', Keywords.ACCESS_FROM_OBJECT, None, None, None, None),
            Token('hat', Literals.ID, None, None, None, None)]
        self.parser.current_token = self.lexer.get_next_token()
        res = self.parser.call()
        self.assertTrue(isinstance(res, fim_ast.Get))
        self.assertTrue(res.name.value == 'hat')
        self.assertTrue(isinstance(res.object, fim_ast.Var))
        self.assertTrue(res.object.token.value == 'Applejack')


if __name__ == '__main__':
    unittest.main()
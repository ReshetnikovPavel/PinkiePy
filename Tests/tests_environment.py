import unittest
import fim_ast

from environment import Environment
from fim_lexer import Token, Literals


class Base(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass


class EnvironmentTests(Base):
    def testGetAt(self):
        ancestor = Environment()
        var = fim_ast.Var(Token('a', Literals.ID, None, None, None, None))
        ancestor.define(var.token.value, "Hello World!")
        env = ancestor
        for i in range(4):
            env = Environment(env)

        res = env.get_at(4, var.token.value)
        self.assertTrue(res == "Hello World!")

    def testAncestorNoAncestors(self):
        env = Environment()
        res = env.ancestor(0)
        self.assertTrue(env is res)

    def testAncestor(self):
        ancestor = Environment()
        env = ancestor
        for i in range(4):
            env = Environment(env)
        res = env.ancestor(4)
        self.assertTrue(res is ancestor)

    def testAssignAt(self):
        ancestor = Environment()
        var = fim_ast.Var(Token('a', Literals.ID, None, None, None, None))
        ancestor.define(var.token.value, "before")
        env = ancestor
        for i in range(4):
            env = Environment(env)

        env.assign_at(4, var.token, "after")
        self.assertTrue(ancestor._values[var.token.value] == "after")


if __name__ == '__main__':
    unittest.main()

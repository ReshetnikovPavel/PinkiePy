import unittest
import fim_ast

from fim_interpreter import Interpreter
from fim_lexer import Lexer, Token, Literals, Keywords
from fim_parser import Parser
from fim_resolver import Resolver
from csharp_translator import CSharpTranslator


class Base(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser(self.lexer)
        self.interpreter = Interpreter(self.parser)
        self.resolver = Resolver(self.interpreter)
        self.translator = CSharpTranslator(self.parser, self.resolver)

    def set_up_program(self, program):
        self.lexer.set_source(program)
        self.lexer.lex()
        self.parser.current_token = self.lexer.get_next_token()
        tree = self.parser.parse()
        #self.resolver.resolve(tree)

        return tree

    def tearDown(self):
        pass


class TestTranslator(Base):
    def assert_csharp_program_from_node(self, ast_node, expected):
        actual = self.translator.visit(ast_node)
        self.assertEqual(actual, expected)

    def assert_csharp_program_from_fim(self, fim_program, expected):
        tree = self.set_up_program(fim_program)
        self.translator.tree = tree
        actual = self.translator.translate()
        self.assertEqual(actual, expected,
                         f"Expected: {expected} \n Actual: {actual}")

    def test_visit_BinOp(self):
        token = Token('plus', Keywords.ADDITION, None, None, None, None)
        self.assert_csharp_program_from_node(
            fim_ast.BinOp(fim_ast.Number(Token('1', Literals.NUMBER, None,
                                               None, None, None)),
                          token,
                          fim_ast.Number(Token('2', Literals.NUMBER, None,
                                               None, None, None))),
            '(1d) + (2d)')

    def test_visit_UnaryOp(self):
        self.assert_csharp_program_from_fim(
            """
        I said not correct.""",
            'using System;\n'
            'Console.WriteLine(!(true));')


    def test_visit_Number(self):
        token = Token('1', Literals.NUMBER, None, None, None, None)
        self.assert_csharp_program_from_node(fim_ast.Number(token), '1d')

    def test_visit_String(self):
        token = Token('"Hello World"', Literals.STRING, None, None, None, None)
        self.assert_csharp_program_from_node(fim_ast.String(token),
                                             '"Hello World"')

    def test_visit_Char(self):
        token = Token("'a'", Literals.CHAR, None, None, None, None)
        self.assert_csharp_program_from_node(fim_ast.Char(token), "'a'")

    def test_visit_Bool_true(self):
        token = Token('correct', Literals.TRUE, None, None, None, None)
        self.assert_csharp_program_from_node(fim_ast.Bool(token), 'true')

    def test_visit_Bool_false(self):
        token = Token('incorrect', Literals.FALSE, None, None, None, None)
        self.assert_csharp_program_from_node(fim_ast.Bool(token), 'false')

    def test_visit_Null(self):
        token = Token('nothing', Literals.NULL, None, None, None, None)
        self.assert_csharp_program_from_node(fim_ast.Null(token), 'null')

    def test_visit_Compound(self):
        pass

    def test_visit_Root(self):
        pass

    def test_visit_If(self):
        self.assert_csharp_program_from_fim(
            'When correct:'
            'I said "Hello World!".'
            'Otherwise:'
            'I said "Goodbye World!".'
            'That‘s what I would do.',

            'using System;\n'
            'if (true)\n'
            '{\n'
            'Console.WriteLine("Hello World!");\n'
            '}\n'
            'else\n'
            '{\n'
            'Console.WriteLine("Goodbye World!");\n'
            '}\n;')

    def test_visit_While(self):
        self.assert_csharp_program_from_fim(
            """
            As long as true:
                I said "Hello World!".
            That's what I did.
            """,
            'using System;\n'
            'while (true)\n'
            '{\n'
            'Console.WriteLine("Hello World!");\n'
            '}\n;')

    def test_visit_DoWhile(self):
        self.assert_csharp_program_from_fim(
            """
        Here's what I did:
        I said "Hello World!".
        I did this as long as true.""",

            'using System;\n'
            'do\n'
            '{\n'
            'Console.WriteLine("Hello World!");\n'
            '}\n'
            'while (true);')

    def test_visit_For(self):
        self.assert_csharp_program_from_fim(
            """
            For every number i from 0 to 10:
                I said "Hello World!".
            That's what I did.
            """,
            'using System;\n'
            'for (double i = 0d; i <= 10d; i++)\n'
            '{\n'
            'Console.WriteLine("Hello World!");\n'
            '}\n;')

    def test_visit_ForIter(self):
        self.assert_csharp_program_from_fim(
            """
            Did you know that Berry Punch likes the phrase “Cheerwine”?
            For every character c in Berry Punch...
            I said c.
            That’s what I did.
            """,
            ('using System;\n'
 'var Berry_Punch = "the phrase “Cheerwine”";\n'
 'foreach (var c in Berry_Punch)\n'
 '{\n'
 'Console.WriteLine(c);\n'
 '}\n'
 ';'))

    def test_visit_StatementList(self):
        pass

    def test_visit_NoOp(self):
        self.assert_csharp_program_from_node(fim_ast.NoOp(), '')

    def test_visit_Assign(self):
        self.assert_csharp_program_from_fim(
            """
            Did you know that x is 0?
            x is now 1.
            """,
            'using System;\n'
            'var x = 0d;\n'
            'x = 1d;')

    def test_visit_VariableDeclaration(self):
        self.assert_csharp_program_from_node(
            fim_ast.VariableDeclaration(fim_ast.Var(Token('x', Literals.ID,
                                                          None, None, None,
                                                          None)),
                                        None,
                                        fim_ast.Number(Token('1',
                                                             Literals.NUMBER,
                                                             None, None,
                                                             None, None))),
            'var x = 1d')

    def test_visit_Var(self):
        self.assert_csharp_program_from_node(
            fim_ast.Var(
                Token("Applejack's hat", Literals.ID, None, None, None, None)),
            'Applejack_s_hat')

    def test_visit_FunctionCall(self):
        self.assert_csharp_program_from_fim(
            """
            I learned Function using number one:
            I said "Hello World!".
            That's all about Function.
            
            I remembered Function using 1.
            """,
            'using System;\n'
            'public static object Function(double one)\n'
            '{\n'
            'Console.WriteLine("Hello World!");\n'
            'return null;\n'
            '}\n;\n'
            ';\n'
            'Function(1d);')

    def test_visit_Return(self):
        self.assert_csharp_program_from_node(
            fim_ast.Return(fim_ast.Number(Token('1', Literals.NUMBER, None,
                                                None, None, None))),
            'return 1d')

    def test_visit_Increment(self):
        self.assert_csharp_program_from_node(
            fim_ast.Increment(fim_ast.Var(Token('x', Literals.ID, None,
                                                None, None, None))),
            '(x)++')

    def test_visit_Increment2(self):
        self.assert_csharp_program_from_node(
            fim_ast.Increment(fim_ast.Var(Token('x', Literals.ID, None,
                                                None, None, None)), 2),
            '(x) += 2')

    def test_visit_Decrement(self):
        self.assert_csharp_program_from_node(
            fim_ast.Decrement(fim_ast.Var(Token('x', Literals.ID, None,
                                                None, None, None))),
            '(x)--')

    def test_visit_Print(self):
        token = Token('"Hello World"', Literals.STRING, None, None, None, None)
        self.assert_csharp_program_from_node(
            fim_ast.Print(fim_ast.String(token)),
            'Console.WriteLine("Hello World")')

    def test_visit_Read(self):
        token = Token('x', Literals.ID, None, None, None, None)
        self.assert_csharp_program_from_node(
            fim_ast.Read(fim_ast.Var(token)),
            'x = Console.ReadLine()')

    def test_visit_FunctionObject(self):
        self.assert_csharp_program_from_fim(
            """
            I learned Function:
            I said "Hello World!".
            That's all about Function.
            """,
            'using System;\n'
            'public static object Function()\n'
            '{\n'
            'Console.WriteLine("Hello World!");\n'
            'return null;\n'
            '}\n;\n'
            ';')

    def test_visit_FunctionReturnType(self):
        self.assert_csharp_program_from_fim(
            """
            I learned Function to get number:
            Then you get 1!
            That's all about Function.
            """,
            'using System;\n'
            'public static double Function()\n'
            '{\n'
            'return 1d;\n'
            '}\n;\n'
            ';')

    def test_visit_Class(self):
        pass

    def test_visit_Interface(self):
        pass

    def test_visit_Get(self):
        pass

    def test_visit_Set(self):
        pass

    def test_visit_Switch(self):
        self.assert_csharp_program_from_fim(
        """
        Did you know that Pinkies Tail is the number 1?

    As long as Pinkies Tail had no more than 5...
        In regards to Pinkies Tail:
            On the 1st hoof...
                I said "That's impossible!".
            On the 2nd hoof...
                I said "There must be a scientific explanation".
            On the 3rd hoof...
                I said "There must be an explanation".
            On the 4th hoof...
                I said "Why does this happen?!".
            If all else fails...
                I said "She's just being Pinkie Pie.".
        That's what I did.

        Pinkies Tail got one more!
    That's what I did.
        """,
            ('using System;\n'
 'var Pinkies_Tail = the number 1d;\n'
 'while ((Pinkies_Tail) <= (5d))\n'
 '{\n'
 'switch (Pinkies_Tail)\n'
 '{\n'
 'case 1d:\n'
 '{\n'
 'Console.WriteLine("That\'s impossible!");\n'
 '}\n'
 'break;\n'
 'case 2d:\n'
 '{\n'
 'Console.WriteLine("There must be a scientific explanation");\n'
 '}\n'
 'break;\n'
 'case 3d:\n'
 '{\n'
 'Console.WriteLine("There must be an explanation");\n'
 '}\n'
 'break;\n'
 'case 4d:\n'
 '{\n'
 'Console.WriteLine("Why does this happen?!");\n'
 '}\n'
 'break;\n'
 'default:\n'
 '{\n'
 'Console.WriteLine("She\'s just being Pinkie Pie.");\n'
 '}\n'
 'break;\n'
 '};\n'
 '(Pinkies_Tail)++;\n'
 '}\n'
 ';')
        )

    def test_visit_Import(self):
        self.assert_csharp_program_from_node(
            fim_ast.Import(fim_ast.Var(Token('System', Literals.STRING,
                                                None, None, None, None))),
            'using System;')

    def test_visit_Array(self):
        pass

    def test_visit_ArrayElementAssignment(self):
        pass

import unittest
import unittest.mock

from fim_debugger import Debugger
from fim_lexer import Lexer
from fim_parser import Parser
from fim_resolver import Resolver


class Base(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser(self.lexer)
        self.debugger = Debugger(self.parser, '')
        self.resolver = Resolver(self.debugger)

    def set_up_program(self, program):
        self.lexer.set_source(program)
        self.lexer.lex()
        self.parser.current_token = self.lexer.get_next_token()
        self.parser.parse()
        self.debugger.lines = program.split('\n')

    def tearDown(self):
        pass


class DebuggerTests(Base):
    @unittest.mock.patch('builtins.input', return_value='0')
    def test_set_breakpoint(self, input):
        self.debugger.set_breakpoint()
        self.assertEqual(self.debugger.breakpoints, {0})

    def test_is_breakpoint_input_valid(self):
        self.set_up_program('Did you know that ten is 10?\n'
                            'Did you know that twelve is 2 plus ten?\n'
                            'I said twelve!')

        self.assertTrue(self.debugger._is_breakpoint_valid('0'))
        self.assertTrue(self.debugger._is_breakpoint_valid('1'))
        self.assertTrue(self.debugger._is_breakpoint_valid('2'))
        self.assertFalse(self.debugger._is_breakpoint_valid('3'))
        self.assertFalse(self.debugger._is_breakpoint_valid('-1'))

    @unittest.mock.patch('builtins.input', return_value='1')
    def test_remove_breakpoint(self, input):
        self.debugger.breakpoints = {0, 1, 2}
        self.debugger.remove_breakpoint()
        self.assertEqual(self.debugger.breakpoints, {0, 2})

    def test_should_stop(self):
        self.debugger.breakpoints = {0, 1, 2}
        self.debugger.current_line = 0
        self.assertFalse(self.debugger.should_stop(0))
        self.assertTrue(self.debugger.should_stop(1))
        self.assertTrue(self.debugger.should_stop(2))
        self.assertTrue(self.debugger.should_stop(3))
        self.debugger.command = 'c'
        self.assertFalse(self.debugger.should_stop(3))

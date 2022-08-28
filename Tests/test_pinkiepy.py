import sys
import unittest
import io
from pathlib import Path

import pinkiepy
import special_words


class Base(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def assert_printed(self, program_string, expected):
        self.old_stdout = sys.stdout  # Memorize the default stdout stream
        sys.stdout = self.buffer = io.StringIO()

        pinkiepy.interpret(program_string)
        self.assertTrue(
            expected in self.buffer.getvalue(),
            f'{self.buffer.getvalue()} does not contain {expected}')

        sys.stdout = self.old_stdout

    def assert_printed_path(self, path, expected):
        self.old_stdout = sys.stdout
        sys.stdout = self.buffer = io.StringIO()
        abs_path = Path(path).absolute()
        pinkiepy.interpret_file(abs_path)
        self.assertTrue(
            expected in self.buffer.getvalue(),
            f'{self.buffer.getvalue()} does not contain {expected}')
        sys.stdout = self.old_stdout


class PinkiePyTests(Base):
    def testOkProgram(self):
        self.assert_printed(
            'I said "Hello World"!',
            "Hello World\n"
        )

    def testParserException(self):
        self.assert_printed(
            'I said "Hello World',
            "FimParserException"
        )

    def testResolverException(self):
        self.assert_printed(
            'I said a.',
            "FimResolverException"
        )

    def testRuntimeException(self):
        self.assert_printed(
            'I said 1 plus "Hello".',
            "FimRuntimeException"
        )

    def testRecursionError(self):
        self.assert_printed(
            """I learned function using a:
                As long as true:
                    I remembered function using a.
                That's what I did.
            That's all about function.
            
            I said function using 1.""",
            "Recursion error"
        )

    def testInterpretFileOK(self):
        self.assert_printed_path('For Test.fim', "Hello World\n")

    def testInterpretFileNotFound(self):
        self.assert_printed_path('For Test2.fim', "File not found")


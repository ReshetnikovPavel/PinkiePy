import unittest
import lexer
import lexer_second_attempt


class Base(unittest.TestCase):
    def setUp(self):
        self.lex = lexer.lex

    def get_tokens(self, program):
        return list(self.lex(program))


def tokens_are(tokens, *tuples):
    for i in range(len(tokens)):
        if not(tuples[i][0] and tuples[i][1] in str(tokens[i])):
            return False
    return len(tokens) == len(tuples)


class TestComments(Base):
    def no_tokens(self, program):
        tokens = self.get_tokens(program)
        self.assertTrue(len(tokens) == 0, f"Should've been no tokens:"
                                          f"\n{list(tokens)}")

    def testSingleLineComment(self):
        self.no_tokens('P.S. I don’t know how well this will go')

    def testSingleLineComment_MultipleS(self):
        self.no_tokens('P.P.S. That said, I’m pretty excited!')

    def testSingleLine_AnotherSInsideCommentedString(self):
        self.no_tokens('P.S.You don’t need a space after the “S.”.')

    def testSingleLine_UnusedCode(self):
        self.no_tokens(
            'P.S.I said “something else”! <= old, unused code kept for reference')

    def testSingleLine_CodeAndComment(self):
        tokens = self.get_tokens(
            'I said “something”! P.S. replace “something” with the actual variable.')
        expr = tokens_are(tokens,
                          ('PRINT', 'I said'),
                          ('STRING', '“something”'),
                          ('PUNCTUATION', '!'))

        self.assertTrue(expr, "tokens are not right"
                              f"\n{list(tokens)}")

    def testBlock(self):
        self.no_tokens('(I can say anything I want in here!)')

    def testBlock_WithCode(self):
        tokens = self.get_tokens('I said “something”! (replace “something” with the actual variable)')
        expr = tokens_are(tokens,
                          ('PRINT', 'I said'),
                          ('STRING', '“something”'),
                          ('PUNCTUATION', '!'))
        self.assertTrue(expr, "tokens are not right"
                              f"\n{list(tokens)}")

    def testBlock_InsideCode(self):
        tokens = self.get_tokens('Dear Princess Celestia( and Princess Luna and Princess Cadence): Hey, Celly!')
        expr = tokens_are(tokens,
                          ('REPORT', 'Dear'),
                          ('NAME', 'Princess Celestia'),
                          ('PUNCTUATION', ':'),
                          ('NAME', 'Hey, Celly'),
                          ('PUNCTUATION', '!'))
        self.assertTrue(expr, "tokens are not right"
                              f"\n{list(tokens)}")

    def 


if __name__ == '__main__':
    unittest.main()

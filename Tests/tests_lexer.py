import unittest
import lexer
import lexer_second_attempt


class Base(unittest.TestCase):
    def setUp(self):
        self.lex = lexer.lex

    def get_tokens(self, program):
        return list(self.lex(program))

    def no_tokens(self, program):
        tokens = self.get_tokens(program)
        self.assertTrue(len(tokens) == 0, f"Should've been no tokens:"
                                          f"\n{list(tokens)}")


def tokens_are(tokens, *tuples):
    for i in range(len(tokens)):
        if not (tuples[i][0] in str(tokens[i]) and tuples[i][1] in str(
                tokens[i])):
            return False
    return len(tokens) == len(tuples)


class TestComments(Base):

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
        tokens = self.get_tokens(
            'I said “something”! (replace “something” with the actual variable)')
        expr = tokens_are(tokens,
                          ('PRINT', 'I said'),
                          ('STRING', '“something”'),
                          ('PUNCTUATION', '!'))
        self.assertTrue(expr, "tokens are not right"
                              f"\n{list(tokens)}")

    def testBlock_InsideCode(self):
        tokens = self.get_tokens(
            'Dear Princess Celestia( and Princess Luna and Princess Cadence): Hey, Celly!')
        expr = tokens_are(tokens,
                          ('REPORT', 'Dear'),
                          ('NAME', 'Princess Celestia'),
                          ('PUNCTUATION', ':'),
                          ('NAME', 'Hey, Celly'),
                          ('PUNCTUATION', '!'))
        self.assertTrue(expr, "tokens are not right"
                              f"\n{list(tokens)}")


class TestClasses(Base):
    def testClassDeclaration(self):
        tokens = self.get_tokens('Dear Princess Celestia: Letter One.')
        expr = tokens_are(tokens,
                          ('REPORT', 'Dear'),
                          ('NAME', 'Princess Celestia'),
                          ('PUNCTUATION', ':'),
                          ('NAME', 'Letter One'),
                          ('PUNCTUATION', '.'))
        self.assertTrue(expr, "tokens are not right"
                              f"\n{list(tokens)}")

    def testInheritsMultipleInterfaces(self):
        tokens = self.get_tokens(
            'Dear Princess Luna and Shining Armor and Cadence: An Update:')
        expr = tokens_are(tokens,
                          ('REPORT', 'Dear'),
                          ('NAME', 'Princess Luna'),
                          ('AND', 'and'),
                          ('NAME', 'Shining Armor'),
                          ('AND', 'and'),
                          ('NAME', 'Cadence'),
                          ('PUNCTUATION', ':'),
                          ('NAME', 'An Update'),
                          ('PUNCTUATION', ':'))
        self.assertTrue(expr, "tokens are not right"
                              f"\n{list(tokens)}")

    def testEnding(self):
        tokens = self.get_tokens('Your faithful student, Twilight Sparkle.')
        expr = tokens_are(tokens,
                          ('REPORT', 'Your faithful student'),
                          ('PUNCTUATION', ','),
                          ('NAME', 'Twilight Sparkle'),
                          ('PUNCTUATION', '.'))
        self.assertTrue(expr, "tokens are not right"
                              f"\n{list(tokens)}")

    def testInterfaceDeclaration(self):
        tokens = self.get_tokens('Princess Luna:')
        expr = tokens_are(tokens,
                          ('NAME', 'Princess Luna'),
                          ('Punctuation', ':'))
        self.assertTrue(expr, "tokens are not right"
                              f"\n{list(tokens)}")


class TestMethods(Base):
    def testDeclaration(self):
        tokens = self.get_tokens('I learned the importance of oral hygiene!')
        expr = tokens_are(tokens,
                          ('PARAGRAPH', 'I learned'),
                          ('NAME', 'the importance of oral hygiene'),
                          ('PUNCTUATION', '!'))
        self.assertTrue(expr, "tokens are not right"
                              f"\n{list(tokens)}")

    def testManeDeclaration(self):
        tokens = self.get_tokens('Today I learned how to say Hello World.')
        expr = tokens_are(tokens,
                          ('MANE_PARAGRAPH', 'Today I learned'),
                          ('NAME', 'how to say Hello World'),
                          ('PUNCTUATION', '.'))
        self.assertTrue(expr, "tokens are not right"
                              f"\n{list(tokens)}")

    def testDeclarationReturnValue(self):
        tokens = self.get_tokens('I learned how to do math with a number.')
        expr = tokens_are(tokens,
                          ('PARAGRAPH', 'I learned'),
                          ('NAME', 'how to do math'),
                          ('RETURNED_VARIABLE_TYPE_DEFINITION', 'with'),
                          ('NUMBER_64_TYPE', 'a number'),
                          ('PUNCTUATION', '.'))
        self.assertTrue(expr, "tokens are not right"
                              f"\n{list(tokens)}")

    def testDeclarationArguments(self):
        tokens = self.get_tokens(
            'I learned how to take the sum of a set of numbers with a number using the numbers X.')
        expr = tokens_are(tokens,
                          ('PARAGRAPH', 'I learned'),
                          ('NAME', 'how to take the sum of a set of numbers'),
                          ('RETURNED_VARIABLE_TYPE_DEFINITION', 'with'),
                          ('NUMBER_64_TYPE', 'a number'),
                          ('LISTING_PARAGRAPH_PARAMETERS', 'using'),
                          ('NUMBER_64_ARRAY_TYPE', 'the numbers'),
                          ('NAME', 'X'),
                          ('PUNCTUATION', '.'))
        self.assertTrue(expr, "tokens are not right"
                              f"\n{list(tokens)}")

    def testReturn(self):
        tokens = self.get_tokens('Then you get 99!')
        expr = tokens_are(tokens,
                          ('RETURN', 'Then you get'),
                          ('NUMBER_64_TYPE', '99'),
                          ('PUNCTUATION', '!'))
        self.assertTrue(expr, "tokens are not right"
                              f"\n{list(tokens)}")

    def testReturnVariable(self):
        tokens = self.get_tokens('Then you get the answer!')
        expr = tokens_are(tokens,
                          ('RETURN', 'Then you get'),
                          ('NAME', 'the answer'),
                          ('PUNCTUATION', '!'))
        self.assertTrue(expr, "tokens are not right"
                              f"\n{list(tokens)}")

    def testEnding(self):
        tokens = self.get_tokens('That’s all about how to do math!')
        expr = tokens_are(tokens,
                          ('PARAGRAPH', 'That’s all about'),
                          ('NAME', 'how to do math'),
                          ('PUNCTUATION', '!'))
        self.assertTrue(expr, "tokens are not right"
                              f"\n{list(tokens)}")

    def testCalling_WithAnother(self):
        tokens = self.get_tokens('Did you know that Spike was Spike’s age?')
        expr = tokens_are(tokens,
                          ('VAR', 'Did you know that'),
                          ('NAME', 'Spike'),
                          ('EQUAL', 'was'),
                          ('NAME', 'Spike’s age'),
                          ('PUNCTUATION', '?'))
        self.assertTrue(expr, "tokens are not right"
                              f"\n{list(tokens)}")

    def testCalling_Print(self):
        tokens = self.get_tokens('I said how to write Hello World!')
        expr = tokens_are(tokens,
                          ('PRINT', 'I said'),
                          ('NAME', 'how to write Hello World'),
                          ('PUNCTUATION', '!'))
        self.assertTrue(expr, "tokens are not right"
                              f"\n{list(tokens)}")

    def testCalling_Run(self):
        tokens = self.get_tokens('I remembered how to write Hello World.')
        expr = tokens_are(tokens,
                          ('RUN', 'I remembered'),
                          ('NAME', 'how to write Hello World'),
                          ('PUNCTUATION', '.'))
        self.assertTrue(expr, "tokens are not right"
                              f"\n{list(tokens)}")

    def testCalling_Run2(self):
        tokens = self.get_tokens('I would say some choice words.')
        expr = tokens_are(tokens,
                          ('RUN', 'I would'),
                          ('NAME', 'say some choice words'),
                          ('PUNCTUATION', '.'))
        self.assertTrue(expr, "tokens are not right"
                              f"\n{list(tokens)}")


class TestVariablesAndConstants(Base):
    def testCorrectNames(self):
        names = ['Applejack',
                 'Applejack’s hat',
                 'Team Fortress 2'
                 'Somepony’s true identity']
        tokens_list = [self.get_tokens(name) for name in names]
        for tokens, name in zip(tokens_list, names):
            expr = tokens_are(tokens, ('NAME', name))
            self.assertTrue(expr, "name is supposed to be correct"
                                  f"\nname:{name}"
                                  f"\ntokens:{list(tokens)}")

    def testIncorrectNames(self):
        names = ['“reality”',
                 '99 jugs of cider',
                 'true facts',
                 'My Dear Fluttershy',
                 'Something valuable I learned yesterday',
                 'the song I sang']
        tokens_list = [self.get_tokens(name) for name in names]
        for tokens, name in zip(tokens_list, names):
            expr = tokens_are(tokens, ('NAME', name))
            self.assertFalse(expr, "name is supposed to be incorrect"
                                   f"\nname:{name}"
                                   f"\ntokens:{list(tokens)}")


if __name__ == '__main__':
    unittest.main()

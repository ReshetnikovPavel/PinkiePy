import unittest
from lexer_second_attempt import Lexer


class Base(unittest.TestCase):
    def setUp(self):
        pass

    def get_tokens(self, program):
        lexer = Lexer(program)
        return list(lexer.lex())

    def assert_no_tokens(self, program):
        tokens = self.get_tokens(program)
        self.assertTrue(len(tokens) == 0, f"Should've been no tokens:"
                                          f"\n{list(tokens)}")

    def assert_tokens(self, program, *expected_tokens):
        tokens = self.get_tokens(program)
        self.assertTrue(tokens_are(tokens, expected_tokens),
                        f"tokens are not right\n{list(tokens)}")


def tokens_are(tokens, tuples):
    try:
        for i in range(len(tokens)):
            print(tuples[i][0] in str(tokens[i]), tuples[i][0], tokens[i])
            print(tuples[i][1] in str(tokens[i]), tuples[i][1], tokens[i])
            if not (tuples[i][0] in str(tokens[i]) and tuples[i][1] in str(
                    tokens[i])):
                return False
        print(len(tokens), len(tuples))
        return len(tokens) == len(tuples)
    except IndexError:
        return False


class TestComments(Base):

    def testSingleLineComment(self):
        self.assert_tokens(
            'P.S. I don’t know how well this will go',
            ('COMMENT', 'P.S. I don’t know how well this will go'))

    def testSingleLineComment_MultipleS(self):
        self.assert_tokens('P.P.S. That said, I’m pretty excited!',
                           ('COMMENT', 'P.P.S. That said, I’m pretty excited!'))

    def testSingleLine_AnotherSInsideCommentedString(self):
        self.assert_tokens(
            'P.S.You don’t need a space after the “S.”.',
            ('COMMENT', 'P.S.You don’t need a space after the “S.”.'))

    def testSingleLine_UnusedCode(self):
        self.assert_tokens(
            'P.S.I said “something else”! <= old, unused code kept for '
            'reference',
            ('COMMENT', 'P.S.I said “something else”! <= old, unused code '
                        'kept for reference'))

    def testSingleLine_CodeAndComment(self):
        self.assert_tokens(
            'I said “something”! P.S. replace “something” with the actual '
            'variable.',
            ('PRINT', 'I said'),
            ('STRING', '“something”'),
            ('PUNCTUATION', '!'),
            ('COMMENT', 'P.S. replace “something” with the actual variable.'))

    def testBlock(self):
        self.assert_tokens('(I can say anything I want in here!)',
                           ('COMMENT', '(I can say anything I want in here!)'))

    def testBlock_WithCode(self):
        self.assert_tokens(
            'I said “something”! '
            '(replace “something” with the actual variable)',
            ('PRINT', 'I said'),
            ('STRING', '“something”'),
            ('PUNCTUATION', '!'),
            ('COMMENT', '(replace “something” with the actual variable)'))

    def testBlock_InsideCode(self):
        self.assert_tokens(
            'Dear Princess Celestia( and Princess Luna and Princess Cadence): '
            'Hey, Celly!',
            ('REPORT', 'Dear'),
            ('NAME', 'Princess Celestia'),
            ('COMMENT', '( and Princess Luna and Princess Cadence)'),
            ('PUNCTUATION', ':'),
            ('NAME', 'Hey, Celly'),
            ('PUNCTUATION', '!'))


class TestClasses(Base):
    def testClassDeclaration(self):
        self.assert_tokens('Dear Princess Celestia: Letter One.',
                           ('REPORT', 'Dear'),
                           ('NAME', 'Princess Celestia'),
                           ('PUNCTUATION', ':'),
                           ('NAME', 'Letter One'),
                           ('PUNCTUATION', '.'))

    def testInheritsMultipleInterfaces(self):
        self.assert_tokens(
            'Dear Princess Luna and Shining Armor and Cadence: An Update:',
            ('REPORT', 'Dear'),
            ('NAME', 'Princess Luna'),
            ('AND', 'and'),
            ('NAME', 'Shining Armor'),
            ('AND', 'and'),
            ('NAME', 'Cadence'),
            ('PUNCTUATION', ':'),
            ('NAME', 'An Update'),
            ('PUNCTUATION', ':'))

    def testEnding(self):
        self.assert_tokens('Your faithful student, Twilight Sparkle.',
                           ('REPORT', 'Your faithful student'),

                           ('NAME', 'Twilight Sparkle'),
                           ('PUNCTUATION', '.'))

    def testInterfaceDeclaration(self):
        self.assert_tokens('Princess Luna:',
                           ('NAME', 'Princess Luna'),
                           ('PUNCTUATION', ':'))


class TestMethods(Base):
    def testDeclaration(self):
        self.assert_tokens('I learned the importance of oral hygiene!',
                           ('PARAGRAPH', 'I learned'),
                           ('NAME', 'the importance of oral hygiene'),
                           ('PUNCTUATION', '!'))

    def testManeDeclaration(self):
        self.assert_tokens('Today I learned how to say Hello World.',
                           ('MANE_PARAGRAPH', 'Today I learned'),
                           ('NAME', 'how to say Hello World'),
                           ('PUNCTUATION', '.'))

    def testDeclarationReturnValue(self):
        self.assert_tokens('I learned how to do math with a number.',
                           ('PARAGRAPH', 'I learned'),
                           ('NAME', 'how to do math'),
                           ('RETURNED_VARIABLE_TYPE_DEFINITION', 'with'),
                           ('NUMBER_TYPE', 'a number'),
                           ('PUNCTUATION', '.'))

    def testDeclarationArguments(self):
        self.assert_tokens(
            'I learned how to take the sum of a set of numbers with a number '
            'using the numbers X.',
            ('PARAGRAPH', 'I learned'),
            ('NAME', 'how to take the sum of a set of numbers'),
            ('RETURNED_VARIABLE_TYPE_DEFINITION', 'with'),
            ('NUMBER_64_TYPE', 'a number'),
            ('LISTING_PARAGRAPH_PARAMETERS', 'using'),
            ('NUMBER_64_ARRAY_TYPE', 'the numbers'),
            ('NAME', 'X'),
            ('PUNCTUATION', '.'))

    def testReturn(self):
        self.assert_tokens('Then you get 99!',
                           ('RETURN', 'Then you get'),
                           ('NUMBER', '99'),
                           ('PUNCTUATION', '!'))

    def testReturnVariable(self):
        self.assert_tokens('Then you get the answer!',
                           ('RETURN', 'Then you get'),
                           ('NAME', 'the answer'),
                           ('PUNCTUATION', '!'))

    def testEnding(self):
        self.assert_tokens('That’s all about how to do math!',
                           ('PARAGRAPH', 'That’s all about'),
                           ('NAME', 'how to do math'),
                           ('PUNCTUATION', '!'))

    def testCalling_WithAnother(self):
        self.assert_tokens('Did you know that Spike was Spike’s age?',
                           ('VAR', 'Did you know that'),
                           ('NAME', 'Spike'),
                           ('EQUAL', 'was'),
                           ('NAME', 'Spike’s age'),
                           ('PUNCTUATION', '?'))

    def testCalling_Print(self):
        self.assert_tokens('I said how to write Hello World!',
                           ('PRINT', 'I said'),
                           ('NAME', 'how to write Hello World'),
                           ('PUNCTUATION', '!'))

    def testCalling_Run(self):
        self.assert_tokens('I remembered how to write Hello World.',
                           ('RUN', 'I remembered'),
                           ('NAME', 'how to write Hello World'),
                           ('PUNCTUATION', '.'))

    def testCalling_Run2(self):
        self.assert_tokens('I would say some choice words.',
                           ('RUN', 'I would'),
                           ('NAME', 'say some choice words'),
                           ('PUNCTUATION', '.'))


class TestVariablesAndConstants(Base):
    def testCorrectNames(self):
        names = ['Applejack',
                 'Applejack’s hat',
                 'Team Fortress 2'
                 'Somepony’s true identity']
        tokens_list = [self.get_tokens(name) for name in names]
        for tokens, name in zip(tokens_list, names):
            expr = tokens_are(tokens, (('NAME', name),))
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
            expr = tokens_are(tokens, (('NAME', name),))
            self.assertFalse(expr, "name is supposed to be incorrect"
                                   f"\nname:{name}"
                                   f"\ntokens:{list(tokens)}")

    def testDataArrays(self):
        self.assert_tokens('Did you know that cake has many names?'
                           '\ncake 1 is “chocolate”.'
                           '\ncake 2 is “apple cinnamon”.'
                           '\ncake 3 is “fruit”.'
                           '\nI said cake 2.',
                           ('VAR', 'Did you know that'),
                           ('NAME', 'cake'),
                           ('VAR', 'has'),
                           ('STRING_ARRAY', 'many names'),
                           ('PUNCTUATION', '?'),
                           ('NAME', 'cake'),
                           ('NUMBER', '1'),
                           ('VAR', 'is'),
                            ('STRING', 'chocolate'),
                            ('PUNCTUATION', '.'),
                            ('NAME', 'cake'),
                            ('NUMBER', '2'),
                            ('VAR', 'is'),
                            ('STRING', 'apple cinnamon'),
                            ('PUNCTUATION', '.'),
                            ('NAME', 'cake'),
                            ('NUMBER', '3'),
                            ('VAR', 'is'),
                            ('STRING', 'fruit'),
                            ('PUNCTUATION', '.'),
                            ('PRINT', 'I said'),
                            ('NAME', 'cake'),
                            ('NUMBER', '2'),
                            ('PUNCTUATION', '.'))


    def testDataArrays2(self):
        self.assert_tokens('Did you know that cake has the names “chocolate” '
                           'and “apple cinnamon” and “fruit”?',
                           ('VAR', 'Did you know that'),
                           ('NAME', 'cake'),
                           ('VAR', 'has'),
                           ('STRING_ARRAY', 'the names'),
                           ('STRING', '“chocolate”'),
                           ('AND', 'and'),
                           ('STRING', '“apple cinnamon”'),
                           ('AND', 'and'),
                           ('STRING', '“fruit”'),
                           ('PUNCTUATION', '?'))

    def testDeclaration(self):
        self.assert_tokens(
            'Did you know that Applejack likes numbers?',
            ('VAR', 'Did you know that'),
            ('NAME', 'Applejack'),
            ('VAR', 'likes'),
            ('NUMBER_ARRAY_TYPE', 'numbers'),
            ('PUNCTUATION', '?'))

    def testDeclaration2(self):
        self.assert_tokens(
            'Did you know that Trixie has the name “Trixie Lulamoon”?',
            ('VAR', 'Did you know that'),
            ('NAME', 'Trixie'),
            ('VAR', 'has'),
            ('STRING_TYPE', 'the name'),
            ('STRING', '“Trixie Lulamoon”'),
            ('PUNCTUATION', '?'))

    def testDeclaration3(self):
        self.assert_tokens(
            'Did you know that Kyli Rouge likes the phrase “inventing an '
            'esoteric programming language based on MLP:FiM is fun”? ',
            ('VAR', 'Did you know that'),
            ('NAME', 'Kyli Rouge'),
            ('VAR', 'likes'),
            ('STRING_TYPE', 'the phrase'),
            ('STRING', '“inventing an esoteric programming language based on '
                       'MLP:FiM is fun”'),
            ('PUNCTUATION', '?'))


    def testDeclaration4(self):
        self.assert_tokens('Did you know that Spike’s age is the number 10?',
                           ('VAR', 'Did you know that'),
                           ('NAME', 'Spike’s age'),
                           ('EQUAL', 'is'),
                           ('NUMBER_TYPE', 'the number'),
                           ('NUMBER', '10'),
                           ('PUNCTUATION', '?'))

    def testDeclaration5(self):
        self.assert_tokens(
            'Did you know that Princess Luna is always the phrase “awesome”?',
            ('VAR', 'Did you know that'),
            ('NAME', 'Princess Luna'),
            ('VAR', 'is'),
            ('CONST', 'always'),
            ('STRING_TYPE', 'the phrase'),
            ('STRING', '“awesome”'),
            ('PUNCTUATION', '?'))


class TestLiterals(Base):
    def testNumbers(self):
        self.assert_tokens('1', ('NUMBER', '1'))

    def testNumbers2(self):
        self.assert_tokens('512', ('NUMBER', '512'))

    def testNumbers3(self):
        self.assert_tokens('-1', ('NUMBER', '-1'))

    def testNumbers4(self):
        self.assert_tokens('31.25', ('NUMBER', '31.25'))

    def testNumbers5(self):
        self.assert_tokens('the number 99.',
                           ('NUMBER_TYPE', 'the number'),
                           ('NUMBER', '99'),
                           ('PUNCTUATION', '.'))

    def testCharacters(self):
        self.assert_tokens("'a'", ('CHAR', "'a'"))

    def testCharacters2(self):
        self.assert_tokens("'A'", ('CHAR', "'A'"))

    def testCharacters3(self):
        self.assert_tokens("'6'", ('CHAR', "'6'"))

    def testCharacters4(self):
        self.assert_tokens('the letter ‘T’.',
                           ('CHAR_TYPE', 'the letter'),
                           ('CHAR', '‘T’'),
                           ('PUNCTUATION', '.'))

    def testStrings(self):
        self.assert_tokens('“Princess”', ('STRING', '“Princess”'))

    def testStrings2(self):
        self.assert_tokens('the word "adorable".',
                           ('STRING_TYPE', 'the word'),
                           ('STRING', '"adorable"'),
                           ('PUNCTUATION', '.'))

    def testStrings3(self):
        self.assert_tokens('“^_^"', ('STRING', '“^_^"'))

    def testBoolean(self):
        self.assert_tokens('yes', ('TRUE', 'yes'))

    def testBoolean2(self):
        self.assert_tokens('no', ('FALSE', 'no'))

    def testBoolean3(self):
        self.assert_tokens('incorrect', ('FALSE', 'incorrect'))


class TestOperators(Base):
    def testAddition(self):
        self.assert_tokens('I said add 2 and 3',
                           ('PRINT', 'I said'),
                           ('ADD', 'add'),
                           ('NUMBER', '2'),
                           ('ADD', 'and'),
                           ('NUMBER', '3'))

    def testAddition2(self):
        self.assert_tokens('Did you know that twelve is 2 plus ten?',
                           ('VAR', 'Did you know that'),
                           ('NAME', 'twelve'),
                           ('EQUAL', 'is'),
                           ('NUMBER', '2'),
                           ('ADD', 'plus'),
                           ('NAME', 'ten'),
                           ('PUNCTUATION', '?'))

    def testAddition3(self):
        self.assert_tokens('I wrote 8 and 7 plus 3 added to 19.',
                           ('PRINT', 'I wrote'),
                           ('NUMBER', '8'),
                           ('ADD', 'and'),
                           ('NUMBER', '7'),
                           ('ADD', 'plus'),
                           ('NUMBER', '3'),
                           ('ADD', 'added to'),
                           ('NUMBER', '19'),
                           ('PUNCTUATION', '.'))

    def testIncrement(self):
        self.assert_tokens('Spike got one more.',
                           ('NAME', 'Spike'),
                           ('INCREMENT', 'got one more'),
                           ('PUNCTUATION', '.'))

    def testSubtraction(self):
        self.assert_tokens('I said subtract 5 and 7',
                           ('PRINT', 'I said'),
                           ('SUBTRACT', 'subtract'),
                           ('NUMBER', '2'),
                           ('SUBTRACT', 'and'),
                           ('NUMBER', '3'))

    def testSubtraction2(self):
        self.assert_tokens(
            'Did you know that Spike’s age is Rarity’s age minus Applebloom’s '
            'Age?',
            ('VAR', 'Did you know that'),
            ('NAME', 'Spike’s age'),
            ('EQUAL', 'is'),
            ('NAME', 'Rarity’s age'),
            ('SUBTRACT', 'minus'),
            ('NAME', 'Applebloom’s Age'),
            ('PUNCTUATION', '?'))

    def testSubtraction3(self):
        self.assert_tokens('I wrote the difference between the number of '
                           'books in the Canterlot Archives and the number of '
                           'books in the Treebrary.',
                           ('PRINT', 'I wrote'),
                           ('SUBTRACT', 'the difference between'),
                           ('NAME',
                            'the number of books in the Canterlot Archives'),
                           ('SUBTRACT', 'and'),
                           ('NAME', 'the number of books in the Treebrary'),
                           ('PUNCTUATION', '.'))

    def testDecrement(self):
        self.assert_tokens('Applejack got one less.',
                           ('NAME', 'Applejack'),
                           ('DECREMENT', 'got one less'),
                           ('PUNCTUATION', '.'))

    def testMultiplication(self):
        self.assert_tokens('I said multiply 8 and 16!',
                           ('PRINT', 'I said'),
                           ('MULTIPLY', 'multiply'),
                           ('NUMBER', '8'),
                           ('MULTIPLY', 'and'),
                           ('NUMBER', '16'),
                           ('PUNCTUATION', '!'))

    def testMultiplication2(self):
        self.assert_tokens('Did you know that Junebug’s daily profits is '
                           'Junebug’s hourly wage times 8?',
                           ('VAR', 'Did you know that'),
                           ('NAME', 'Junebug’s daily profits'),
                           ('EQUAL', 'is'),
                           ('NAME', 'Junebug’s hourly wage'),
                           ('MULTIPLY', 'times'),
                           ('NUMBER', '8'),
                           ('PUNCTUATION', '?'))

    def testMultiplication3(self):
        self.assert_tokens('I wrote my favorite number times 100.',
                           ('PRINT', 'I wrote'),
                           ('NAME', 'my favorite number'),
                           ('MULTIPLY', 'times'),
                           ('NUMBER', '100'),
                           ('PUNCTUATION', '.'))

    def testDivision(self):
        self.assert_tokens('I said divide 8 and 2.',
                           ('PRINT', 'I said'),
                           ('DIVIDE', 'divide'),
                           ('NUMBER', '8'),
                           ('DIVIDE', 'and'),
                           ('NUMBER', '2'),
                           ('PUNCTUATION', '.'))

    def testDivision2(self):
        self.assert_tokens(
            'Did you know that Spike’s age is my age divided by 2?',
            ('VAR', 'Did you know that'),
            ('NAME', 'Spike’s age'),
            ('EQUAL', 'is'),
            ('NAME', 'my age'),
            ('DIVIDE', 'divided by'),
            ('NUMBER', '2'),
            ('PUNCTUATION', '?'))

    def testDivision3(self):
        self.assert_tokens('I wrote divide 2 by 9.',
                           ('PRINT', 'I wrote'),
                           ('DIVIDE', 'divide'),
                           ('NUMBER', '2'),
                           ('DIVIDE', 'by'),
                           ('NUMBER', '9'),
                           ('PUNCTUATION', '.'))

    def testVariableModifier(self):
        self.assert_tokens('Spike’s age is now 11!',
                           ('NAME', 'Spike’s age'),
                           ('VARIABLE_VALUE_ASSIGNMENT', 'is now'),
                           ('NUMBER', '11'),
                           ('PUNCTUATION', '!'))

    def testVariableModifier2(self):
        self.assert_tokens('Applejack now likes 99.',
                           ('NAME', 'Applejack'),
                           ('VARIABLE_VALUE_ASSIGNMENT', 'now likes'),
                           ('NUMBER', '99'),
                           ('PUNCTUATION', '.'))

    def testVariableModifier3(self):
        self.assert_tokens(
            'the number of books in Twilight’s library becomes 1000.',
            ('NAME', 'the number of books in Twilight’s library'),
            ('VARIABLE_VALUE_ASSIGNMENT', 'becomes'),
            ('NUMBER', '1000'),
            ('PUNCTUATION', '.'))

    def testOutput(self):
        self.assert_tokens('I said “Hello World”!',
                           ('PRINT', 'I said'),
                           ('STRING', 'Hello World'),
                           ('PUNCTUATION', '!'))

    def testOutput2(self):
        self.assert_tokens('I wrote 99.',
                           ('PRINT', 'I wrote'),
                           ('NUMBER', '99'),
                           ('PUNCTUATION', '.'))

    def testOutput3(self):
        self.assert_tokens('I sang Winter Wrap-Up!',
                           ('PRINT', 'I sang'),
                           ('STRING', 'Winter Wrap-Up'),
                           ('PUNCTUATION', '!'))

    def testOutput4(self):
        self.assert_tokens('I said “Hello”! I said “World”.',
                           ('PRINT', 'I said'),
                           ('STRING', 'Hello'),
                           ('PUNCTUATION', '!'),
                           ('PRINT', 'I said'),
                           ('STRING', 'World'),
                           ('PUNCTUATION', '.'))

    def testInput(self):
        self.assert_tokens('I heard Applejack’s speech.',
                           ('READ', 'I heard'),
                           ('NAME', 'Applejack’s speech'),
                           ('PUNCTUATION', '.'))

    def testInput2(self):
        self.assert_tokens('I read the scroll!',
                           ('READ', 'I read'),
                           ('NAME', 'the scroll'),
                           ('PUNCTUATION', '!'))

    def testInput3(self):
        self.assert_tokens('I asked the first number.',
                           ('READ', 'I asked'),
                           ('NAME', 'the first number'),
                           ('PUNCTUATION', '.'))

    def testPrompt(self):
        self.assert_tokens('I asked Spike “How many gems are left?”.',
                           ('READ', 'I asked'),
                           ('NAME', 'Spike'),
                           ('STRING', 'How many gems are left?'),
                           ('PUNCTUATION', '.'))

    def testEqual(self):
        self.assert_tokens('nine is 9',
                           ('NAME', 'nine'),
                           ('EQUAL', 'is'),
                           ('NUMBER', '9'))

    def testEqual2(self):
        self.assert_tokens('Spike’s age was 10',
                           ('NAME', 'Spike’s age'),
                           ('EQUAL', 'was'),
                           ('NUMBER', '10'))

    def testEqual3(self):
        self.assert_tokens('Junebug’s profit was Rose’s profit',
                           ('NAME', 'Junebug’s profit'),
                           ('EQUAL', 'was'),
                           ('NAME', 'Rose’s profit'))

    def testNotEqual(self):
        self.assert_tokens('Celestia’s age is not 10',
                           ('NAME', 'Celestia’s age'),
                           ('NOT_EQUAL', 'is not'),
                           ('NUMBER', '10'))

    def testNotEqual2(self):
        self.assert_tokens('the number of cupcakes isn’t 0',
                           ('NAME', 'the number of cupcakes'),
                           ('NOT_EQUAL', 'isn’t'),
                           ('NUMBER', '0'))

    def testNotEqual3(self):
        self.assert_tokens('Trixie’s name wasn’t “Luna”',
                           ('NAME', 'Trixie’s name'),
                           ('NOT_EQUAL', 'wasn’t'),
                           ('STRING', 'Luna'))

    def testLessThan(self):
        self.assert_tokens(
            'the coolness of Rainbow Dash’s dress was less than 0.83',
            ('NAME', 'the coolness of Rainbow Dash’s dress'),
            ('LESS_THAN', 'was less than'),
            ('NUMBER', '0.83'))

    def testLessThan2(self):
        self.assert_tokens('the number of cupcakes is less than satisfactory',
                           ('NAME', 'the number of cupcakes'),
                           ('LESS_THAN', 'is less than'),
                           ('NAME', 'satisfactory'))

    def testLessThan3(self):
        self.assert_tokens('“Apple” is less than “Nothing”',
                           ('STRING', 'Apple'),
                           ('LESS_THAN', 'is less than'),
                           ('STRING', 'Nothing'))

    def testLessThanOrEqual(self):
        self.assert_tokens(
            'the number of flowers in Junebug’s garden isn’t more than 50',
            ('NAME', 'the number of flowers in Junebug’s garden'),
            ('LESS_THAN_OR_EQUAL', 'isn’t more than'),
            ('NUMBER', '50'))

    def testLessThanOrEqual2(self):
        self.assert_tokens(
            '10 is not greater than the number jugs of cider on the wall',
            ('NUMBER', '10'),
            ('LESS_THAN_OR_EQUAL', 'is not greater than'),
            ('NAME', 'the number jugs of cider on the wall'))

    def testGreaterThan(self):
        self.assert_tokens(
            'Did you know that truth is the argument anything Trixie can do '
            'is greater than anything you can do?',
            ('VAR', 'Did you know that'),
            ('NAME', 'truth'),
            ('BOOLEAN_TYPE', 'the argument'),
            ('NAME', 'anything Trixie can do'),
            ('GREATER_THAN', 'is greater than'),
            ('NAME', 'anything you can do'),
            ('PUNCTUATION', '?'))

    def testGreaterThanIf(self):
        self.assert_tokens(
            'If Spike’s crush on Rarity is more than Scootaloo’s crush on '
            'Rainbow Dash then: I said “It’s Tuesday”.',
            ('IF', 'If'),
            ('NAME', 'Spike’s crush on Rarity'),
            ('GREATER_THAN', 'is more than'),
            ('NAME', 'Scootaloo’s crush on Rainbow Dash'),
            ('IF', 'then'),
            ('PUNCTUATION', ':'),
            ('PRINT', 'I said'),
            ('STRING', 'It’s Tuesday'),
            ('PUNCTUATION', '.'))

    def testGreaterThanOrEqual(self):
        self.assert_tokens(
            'If Celestia’s greatness is no less than Luna’s greatness then: I '
            'would praise Luna some more.',
            ('IF', 'If'),
            ('NAME', 'Celestia’s greatness'),
            ('LESS_THAN_OR_EQUAL', 'is no less than'),
            ('NAME', 'Luna’s greatness'),
            ('IF', 'then'),
            ('PUNCTUATION', ':'),
            ('RUN', 'I would'),
            ('NAME', 'praise Luna some more'),
            ('PUNCTUATION', '.'))

    def testGreaterThanOrEqual2(self):
        self.assert_tokens(
            'Chrysalis’ greatness isn’t less than Twilight Sparkle’s greatness',
            ('NAME', 'Chrysalis’ greatness'),
            ('LESS_THAN_OR_EQUAL', 'isn’t less than'),
            ('NAME', 'Twilight Sparkle’s greatness'))

    def testAnd(self):
        self.assert_tokens(
            'Did you know that whether I went outside is the argument the sky '
            'is clear and Pinkie’s tail is still?',
            ('VAR', 'Did you know that'),
            ('NAME', 'whether I went outside'),
            ('BOOLEAN_TYPE', 'the argument'),
            ('NAME', 'the sky is clear'),
            ('AND', 'and'),
            ('NAME', 'Pinkie’s tail is still'),
            ('PUNCTUATION', '?'))

    def testAnd2(self):
        self.assert_tokens(
            'If I have no pants and I must scream then: I would scream '
            'without pants.',
            ('IF', 'If'),
            ('NAME', 'I have no pants'),
            ('AND', 'and'),
            ('NAME', 'I must scream'),
            ('IF', 'then'),
            ('PUNCTUATION', ':'),
            ('RUN', 'I would'),
            ('NAME', 'scream without pants'),
            ('PUNCTUATION', '.'))

    def testNot(self):
        self.assert_tokens(
            'As long as it’s not the case that Applejack has 5 (apples), '
            'I said “Keep going!”.',
            ('WHILE', 'As long as'),
            ('NOT', 'it’s not the case that'),
            ('NAME', 'Applejack'),
            ('NAME', 'has'),
            ('NUMBER', '5'),

            ('PRINT', 'I said'),
            ('STRING', 'Keep going!'),
            ('PUNCTUATION', '.'))


class TestBranchingStatements(Base):
    def testIf(self):
        self.assert_tokens('If Spike was 10 then:',
                           ('IF', 'If'),
                           ('NAME', 'Spike'),
                           ('EQUAL', 'was'),
                           ('NUMBER', '10'),
                           ('IF', 'then'),
                           ('PUNCTUATION', ':'))

    def testIf2(self):
        self.assert_tokens('When 10 was not the number:',
                           ('IF', 'When'),
                           ('NUMBER', '10'),
                           ('NOT_EQUAL', 'was not'),
                           ('NAME', 'the number'),
                           ('PUNCTUATION', ':'))

    def testSwitch(self):
        self.assert_tokens('In regards to Pinkie’s Tail:'
                           '\nOn the 1st hoof...'
                           '\nI said “That’s impossible!”.'
                           '\nOn the 2nd hoof...'
                           '\nI said “There must be a scientific explanation”.'
                           '\nOn the 3rd hoof...'
                           '\nI said “There must be an explanation”.'
                           '\nOn the 4th hoof...'
                           '\nI said “Why does this happen?!”.'
                           '\nI would flail.'
                           '\nIf all else fails...'
                           '\nI said “She’s just being Pinkie Pie.”.'
                           '\nThat’s what I did.',
                           ('SWITCH', 'In regards to'),
                           ('NAME', 'Pinkie’s Tail'),
                           ('PUNCTUATION', ':'),
                           ('CASE', 'On the'),
                           ('NUMBER', '1'),
                           ('CASE', 'st hoof'),
                           ('PUNCTUATION', '...'),
                           ('PRINT', 'I said'),
                           ('STRING', 'That’s impossible!'),
                           ('CASE', 'On the'),
                           ('NUMBER', '2'),
                           ('CASE', 'nd hoof'),
                           ('PUNCTUATION', '...'),
                           ('PRINT', 'I said'),
                           ('STRING', 'There must be a scientific explanation'),
                           ('CASE', 'On the'),
                           ('NUMBER', '3'),
                           ('CASE', 'rd hoof'),
                           ('PUNCTUATION', '...'),
                           ('PRINT', 'I said'),
                           ('STRING', 'There must be an explanation'),
                           ('CASE', 'On the'),
                           ('NUMBER', '4'),
                           ('CASE', 'th hoof'),
                           ('PUNCTUATION', '...'),
                           ('PRINT', 'I said'),
                           ('STRING', 'Why does this happen?!'),
                           ('RUN', 'I would'),
                           ('NAME', 'flail'),
                           ('DEFAULT', 'If all else fails'),
                           ('PUNCTUATION', '...'),
                           ('PRINT', 'I said'),
                           ('STRING', 'She’s just being Pinkie Pie.'),
                           ('PUNCTUATION', '.'),
                           ('RUN', 'That’s what I did.'))

    def testFor(self):
        self.assert_tokens('For every number x from 1 to 100,'
                           '\nI said x!'
                           '\nThat’s what I did.',
                           ('FOR', 'For every'),
                           ('NUMBER_TYPE', 'number'),
                           ('NAME', 'x'),
                           ('ITER', 'from'),
                           ('NUMBER', '1'),
                           ('ITER', 'to'),
                           ('NUMBER', '100'),
                           ('PRINT', 'I said'),
                           ('NAME', 'x'),
                           ('PUNCTUATION', '!'),
                           ('FOR', 'That’s what I did'),
                           ('PUNCTUATION', '.'))

    def testFor2(self):
        self.assert_tokens(
            'Did you know that Berry Punch likes the phrase “Cheerwine”?'
            '\nFor every character c in Berry Punch...'
            '\nI said c.'
            '\nThat’s what I did.',
            ('VAR', 'Did you know that'),
            ('NAME', 'Berry Punch'),
            ('VARIABLE_VALUE_ASSIGNMENT', 'likes'),
            ('STRING_TYPE', 'the phrase'),
            ('STRING', '“Cheerwine”'),
            ('PUNCTUATION', '?'),
            ('FOR', 'For every'),
            ('CHAR_TYPE', 'character'),
            ('NAME', 'c'),
            ('IN', 'in'),
            ('NAME', 'Berry Punch'),
            ('PUNCTUATION', '...'),
            ('PRINT', 'I said'),
            ('NAME', 'c'),
            ('PUNCTUATION', '.'),
            ('FOR', 'That’s what I did'),
            ('PUNCTUATION', '.'))


class TestPrograms(Base):
    def testHelloWorld(self):
        self.assert_tokens('\nDear Princess Celestia: Hello World!'
                           '\n'
                           '\nToday I learned how to say Hello World!'
                           '\nI said “Hello World”!'
                           '\nThat’s all about how to say Hello World!'
                           '\n'
                           '\nYour faithful student, Kyli Rouge.',
                           ('REPORT', 'Dear'),
                           ('NAME', 'Princess Celestia'),
                           ('PUNCTUATION', ':'),
                           ('NAME', 'Hello World'),
                           ('PUNCTUATION', '!'),
                           ('MANE_PARAGRAPH', 'Today I learned'),
                           ('NAME', 'how to say Hello World'),
                           ('PUNCTUATION', '!'),
                           ('PRINT', 'I said'),
                           ('STRING', 'Hello World'),
                           ('PUNCTUATION', '!'),
                           ('PARAGRAPH', 'That’s all about'),
                           ('NAME', 'how to say Hello World'),
                           ('PUNCTUATION', '!'),
                           ('REPORT', 'Your faithful student,'),
                           ('NAME', 'Kyli Rouge'),
                           ('PUNCTUATION', '.'))


if __name__ == '__main__':
    unittest.main()

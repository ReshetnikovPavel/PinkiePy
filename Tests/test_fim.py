import unittest
import sys
import io
from fim_lexer import Lexer
from fim_parser import Parser
from fim_interpreter import Interpreter
from fim_resolver import Resolver


def interpret(program):
    lexer = Lexer(program)
    lexer.lex()
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    tree = parser.parse()
    resolver = Resolver(interpreter)
    resolver.resolve(tree)
    interpreter.interpret(tree)


class Base(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def assert_printed(self, program, expected):
        self.old_stdout = sys.stdout  # Memorize the default stdout stream
        sys.stdout = self.buffer = io.StringIO()

        interpret(program)
        self.assertEqual(self.buffer.getvalue(), expected)

        sys.stdout = self.old_stdout


drinking_song = """
Dear Princess Celestia: Cider Jugs.

Today I learned Applejack's Drinking Song.
Did you know that Applejack likes the number 99?
(Applejack likes a lot of things...)
I remembered how to sing the drinking song using Applejack.
That's all about Applejack's Drinking Song!

I learned how to sing the drinking song using ciders.
As long as ciders were more than 1.
I sang ciders" jugs of cider on the wall, "ciders" jugs of cider,".
There was one less ciders.
When ciders had more than 1,
 I sang "Take one down and pass it around, "ciders
 " jugs of cider on the wall."!
Otherwise,
 I sang "Take one down and pass it around, 1 jug of cider on the wall."!
That's what I would do, That's what I did.

I sang "1 jug of cider on the wall, 1 jug of cider.
Take it down and pass it around, no more jugs of cider on the wall.

No more jugs of cider on the wall, no more jugs of cider.
Go to the celler, get some more, 99 jugs of cider on the wall.".
That's all about how to sing the drinking song!

Your faithful student, Twilight Sparkle.
"""


class TestOperators(Base):
    def test_addition(self):
        self.assert_printed('I said add 2 and 3.', '5\n')

    def testAddition2(self):
        self.assert_printed('Did you know that ten is 10? '
                            'Did you know that twelve is 2 plus ten?'
                            'I said twelve!', '12\n')

    def testAddition3(self):
        self.assert_printed('I wrote 8 and 7 plus 3 added to 19.', '37\n')

    def testIncrement(self):
        pass

    def testSubtraction(self):
        self.assert_printed('I said subtract 5 and 7.', '-2\n')

    def testMultiplication(self):
        self.assert_printed('I said multiply 8 and 16!', '128\n')

    def testDivision(self):
        self.assert_printed('I said divide 8 and 2.', '4\n')

    def testDivision3(self):
        self.assert_printed('I wrote divide 2 by 9.', f'{2 / 9}\n')

    def testOutput(self):
        self.assert_printed('I said “Hello World”!', 'Hello World\n')

    def testOutput2(self):
        self.assert_printed('I wrote 99.', '99\n')

    def testOutput4(self):
        self.assert_printed('I said “Hello”! I said “World”.',
                            'Hello\nWorld\n')

    def testXor(self):
        self.assert_printed('I said either false or false.', 'false\n')
        self.assert_printed('I said either false or true.', 'true\n')
        self.assert_printed('I said either true or false.', 'true\n')
        self.assert_printed('I said either true or true.', 'false\n')


class TestPrograms(Base):
    def testMath(self):
        self.assert_printed("""
Dear Princess Celestia: Math!

    Did you know that Pi is number 3.14159265359?
    Did you know that e is number 2.71828182846?

   I learned maximum to get a number using first number and second number!
       Did you know that maximum was nothing?
       If first number is greater than second number,
        maximum becomes first number.
       Otherwise, maximum becomes second number.
       That's what I would do.
       Then you get maximum!

   That’s all about maximum!

    I learned minimum to get a number using first number and second number!
        Did you know that minimum was nothing?
        If first number is less than second number,
         minimum becomes first number.
        Otherwise, minimum becomes second number.
        That's what I would do.
        Then you get minimum!

    That’s all about minimum!

    I learned absolute value to get a number using the number!
        Did you know that absolute value was nothing?
        If the number is less than 0,
         absolute value becomes the number multiplied with -1.
        Otherwise, absolute value becomes the number.
        That's what I would do.
        Then you get absolute value!
    That's all about absolute value!

    I learned sign to get a number using the number!
        Did you know that a sign was nothing?
        If the number is less than 0, a sign becomes -1.
        Otherwise, a sign becomes 1.
        That's what I would do.
        Then you get a sign!
    That's all about sign!

Your faithful student, Kyli Rouge.

I said Math`s minimum using 42 and 69!
I said Math`s maximum using 42 and 69!
I said Math`s absolute value using -42!
I said Math`s absolute value using 42!
I said Math`s sign using -42!
I said Math`s sign using 42!
I said Math`s Pi!
I said Math`s e!
""",
                            '42\n69\n42\n42\n-1\n1\n3.14159265359\n2'
                            '.71828182846\n')

    def testHelloWorld(self):
        self.assert_printed("""Dear Princess Celestia: Hello World!

Today I learned how to say Hello World!
I said “Hello World”!
That’s all about how to say Hello World!

Your faithful student, Kyli Rouge.""", 'Hello World\n')

    def testHelloWorldShort(self):
        self.assert_printed('I said "Hello World"!', 'Hello World\n')

    def testSwitch(self):
        self.assert_printed("""I learned flail.
    I said "Flail!".
That's all about flail.

Did you know that Pinkie’s Tail is 4?

In regards to Pinkie’s Tail:
On the 1st hoof...
I said “That’s impossible!”.
On the 2nd hoof...
I said “There must be a scientific explanation”.
On the 3rd hoof...
I said “There must be an explanation”.
On the 4th hoof...
I said “Why does this happen?!”.
I would flail.
If all else fails...
I said “She’s just being Pinkie Pie.”.
That’s what I did.""", 'Why does this happen?!\nFlail!\n')
        self.assert_printed("""I learned flail.
    I said "Flail!".
That's all about flail.

Did you know that Pinkie’s Tail is 5?

In regards to Pinkie’s Tail:
On the 1st hoof...
I said “That’s impossible!”.
On the 2nd hoof...
I said “There must be a scientific explanation”.
On the 3rd hoof...
I said “There must be an explanation”.
On the 4th hoof...
I said “Why does this happen?!”.
I would flail.
If all else fails...
I said “She’s just being Pinkie Pie.”.
That’s what I did.""", 'She’s just being Pinkie Pie.\n')

    def testInterface1(self):
        self.assert_printed("""Princess Luna:

I learned how to fly.
I learned how to do magic.
I learned how to raise the moon.

Your faithful student, Kyli Rouge.

Dear Princess Celestia and Princess Luna: Interface Name!

Today I learned how to do a lot of things!
    I remembered how to fly,
     I remembered how to do magic, I remembered how to raise the moon!
That's all about how to do a lot of things.

I learned how to fly.
    I said "I can fly now".
That's all about how to fly.

I learned how to do magic.
    I said "Shazam"!
That's all about how to do magic.

I learned how to raise the moon.
    I said "cnreicofnouqefcnf".
That's all about how to raise the moon.

Your faithful student, Pavel Reshetnikov.""",
                            'I can fly now\nShazam\ncnreicofnouqefcnf\n')

    def testInterface2(self):
        self.assert_printed("""
        Dear Princess Celestia and Princess Luna: Interface Name!

        Today I learned how to do a lot of things!
            I remembered how to fly,
             I remembered how to do magic, I remembered how to raise the moon!
        That's all about how to do a lot of things.

        I learned how to fly.
            I said "I can fly now".
        That's all about how to fly.

        I learned how to do magic.
            I said "Shazam"!
        That's all about how to do magic.

        I learned how to raise the moon.
            I said "a".
        That's all about how to raise the moon.

        Your faithful student, Pavel Reshetnikov.

        Princess Luna:

        I learned how to fly.
        I learned how to do magic.
        I learned how to raise the moon.

        Your faithful student, Kyli Rouge.""",
                            'I can fly now\nShazam\na\n')

    def testInterface3(self):
        self.assert_printed("""
        Interface 1:
        I learned method 1!
        Your faithful student, Pavel Reshetnikov.

        Interface 2:
        I learned method 2!
        Your faithful student, Pavel Reshetnikov.

        Dear Princess Celestia and Interface 1 and Interface 2: Implementation!
        Today I learned Main!
            I would method 1!
            I would method 2!
        That's all about Main.

        I learned method 1!
            I said "method 1"!
        That's all about method 1!

         I learned method 2!
            I said "method 2"!
        That's all about method 2!

        Your faithful student, Pavel Reshetnikov.""", 'method 1\nmethod 2\n')

    def testInterface4(self):
        with self.assertRaises(Exception):
            self.assert_printed("""Princess Luna:

I learned how to fly.
I learned how to do magic.
I learned how to raise the moon.

Your faithful student, Kyli Rouge.

Dear Princess Celestia and Princess Luna: Interface Name!

Today I learned how to do a lot of things!
    I remembered how to fly, I remembered how to raise the moon!
That's all about how to do a lot of things.

I learned how to fly.
    I said "I can fly now".
That's all about how to fly.

I learned how to raise the moon.
    I said "cnreicofnouqefcnf".
That's all about how to raise the moon.

Your faithful student, Pavel Reshetnikov.""",
                                'I can fly now\ncnreicofnouqefcnf\n')

    def testArrays(self):
        self.assert_printed("""
Dear Princess Celestia: Arrays!


Today I learned how to make arrays!

    (Without initialized values)
    Did you know that banana is the word "Banana Cake"?
    Did you know that carrot is the number 4? (Pointer - 4)

    Did you know that cake has many words?
    cake 1 is the word "Mango Cake". (Index 1)
    cake 2 is "Strawberry Cake". (Index 2)
    cake 3 is banana. (Index 3)
    cake`s carrot is "Carrot Cake". (Index 4)

    carrot got one less.

    I said cake`s carrot. (Index 3)

    (With initialized values)
    Did you know that Apples has words "Gala" and
     "Red Delicious" and "Mcintosh" and "Honeycrisp"?

    I said Apples 1.

That's all about how to make arrays.


Your faithful student, Vinyla Jaezmien Gael.""", 'Banana Cake\nMcintosh\n')

    def testTheSumOfEverythingFromTo(self):
        self.assert_printed("""
        Dear Princess Celestia: Numbers are fun!
         (Start the class, naming it and its superclass)

Today I learned some math.
 (Start the mane method. This is the first part that runs)
I wrote the sum of everything from 1 to 100.
 (Run the “the sum of all the numbers from 1 to 100” method
  and print the return value)
That’s all about some math. (and now the program has finished running)

I learned the sum of everything from 1 to 100 to get a number.
 (start of a new method)
Did you know that the sum was the number 0?
 (Declare a new variable named “the sum” to be a number,
  and initialize it to 0)
Did you know that the current count was the number 0?
 (Declare a new variable named
  “the current count” to be a number, and initialize it to 0)

As long as the current count was no more than 100:
 (Start a conditional statement that loops
 while “the current count” is less than or equal to 100)
I would add the current count to the sum.
 (Increment “the sum” by the value held in “the current count”)
the current count got one more. (Increment “the current count” by 1)
That’s what I did. (End of the loop)

Then you get the sum! (Return the value held in “the sum”)
That’s all about the sum of everything from 1 to 100. (End of the method)

Your faithful student, Kyli Rouge. (End the class and sign your name)""",
                            '5050\n')

    def testFor(self):
        self.assert_printed("""
For every number x from 1 to 5,
I said x!
That’s what I did.""", '1\n2\n3\n4\n5\n')

    def testForIter(self):
        self.assert_printed("""
Did you know that Berry Punch likes the phrase “Cheerwine”?
For every character c in Berry Punch...
I said c.
That’s what I did.""", 'C\nh\ne\ne\nr\nw\ni\nn\ne\n')

    def testForIter2(self):
        self.assert_printed("""Did you know that A likes many numbers?
A 0 is 0, A 1 is 42, A 2 is 69.
For every number c in A...
I said c.
That’s what I did.""", '0\n42\n69\n')

    def testForIter3(self):
        with self.assertRaises(Exception):
            self.assert_printed("""Did you know that A likes many numbers?
A 0 is 0, A 1 is 42, A 2 is 69.
For every character c in A...
I said c.
That’s what I did.""", '0\n42\n69\n')

    def testNothing(self):
        self.assert_printed("""
    Did you know that string is a word?
    Did you know that string 2 is the word nothing?
    I said string.
    I said string 2.
    """, 'nothing\nnothing\n')


if __name__ == '__main__':
    unittest.main()

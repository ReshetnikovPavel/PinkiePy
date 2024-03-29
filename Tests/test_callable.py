import unittest

import fim_exception
import special_words
from fim_callable import FimClass, FimFunction, FimCallable, FimInstance
from fim_interpreter import Interpreter
from fim_lexer import Lexer, Literals, Token
from fim_parser import Parser
from fim_resolver import Resolver


class Base(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser(self.lexer)
        self.interpreter = Interpreter(self.parser)
        self.resolver = Resolver(self.interpreter)

    def tearDown(self):
        pass


class ClassTests(Base):
    def testInit(self):
        fim_class = FimClass('class name', None, ['a', 'b'], [])
        self.assertTrue(fim_class.name == 'class name')
        self.assertTrue(fim_class.methods == ['a', 'b'])

    def testStr(self):
        fim_class = FimClass('class name', None, [], [])
        self.assertTrue(str(fim_class) == 'class name')

    def testClassIsFimCallable(self):
        fim_class = FimClass('class name', None, [], [])
        self.assertTrue(isinstance(fim_class, FimCallable))

    def testCall(self):
        fim_class = FimClass('class name', None, {}, {})
        instance = fim_class.call(self.interpreter, [])
        self.assertTrue(isinstance(instance, FimInstance))

    def testFindMethod(self):
        fim_function = FimFunction(None, None)
        fim_class = FimClass(
            'class name', None, {'method': fim_function}, [])
        self.assertTrue(fim_class.find_method('method') == fim_function)

    def testFindMethodNoSuchMethod(self):
        fim_class = FimClass(
            'class name', FimClass('Princess Celestia', None, {}, {}), {}, {})
        self.assertTrue(fim_class.find_method('method') is None)

    def testFindMethodInSuperClass(self):
        fim_function = FimFunction(None, None)
        class_a = FimClass(
            Token('A', None, None, None, None, None),
            FimClass('Princess Celestia', None, {}, {}),
            {'method': fim_function},
            {})
        self.interpreter.environment.define('A', class_a)
        class_b = FimClass(
            Token('B', None, None, None, None, None),
            class_a,
            {},
            {})
        res = class_b.find_method('method')
        self.assertTrue(res == fim_function)


class InstanceTests(Base):
    def testInit(self):
        fim_class = FimClass('class name', None, [], [])
        instance = FimInstance(fim_class, {})
        self.assertTrue(instance.fim_class == fim_class)

    def testStr(self):
        fim_class = FimClass('class name', None, [], [])
        instance = FimInstance(fim_class, {})
        self.assertTrue(str(instance) == 'class name instance')

    def testGet(self):
        fim_class = FimClass('class name', None, [], [])
        instance = FimInstance(fim_class, {})
        instance.fields['field'] = 'value'
        token = Token('field', Literals.ID, None, None, None, None)
        self.assertTrue(instance.get(token) == 'value')

    def testGetNotExists(self):
        fim_class = FimClass('class name', None, [], [])
        instance = FimInstance(fim_class, {})
        token = Token('field', Literals.ID, None, None, None, None)
        with self.assertRaises(Exception):
            instance.get(token)

    def testGetMethod(self):
        fim_function = FimFunction(None, None)
        fim_class = FimClass(
            'class name', None, {'method': fim_function}, {})
        instance = FimInstance(fim_class, {'method': fim_function})
        instance.fields['method'] = fim_function
        token = Token('method', Literals.ID, None, None, None, None)
        self.assertTrue(instance.get(token) == fim_function)

    def testGetMethodNoSuchMethod(self):
        fim_class = FimClass(
            'class name', FimClass('Princess Celestia', None, {}, {}), {}, {})
        instance = FimInstance(fim_class, {})
        token = Token('method', Literals.ID, None, None, None, None)
        with self.assertRaises(fim_exception.FimRuntimeException):
            instance.get(token)

    def testSet(self):
        fim_class = FimClass('class name', None, [], [])
        instance = FimInstance(fim_class, {})
        instance.fields['field'] = 'value'
        token = Token('field', Literals.ID, None, None, None, None)
        instance.set(token, 'new value')
        self.assertTrue(instance.get(token) == 'new value')


class FunctionTests(Base):
    def testBind(self):
        fim_function = FimFunction(None, None)
        fim_class = FimClass('class name', None, {}, {})
        instance = FimInstance(fim_class, {})
        function = fim_function.bind(instance)
        self.assertTrue(function.closure.get(special_words.this) == instance)


if __name__ == '__main__':
    unittest.main()

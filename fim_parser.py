import special_words
import utility
import fim_ast
from fim_lexer import Literals, Block, Suffix, Keywords, Token
from fim_exception import FimParserException


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.is_currently_parsing_call_arguments_count = 0

    def reset(self):
        self.current_token = self.lexer.get_next_token()
        self.is_currently_parsing_call_arguments_count = 0

    def error(self, message):
        raise FimParserException(self.current_token, message)

    def next_token(self):
        return self.lexer.peek()

    def eat(self, token_name, message, token_block=None, token_suffix=None):
        if self.current_token.type == token_name \
                and ((token_block is None) or (
                token_block == self.current_token.block)) \
                and ((token_suffix is None) or (
                token_suffix == self.current_token.suffix)):
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(message)

    def declaration(self):
        if self.current_token.type == Keywords.REPORT:
            return self.class_declaration()
        if self.current_token.type == Keywords.PARAGRAPH:
            return self.function_declaration()
        if self.current_token.type == Keywords.MANE_PARAGRAPH:
            return self.main_function_declaration()
        if self.current_token.type == Literals.ID \
                and self.next_token().type == Keywords.PUNCTUATION:
            return self.interface_declaration()
        if self.current_token.type == Keywords.IMPORT:
            return self.import_declaration()
        else:
            node = self.statement()
            self.eat(Keywords.PUNCTUATION, 'Expected punctuation')
            return node

    def import_declaration(self):
        self.eat(Keywords.IMPORT, 'Expected import keyword, '
                                  'try "Remember when I wrote about"')
        name = self.current_token
        self.eat(Literals.ID, 'Expected module name')
        self.eat(Keywords.PUNCTUATION, 'Expected punctuation')
        return fim_ast.Import(name)

    def interface_declaration(self):
        name = self.current_token
        self.eat(Literals.ID, 'Expected interface name')
        self.eat(Keywords.PUNCTUATION, 'Expected punctuation')
        methods = []
        while self.current_token.type != Keywords.REPORT or \
                self.current_token.block != Block.END:
            methods.append(self.function_declaration_without_body())

        self.eat(Keywords.REPORT, 'Expected interface ending,'
                                  ' try "Your faithful student,"',
                 token_block=Block.END)
        programmer_name = self.current_token
        self.eat(Literals.ID, 'Expected programmer name')
        self.eat(Keywords.PUNCTUATION, 'Expected punctuation')
        return fim_ast.Interface(name, methods, programmer_name)

    def class_declaration(self):
        superclass = self._handle_superclass()
        implementations = self._handle_implementations()
        class_token = self._handle_class_name()
        self.eat(Keywords.PUNCTUATION, 'Expected punctuation')

        body = self.compound_statement(end_token_names=(Keywords.REPORT,))
        methods, fields = self._divide_methods_from_fields(body)

        programmer_token = self._handle_class_ending()

        return fim_ast.Class(
            class_token, superclass, implementations, body,
            methods, fields, programmer_token)

    def _handle_superclass(self):
        self.eat(Keywords.REPORT, 'Expected report (class) declaration, '
                                  'try "Dear" '
                                  'followed by addressee (superclass) name',
                 token_block=Block.BEGIN)
        superclass = fim_ast.Var(self.current_token)
        self.eat(Literals.ID,
                 'Expected addressee (superclass) name. '
                 f'try "{special_words.base_class_name}"')

        return superclass

    def _handle_implementations(self):
        implementations = []
        while self.current_token.type == Keywords.AND:
            self.eat(Keywords.AND, 'Expected "and" as '
                                   'a separator between interface names')
            implementations.append(fim_ast.Var(self.current_token))
            self.eat(Literals.ID, 'Expected interface name')
        self.eat(Keywords.PUNCTUATION, 'Expected punctuation')

        return implementations

    def _handle_class_name(self):
        class_token = self.current_token
        self.eat(Literals.ID, 'Expected report (class) name')

        return class_token

    @staticmethod
    def _divide_methods_from_fields(body):
        methods = {}
        fields = {}
        for child in body.children:
            if isinstance(child, fim_ast.Function):
                child.is_class_method = True
                methods[child.name.value] = child
            elif isinstance(child, fim_ast.VariableDeclaration):
                fields[child.left.value] = child

        return methods, fields

    def _handle_class_ending(self):
        self.eat(Keywords.REPORT, 'Expected report (class) ending,'
                                  ' try "Your faithful student,"'
                                  ' followed by programmer name',
                 token_block=Block.END)
        programmer_token = self.current_token
        self.eat(Literals.ID, 'Expected programmer name')
        self.eat(Keywords.PUNCTUATION, 'Expected punctuation')

        return programmer_token

    def function_declaration(self, is_main=False):
        function = self.function_declaration_without_body(is_main)

        body = self.compound_statement(end_token_names=(Keywords.PARAGRAPH,))
        function.body = body

        self._handle_function_ending(function)

        return function

    def _handle_function_ending(self, function):
        self.eat(Keywords.PARAGRAPH,
                 'Expected paragraph (function) ending,'
                 ' try "That\'s all about" followed by paragraph name',
                 token_block=Block.END)
        name_in_ending = self.current_token
        if function.name.value != name_in_ending.value:
            self.error('Paragraph (function) name in the ending must be the '
                       'same as at the beginning of the paragraph')
        self.eat(Literals.ID, 'Expected paragraph (function) name')

    def function_declaration_without_body(self, is_main=False):
        if is_main:
            self.eat(Keywords.MANE_PARAGRAPH,
                     'Expected main method declaration, try "Today I learned"'
                     'followed by method name', token_block=Block.BEGIN)
        else:
            self.eat(Keywords.PARAGRAPH,
                     'Expected function declaration, try "I learned"'
                     ' followed by function name', token_block=Block.BEGIN)
        name = self.current_token
        self.eat(Literals.ID, 'Expected paragraph (function) name')

        return_type = None
        if self.current_token.type == Keywords.RETURNED_VARIABLE_TYPE:
            self.eat(Keywords.RETURNED_VARIABLE_TYPE, 'Expected returned type '
                                                      'keyword, try "to get"')
            return_type = self.current_token
            self.eat(Literals.ID, 'Expected returned type name')

        parameters = self._handle_function_parameters()

        return fim_ast.Function(name, return_type, parameters, None, is_main)

    def _handle_function_parameters(self):
        parameters = []
        if self.current_token.type == Keywords.LISTING_PARAGRAPH_PARAMETERS:
            self.eat(Keywords.LISTING_PARAGRAPH_PARAMETERS,
                     'Expected keyword "using" to list function parameters')
            parameters.append(self.current_token)
            self.eat(Literals.ID, 'Expected parameter name')
            while self.current_token.type == Keywords.AND:
                self.eat(Keywords.AND,
                         'Expected "and" as a separator between parameters')
                parameters.append(self.current_token)
                self.eat(Literals.ID, 'Expected parameter name')
        self.eat(Keywords.PUNCTUATION, 'Expected punctuation')

        return parameters

    def main_function_declaration(self):
        return self.function_declaration(is_main=True)

    def return_statement(self):
        self.eat(Keywords.RETURN,
                 'Expected return keyword, try "Then you get"')
        value = self.expr()
        node = fim_ast.Return(value)
        return node

    def run_statement(self):
        self.eat(Keywords.RUN, 'Expected keyword to interpret an expression,'
                               ' try "I would"')
        node = self.expr()
        return node

    def compound_statement(self, end_token_names=None,
                           end_token_blocks=(Block.END,)):
        nodes = self.statement_list(end_token_names=end_token_names,
                                    end_token_blocks=end_token_blocks)

        root = fim_ast.Compound()
        for node in nodes:
            if not isinstance(node, fim_ast.NoOp):
                root.children.append(node)

        return root

    def statement_list(self, end_token_names=None,
                       end_token_blocks=(Block.END,)):
        node = self.statement()

        results = [node]

        self.eat(Keywords.PUNCTUATION, 'Expected punctuation')
        while self.current_token.type != 'EOF' \
                and (end_token_names is None
                     or self.current_token.type not in end_token_names
                     or self.current_token.block not in end_token_blocks):
            results.append(self.statement())
            self.eat(Keywords.PUNCTUATION, 'Expected punctuation')

        return results

    def statement(self):
        if self.current_token.type == Keywords.VAR:
            node = self.variable_declaration()
        elif self.current_token.type == Keywords.PRINT:
            node = self.print_statement()
        elif self.current_token.type == Keywords.INCREMENT:
            node = self.increment_statement()
        elif self.current_token.type == Keywords.DECREMENT:
            node = self.decrement_statement()
        elif self.current_token.type == Literals.ID \
                and self.next_token().suffix == Suffix.POSTFIX:
            node = self.postfix_statement()
        elif self.current_token.type == Literals.ID:
            node = self.assignment()
        elif self.current_token.type == Keywords.IF \
                and self.current_token.block == Block.BEGIN:
            node = self.if_statement()
        elif self.current_token.type == Keywords.WHILE \
                and self.current_token.block == Block.BEGIN:
            node = self.while_statement()
        elif self.current_token.type == Keywords.DO_WHILE \
                and self.current_token.block == Block.BEGIN:
            node = self.do_while_statement()
        elif self.current_token.type == Keywords.FOR \
                and self.current_token.block == Block.BEGIN_PARTNER \
                and self.next_token().type == Keywords.FROM \
                and self.next_token().block == Block.BEGIN_PARTNER:
            node = self.for_statement()
        elif self.current_token.type == Keywords.FOR:
            node = self.for_iter_statement()
        elif self.current_token.type == Keywords.RUN:
            node = self.run_statement()
        elif self.current_token.type == Keywords.PARAGRAPH \
                and self.current_token.block == Block.BEGIN:
            node = self.function_declaration()
        elif self.current_token.type == Keywords.MANE_PARAGRAPH \
                and self.current_token.block == Block.BEGIN:
            node = self.main_function_declaration()
        elif self.current_token.type == Keywords.RETURN:
            node = self.return_statement()
        elif self.current_token.type == Keywords.READLINE:
            node = self.read_statement()
        elif self.current_token.type == Keywords.SWITCH:
            node = self.switch_statement()
        else:
            node = self.empty()
        return node

    def if_statement(self):
        self.eat(Keywords.IF, 'Expected if keyword, try "If" or "When"')
        condition = self.expr()
        then_branch = self._handle_then_branch()
        else_branch = self._handle_else_branch()

        self.eat(Keywords.IF,
                 'Expected if ending, try "That\'s what I would do"',
                 token_block=Block.END)

        return fim_ast.If(condition, then_branch, else_branch)

    def _handle_then_branch(self):
        if self.current_token.type == Keywords.THEN:
            self.eat(Keywords.THEN, 'Expected then keyword, try "then"')
        if self.current_token.type == Keywords.PUNCTUATION:
            self.eat(Keywords.PUNCTUATION, 'Expected punctuation')
        else:
            self.error("Expected punctuation or then keyword,"
                       " try punctuation or 'then'")

        then_branch = self.compound_statement(end_token_names=(
            Keywords.IF, Keywords.ELSE))

        return then_branch

    def _handle_else_branch(self):
        else_branch = None
        if self.current_token.type == Keywords.ELSE:
            self.eat(Keywords.ELSE, 'Expected else keyword, try "Otherwise"')
            self.eat(Keywords.PUNCTUATION, 'Expected punctuation')
            else_branch = self.compound_statement(
                end_token_names=(Keywords.IF,))

        return else_branch

    def switch_statement(self):
        self.eat(Keywords.SWITCH, 'Expected switch keyword,'
                                  ' try "In regards to"')
        variable = self.variable()
        self.eat(Keywords.PUNCTUATION, 'Expected punctuation')
        cases = self._handle_cases()
        default_body = self._handle_default()
        self.eat(Keywords.END_LOOP,
                 'Expected switch ending, try "That’s what I did"',
                 token_block=Block.END)

        return fim_ast.Switch(variable, cases, default_body)

    def _handle_cases(self):
        cases = {}
        while self.current_token.type == Keywords.CASE \
                and self.current_token.block == Block.BEGIN_PARTNER:
            case_value = self._handle_case_value()
            self.eat(Keywords.PUNCTUATION, 'Expected punctuation')
            case_body = self.compound_statement(
                end_token_names=(Keywords.CASE, Keywords.DEFAULT),
                end_token_blocks=(Block.END, Block.BEGIN_PARTNER))
            cases[case_value] = case_body

        return cases

    def _handle_case_value(self):
        self.eat(Keywords.CASE,
                 'Expected case keywords,'
                 ' try "On the" followed by value and ordinal indicator'
                 ' followed by "hoof"', token_block=Block.BEGIN_PARTNER)
        case_value = self.expr()
        self.eat(Keywords.CASE,
                 'Expected case keywords,'
                 ' try "On the" followed by value and ordinal indicator'
                 ' followed by "hoof"',
                 token_block=Block.END_PARTNER)

        return case_value

    def _handle_default(self):
        default_body = None
        if self.current_token.type == Keywords.DEFAULT:
            self.eat(Keywords.DEFAULT, 'Expected default keyword,'
                                       'try "If all else fails')
            self.eat(Keywords.PUNCTUATION, 'Expected punctuation')
            default_body = self.compound_statement(
                end_token_names=(Keywords.END_LOOP,))

        return default_body

    def while_statement(self):
        self.eat(Keywords.WHILE, 'Expected while keyword,'
                                 ' try "While" or "As long as"')
        condition = self.expr()
        self.eat(Keywords.PUNCTUATION, 'Expected punctuation')
        body = self.compound_statement(end_token_names=(Keywords.END_LOOP,))
        self.eat(Keywords.END_LOOP, 'Expected while ending,'
                                    ' try "That’s what I did"', )

        return fim_ast.While(condition, body)

    def do_while_statement(self):
        self.eat(Keywords.DO_WHILE, 'Expected do while keyword,'
                                    ' try "Here’s what I did"',
                 token_block=Block.BEGIN)
        body = self.compound_statement(end_token_names=(Keywords.DO_WHILE,))
        self.eat(Keywords.DO_WHILE, 'Expected do while ending,'
                                    ' try "I did this while"'
                                    ' or "I did this as long as"'
                                    ' followed by condition',
                 token_block=Block.END)
        condition = self.expr()

        return fim_ast.DoWhile(condition, body)

    def for_statement(self):
        self.eat(Keywords.FOR, 'Expected for keyword, try "For every"',
                 token_block=Block.BEGIN_PARTNER)
        self.eat(Keywords.FROM, 'Something went wrong with'
                                ' For every ... from ... to statement',
                 token_block=Block.BEGIN_PARTNER)
        variable = self.variable()
        self.eat(Keywords.FROM, 'Expected keyword for iterating,'
                                ' try "from"',
                 token_block=Block.END_PARTNER)
        from_value = self.expr()
        self.eat(Keywords.FOR, 'Expected keyword for iterating,'
                               ' try "to"', token_block=Block.END_PARTNER)
        to_value = self.expr()
        self.eat(Keywords.PUNCTUATION, 'Expected punctuation')
        body = self.compound_statement(end_token_names=(Keywords.END_LOOP,))
        self.eat(Keywords.END_LOOP, 'Expected for ending,'
                                    ' try "That’s what I did"',
                 token_block=Block.END)

        return fim_ast.For(
            fim_ast.VariableDeclaration(variable, None, from_value),
            to_value, body)

    def for_iter_statement(self):
        self.eat(Keywords.FOR, 'Expected for keyword, try "For every"',
                 token_block=Block.BEGIN_PARTNER)
        variable = self.variable()
        self.eat(Keywords.FOR, 'Expected in keyword, try "in"',
                 token_block=Block.END_PARTNER)
        iterable = self.expr()
        self.eat(Keywords.PUNCTUATION, 'Expected punctuation')
        body = self.compound_statement(end_token_names=(Keywords.END_LOOP,))
        self.eat(Keywords.END_LOOP, 'Expected for ending,'
                                    ' try "That’s what I did"',
                 token_block=Block.END)

        nothing_token = Token('nothing', Literals.NULL, None, None, None, None)

        return fim_ast.ForIter(
            fim_ast.VariableDeclaration(
                variable, None, fim_ast.Null(nothing_token)),
            iterable, body)

    def postfix_statement(self):
        if self.next_token().suffix == Suffix.POSTFIX:
            if self.next_token().type == Keywords.INCREMENT:
                variable = self.variable()
                self.eat(Keywords.INCREMENT, 'Expected increment keyword,'
                                             ' try "got one more"',
                         token_suffix=Suffix.POSTFIX)
                return fim_ast.Increment(variable)
            elif self.next_token().type == Keywords.DECREMENT:
                variable = self.variable()
                self.eat(Keywords.DECREMENT, 'Expected decrement keyword,'
                                             ' try "got one less"',
                         token_suffix=Suffix.POSTFIX)
                return fim_ast.Decrement(variable)
        self.error('Expected postfix statement')

    def variable_declaration(self):
        self.eat(Keywords.VAR, 'Expected variable declaration keyword,'
                               ' try "Did you know that"',
                 token_suffix=Suffix.PREFIX)
        left = self.variable()
        token = self.current_token
        self.eat(Keywords.VAR, 'Expected variable declaration keyword,'
                               ' try anything from'
                               ' is/was/has/had/like/likes/liked',
                 token_suffix=Suffix.INFIX)

        is_const = False
        if self.current_token.type == Keywords.CONST:
            self.eat(Keywords.CONST, 'Expected const keyword,'
                                     'try "always"')
            is_const = True

        if self.current_token.type == Keywords.ARRAY:
            return self.array_declaration(left)

        if self.current_token.type == Literals.ID \
                and self.current_token.value.endswith('s'):
            return self.inline_array_declaration(left)

        right = self.expr()
        node = fim_ast.VariableDeclaration(left, token, right, is_const)
        return node

    def array_declaration(self, name):
        self.eat(Keywords.ARRAY, 'Expected array keyword, try "many"')
        type = self.variable()
        node = fim_ast.Array(name, type)
        return node

    def inline_array_declaration(self, name):
        type = self.variable()
        elements = self.expr()
        node = fim_ast.Array(name, type, elements=elements)
        return node

    def print_statement(self):
        self.eat(Keywords.PRINT, 'Expected print keyword, '
                                 'try anything from '
                                 '"I said/wrote/sang/thought"')
        node = fim_ast.Print(self.expr())
        return node

    def read_statement(self):
        self.eat(Keywords.READLINE, 'Expected readline keyword, '
                                    'try anything from "I heard/read/asked"')
        node = fim_ast.Read(self.variable())
        return node

    def prompt_statement(self):
        read_node = self.read_statement()
        node = fim_ast.Prompt(read_node, self.expr())
        return node

    def increment_statement(self):
        self.eat(Keywords.INCREMENT, 'Expected increment keyword,'
                                     ' try "got one more"',
                 token_suffix=Suffix.PREFIX)
        node = fim_ast.Increment(self.variable())
        return node

    def decrement_statement(self):
        self.eat(Keywords.DECREMENT, 'Expected decrement keyword,'
                                     ' try "got one less"',
                 token_suffix=Suffix.PREFIX)
        node = fim_ast.Decrement(self.variable())
        return node

    def finish_call(self, expr):
        parameters = [self.expr()]
        while self.current_token.type == Keywords.AND:
            self.eat(Keywords.AND,
                     'Expected "and" as a separator between parameters')
            parameters.append(self.expr())

        return fim_ast.FunctionCall(expr, parameters)

    def variable(self):
        node = fim_ast.Var(self.current_token)
        self.eat(Literals.ID, 'Expected variable name')
        return node

    @staticmethod
    def empty():
        return fim_ast.NoOp()

    def expr(self):
        return self.logic()

    def assignment(self):
        expr = self.term()
        if self.current_token.type == Keywords.ASSIGN:
            return self.assign_or_set(expr)
        elif self.current_token.type == Keywords.EQUAL and \
                self.current_token.value == 'is':
            self.eat(Keywords.EQUAL, 'Expected "is" as array'
                                     ' element assignment keyword')
            return self.array_element_assignment(expr)
        return expr

    def assign_or_set(self, expr):
        self.eat(Keywords.ASSIGN, 'Expected assignment operator, '
                                  'try anything from'
                                  ' [is/are] now'
                                  '/now [like/likes]/become/becomes')
        value = self.assignment()

        if isinstance(expr, fim_ast.Var):
            name = expr
            return fim_ast.Assign(name, value)
        elif isinstance(expr, fim_ast.Get):
            get = expr
            return fim_ast.Set(get.object, get.name, value)
        self.error("Invalid assignment target")

    def array_element_assignment(self, expr):
        value = self.assignment()
        if isinstance(expr, fim_ast.Var):
            array_name = utility.separate_array_name(expr.value)
            index = utility.separate_index(expr.value)
            expr.token.value = array_name

            return fim_ast.ArrayElementAssignment(expr, index, value)
        elif isinstance(expr, fim_ast.Get):
            get = expr

            return fim_ast.ArrayElementAssignment(get.object, get.name,
                                                  value)

    def logic(self):
        return self.logic_xor()

    def logic_xor(self):
        if self.current_token.type in (Keywords.XOR,) \
                and self.current_token.suffix == Suffix.PREFIX:
            token = self.current_token
            self.eat(token.type, 'Expected xor operator,'
                                 ' try "either ... or ..."',
                     token_suffix=Suffix.PREFIX)
            left = self.logic_or()
            self.eat(token.type, 'Expected xor operator,'
                                 ' try "either ... or ..."',
                     token_suffix=Suffix.INFIX)
            right = self.logic_or()
            node = fim_ast.BinOp(op=token, left=left, right=right)
            return node
        else:
            return self.logic_or()

    def logic_or(self):
        left = self.logic_and()
        while self.current_token.type in (Keywords.OR,) \
                and self.current_token.suffix == Suffix.INFIX \
                and self.current_token.block == Block.NONE:
            op = self.current_token
            if op.type == Keywords.OR:
                self.eat(Keywords.OR, 'Expected or operator, try "or"',
                         token_suffix=Suffix.INFIX)

            right = self.logic_and()
            left = fim_ast.BinOp(left, op, right)

        return left

    def logic_and(self):
        left = self.equality()

        while self.current_token.type in (Keywords.AND,) \
                and self.current_token.suffix == Suffix.INFIX \
                and self.current_token.block == Block.NONE:

            if self.is_currently_parsing_call_arguments_count != 0:
                return left

            op = self.current_token
            if op.type == Keywords.AND:
                self.eat(Keywords.AND, 'Expected and operator, try "and"',
                         token_suffix=Suffix.INFIX)

            right = self.equality()
            left = fim_ast.BinOp(left, op, right)

        return left

    def equality(self):
        left = self.comparison()

        while self.current_token.type in (Keywords.EQUAL, Keywords.NOT_EQUAL) \
                and self.current_token.suffix == Suffix.INFIX \
                and self.current_token.block == Block.NONE:
            op = self.current_token
            if op.type == Keywords.EQUAL:
                self.eat(Keywords.EQUAL, 'Expected equal operator, '
                                         'try anything from '
                                         '"is/was/has/had/is equal to"',
                         token_suffix=Suffix.INFIX)
            elif op.type == Keywords.NOT_EQUAL:
                self.eat(Keywords.NOT_EQUAL, 'Expected not equal operator,'
                                             ' try anything from'
                                             ' [is/was/has/had][n\'t/ not]"',
                         token_suffix=Suffix.INFIX)

            right = self.comparison()
            left = fim_ast.BinOp(left, op, right)

        return left

    def comparison(self):
        node = self.arithmetic()
        while self.current_token.type in \
                (Keywords.GREATER_THAN,
                 Keywords.GREATER_THAN_OR_EQUAL,
                 Keywords.LESS_THAN_OR_EQUAL,
                 Keywords.LESS_THAN) \
                and self.current_token.suffix == Suffix.INFIX \
                and self.current_token.block == Block.NONE:
            token = self.current_token
            if token.type == Keywords.GREATER_THAN:
                self.eat(Keywords.GREATER_THAN,
                         'Expected greater than operator,'
                         ' try anything from '
                         '"[is/was/has/had] [more/greater] than"',
                         token_suffix=Suffix.INFIX)
            elif token.type == Keywords.GREATER_THAN_OR_EQUAL:
                self.eat(Keywords.GREATER_THAN_OR_EQUAL,
                         'Expected greater than or equal operator,'
                         ' try anything from "[no/not/n’t] less than"',
                         token_suffix=Suffix.INFIX)
            elif token.type == Keywords.LESS_THAN_OR_EQUAL:
                self.eat(Keywords.LESS_THAN_OR_EQUAL,
                         'Expected less than or equal operator, '
                         'try anything from'
                         ' "[no/not/n’t] [more/greater] than"',
                         token_suffix=Suffix.INFIX)
            elif token.type == Keywords.LESS_THAN:
                self.eat(Keywords.LESS_THAN, 'Expected less than operator, '
                                             'try [is/was/has/had] less than',
                         token_suffix=Suffix.INFIX)
            node = fim_ast.BinOp(left=node, op=token, right=self.arithmetic())
        return node

    def arithmetic(self):
        node = self.term()
        while self.current_token.type in (Keywords.MODULO,):
            token = self.current_token
            if token.type == Keywords.MODULO:
                self.eat(Keywords.MODULO, 'Expected modulo operator,'
                                          ' try "modulo"')
                node = fim_ast.BinOp(left=node, op=token, right=self.term())
        return node

    def term(self):
        if self.current_token.type == Keywords.INCREMENT:
            return self.increment_term()

        operations = (Keywords.ADDITION, Keywords.SUBTRACTION)
        if self.current_token.type in operations \
                and self.current_token.suffix == Suffix.PREFIX:
            return self.prefix_bin_op(operations, self.term)

        node = self.factor()
        operations = (Keywords.ADDITION, Keywords.SUBTRACTION, Keywords.AND)
        while self.current_token.type in operations \
                and self.current_token.suffix == Suffix.INFIX \
                and self.current_token.block == Block.NONE:
            token = self.current_token
            if token.type == Keywords.ADDITION:
                self.eat(Keywords.ADDITION, 'Expected addition operator',
                         token_suffix=Suffix.INFIX)
            elif token.type == Keywords.AND:
                if self.is_currently_parsing_call_arguments_count != 0:
                    return node
                self.eat(Keywords.AND, 'expected addition operator "and"',
                         token_suffix=Suffix.INFIX)
            elif token.type == Keywords.SUBTRACTION:
                self.eat(Keywords.SUBTRACTION,
                         'expected subtraction operator',
                         token_suffix=Suffix.INFIX)
            node = fim_ast.BinOp(left=node, op=token, right=self.factor())
        return node

    def prefix_bin_op(self, keywords, bin_op_level_function):
        token = self.current_token
        self.eat(token.type,
                 f'Expected'
                 f' {self.get_expected_keywords_names_string(keywords)}'
                 f' operator',
                 token_suffix=Suffix.PREFIX)
        left = bin_op_level_function()
        self.eat(token.type,
                 f'Expected'
                 f' {self.get_expected_keywords_names_string(keywords)}'
                 f' operator',
                 token_suffix=Suffix.INFIX)
        right = bin_op_level_function()
        node = fim_ast.BinOp(op=token, left=left, right=right)
        return node

    @staticmethod
    def get_expected_keywords_names_string(keywords):
        return ' or '.join([keyword.name for keyword in keywords])

    def increment_term(self):
        self.eat(Keywords.INCREMENT, 'Expected increment prefix',
                 token_suffix=Suffix.PREFIX)
        value = self.term()
        self.eat(Keywords.INCREMENT, 'Expected increment infix',
                 token_block=Block.END_PARTNER)
        variable = self.variable()
        node = fim_ast.Increment(variable, value)
        return node

    def factor(self):
        operations = (Keywords.MULTIPLICATION, Keywords.DIVISION)
        if self.current_token.type in operations \
                and self.current_token.suffix == Suffix.PREFIX:
            return self.prefix_bin_op(operations, self.factor)
        node = self.unary()
        while self.current_token.type in operations \
                and self.current_token.suffix == Suffix.INFIX \
                and self.current_token.block == Block.NONE:
            token = self.current_token
            if token.type == Keywords.MULTIPLICATION:
                self.eat(Keywords.MULTIPLICATION,
                         'Expected multiplication operator')
            elif token.type == Keywords.DIVISION:
                self.eat(Keywords.DIVISION, 'Expected division operator')
            node = fim_ast.BinOp(left=node, op=token, right=self.unary())
        return node

    def unary(self):
        token = self.current_token
        if token.type == Keywords.NOT:
            self.eat(Keywords.NOT, 'Expected not operator,'
                                   'try "not" or "it’s not the case that"')
            return fim_ast.UnaryOp(token, self.unary())
        else:
            node = self.call()
            return node

    def call(self):
        expr = self.concatenation()
        while True:
            if self.current_token.type == \
                    Keywords.LISTING_PARAGRAPH_PARAMETERS:
                self.eat(
                    Keywords.LISTING_PARAGRAPH_PARAMETERS,
                    'Expected keyword "using" to list function parameters')
                self.is_currently_parsing_call_arguments_count += 1
                expr = self.finish_call(expr)
                self.is_currently_parsing_call_arguments_count -= 1
                if len(expr.arguments) != 0 and isinstance(expr.name,
                                                           fim_ast.Get):
                    expr.name.has_parameters = True
            elif self.current_token.type == Keywords.ACCESS_FROM_OBJECT:
                self.eat(Keywords.ACCESS_FROM_OBJECT, 'Expected `s or `')
                name_token = fim_ast.Var(self.current_token)
                self.eat(Literals.ID, 'Expected variable name')
                expr = fim_ast.Get(expr, name_token, False)
            else:
                break

        return expr

    def concatenation(self):
        next_token = self.next_token()
        if self._is_concatenation():
            left = self.primary()
            right = self.expr()

            return fim_ast.BinOp(
                left,
                Token('Concatenation',
                      Keywords.CONCAT,
                      Block.NONE,
                      Suffix.NONE,
                      self.current_token.end,
                      next_token.start),
                right)
        else:
            return self.primary()

    def _is_concatenation(self):
        possible_tokens = (Literals.STRING, Literals.ID)
        current_is_good = self.current_token.type in possible_tokens
        next_is_good = self.next_token().type in possible_tokens
        return current_is_good and next_is_good

    def primary(self):
        token = self.current_token
        if token.type == Literals.NUMBER:
            self.eat(Literals.NUMBER, 'Expected number')
            return fim_ast.Number(token)
        elif token.type == Literals.STRING:
            self.eat(Literals.STRING, 'Expected string')
            return fim_ast.String(token)
        elif token.type == Literals.CHAR:
            self.eat(Literals.CHAR, 'Expected char')
            return fim_ast.Char(token)
        elif token.type == Literals.TRUE:
            self.eat(Literals.TRUE, 'Expected true')
            return fim_ast.Bool(token)
        elif token.type == Literals.FALSE:
            self.eat(Literals.FALSE, 'Expected false')
            return fim_ast.Bool(token)
        elif token.type == Literals.NULL:
            self.eat(Literals.NULL, 'Expected null')
            return fim_ast.Null(token)
        else:
            node = self.variable()
            return node

    def parse(self):
        statements = []
        while not self.current_token.type == 'EOF':
            statements.append(self.declaration())

        return fim_ast.Root(statements)

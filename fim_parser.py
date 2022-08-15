import fim_ast
from fim_lexer import Literals, Block, Suffix, Keywords, Token


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.is_currently_parsing_call_arguments_count = 0

    def error(self):
        raise Exception('Invalid syntax', self.current_token)

    def eat(self, token_name, token_block=None, token_suffix=None):
        if self.current_token.type == token_name \
                and ((token_block is None) or (
                token_block == self.current_token.block)) \
                and ((token_suffix is None) or (
                token_suffix == self.current_token.suffix)):
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def declaration(self):
        if self.current_token.type == Keywords.REPORT:
            return self.class_declaration()
        if self.current_token.type == Keywords.PARAGRAPH:
            return self.function_declaration()
        if self.current_token.type == Keywords.MANE_PARAGRAPH:
            return self.main_function_declaration()
        else:
            node = self.statement()
            self.eat(Keywords.PUNCTUATION)
            return node

    def class_declaration(self):
        self.eat(Keywords.REPORT, token_block=Block.BEGIN)
        superclass = fim_ast.Var(self.current_token)
        self.eat(Literals.ID)

        implementations = []
        while self.current_token.type == Keywords.AND:
            self.eat(Keywords.AND)
            implementations.append(fim_ast.Var(self.current_token))
            self.eat(Literals.ID)
        self.eat(Keywords.PUNCTUATION)

        class_token = self.current_token
        self.eat(Literals.ID)

        self.eat(Keywords.PUNCTUATION)
        body = self.compound_statement(end_token_names=(Keywords.REPORT,))

        methods = []
        fields = []
        for child in body.children:
            if isinstance(child, fim_ast.Function):
                child.is_class_method = True
                methods.append(child)
            elif isinstance(child, fim_ast.VariableDeclaration):
                fields.append(child)

        self.eat(Keywords.REPORT, token_block=Block.END)
        programmer_token = self.current_token
        self.eat(Literals.ID)
        self.eat(Keywords.PUNCTUATION)

        return fim_ast.Class(
            class_token, superclass, implementations, body,
            methods, fields, programmer_token)

    def function_declaration(self, is_main=False):
        if is_main:
            self.eat(Keywords.MANE_PARAGRAPH, token_block=Block.BEGIN)
        else:
            self.eat(Keywords.PARAGRAPH, token_block=Block.BEGIN)
        name = self.current_token
        self.eat(Literals.ID)

        return_type = None
        if self.current_token.type == Keywords.RETURNED_VARIABLE_TYPE:
            self.eat(Keywords.RETURNED_VARIABLE_TYPE)
            return_type = self.current_token
            self.eat(Literals.ID)

        parameters = []
        if self.current_token.type == Keywords.LISTING_PARAGRAPH_PARAMETERS:
            self.eat(Keywords.LISTING_PARAGRAPH_PARAMETERS)
            parameters.append(self.current_token)
            self.eat(Literals.ID)
            while self.current_token.type == Keywords.AND:
                self.eat(Keywords.AND)
                parameters.append(self.current_token)
                self.eat(Literals.ID)
        self.eat(Keywords.PUNCTUATION)

        body = self.compound_statement(end_token_names=(Keywords.PARAGRAPH,))

        self.eat(Keywords.PARAGRAPH, token_block=Block.END)
        name_in_ending = self.current_token
        if name.value != name_in_ending.value:
            self.error()
        self.eat(Literals.ID)

        return fim_ast.Function(name, return_type, parameters, body, is_main)

    def main_function_declaration(self):
        return self.function_declaration(is_main=True)

    def return_statement(self):
        self.eat(Keywords.RETURN)
        # value = None
        # if self.current_token.name != Keywords.PUNCTUATION:
        #     value = self.expr()
        value = self.expr()
        node = fim_ast.Return(value)
        return node

    def run_statement(self):
        self.eat(Keywords.RUN)
        node = self.expr()
        return node

    def compound_statement(self,
                           end_token_names=None,
                           end_block_type=(Block.END,)):
        nodes = self.statement_list(end_token_names=end_token_names)

        root = fim_ast.Compound()
        for node in nodes:
            root.children.append(node)

        return root

    def statement_list(self, end_token_names=None):
        node = self.statement()

        results = [node]

        self.eat(Keywords.PUNCTUATION)
        while self.current_token.type != 'EOF' \
                and (end_token_names is None
                     or self.current_token.type not in end_token_names
                     and self.current_token.block != Block.END):
            results.append(self.statement())
            self.eat(Keywords.PUNCTUATION)

        if self.current_token.type == Literals.ID:
            self.error()

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
                and self.lexer.peek().type == Keywords.ASSIGN:
            node = self.assignment()
        elif self.current_token.type == Literals.ID \
                and self.lexer.peek().suffix == Suffix.POSTFIX:
            node = self.postfix_statement()
        elif self.current_token.type == Keywords.IF \
                and self.current_token.block == Block.BEGIN:
            node = self.if_statement()
        elif self.current_token.type == Keywords.WHILE \
                and self.current_token.block == Block.BEGIN:
            node = self.while_statement()
        elif self.current_token.type == Keywords.DO_WHILE \
                and self.current_token.block == Block.BEGIN:
            node = self.do_while_statement()
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
        self.eat(Keywords.IF)
        condition = self.expr()
        if self.current_token.type == Keywords.THEN:
            self.eat(Keywords.THEN)
            self.eat(Keywords.PUNCTUATION)
        elif self.current_token.type == Keywords.PUNCTUATION:
            self.eat(Keywords.PUNCTUATION)
        else:
            self.error()

        then_branch = self.compound_statement(end_token_names=(
            Keywords.IF, Keywords.ELSE))
        else_branch = None
        if self.current_token.type == Keywords.ELSE:
            self.eat(Keywords.ELSE)
            self.eat(Keywords.PUNCTUATION)
            else_branch = self.compound_statement(
                end_token_names=(Keywords.IF,))

        self.eat(Keywords.IF, token_block=Block.END)

        return fim_ast.If(condition, then_branch, else_branch)

    def switch_statement(self):
        self.eat(Keywords.SWITCH)
        variable = self.variable()
        self.eat(Keywords.PUNCTUATION)
        cases = {}
        while self.current_token.type == Keywords.CASE \
                and self.current_token.block == Block.BEGIN_PARTNER:
            self.eat(Keywords.CASE, token_block=Block.BEGIN_PARTNER)
            case_value = self.expr()
            self.eat(Keywords.CASE, token_block=Block.END_PARTNER)
            self.eat(Keywords.PUNCTUATION)
            case_body = self.compound_statement(end_token_names=
                                                (Keywords.CASE,
                                                 Keywords.DEFAULT),
                                                end_block_type=
                                                (Block.BEGIN_PARTNER,
                                                 Block.NONE))
            cases[case_value] = case_body
        default_body = None
        if self.current_token.type == Keywords.DEFAULT:
            self.eat(Keywords.DEFAULT)
            self.eat(Keywords.PUNCTUATION)
            default_body = self.compound_statement(end_token_names=
                                                   (Keywords.SWITCH,))
        self.eat(Keywords.END_LOOP, token_block=Block.END)
        return fim_ast.Switch(variable, cases, default_body)

    def while_statement(self):
        self.eat(Keywords.WHILE)
        condition = self.expr()
        self.eat(Keywords.PUNCTUATION)
        body = self.compound_statement(end_token_names=(Keywords.END_LOOP,))
        self.eat(Keywords.END_LOOP)

        return fim_ast.While(condition, body)

    def do_while_statement(self):
        self.eat(Keywords.DO_WHILE, token_block=Block.BEGIN)
        body = self.compound_statement(end_token_names=(Keywords.DO_WHILE,))
        self.eat(Keywords.DO_WHILE, token_block=Block.END)
        condition = self.expr()

        return fim_ast.DoWhile(condition, body)

    def postfix_statement(self):
        if self.lexer.peek().suffix == Suffix.POSTFIX:
            if self.lexer.peek().type == Keywords.INCREMENT:
                variable = self.variable()
                self.eat(Keywords.INCREMENT, token_suffix=Suffix.POSTFIX)
                return fim_ast.Increment(variable)
            elif self.lexer.peek().type == Keywords.DECREMENT:
                variable = self.variable()
                self.eat(Keywords.DECREMENT, token_suffix=Suffix.POSTFIX)
                return fim_ast.Decrement(variable)
        self.error()

    def variable_declaration(self):
        self.eat(Keywords.VAR, token_suffix=Suffix.PREFIX)
        left = self.variable()
        token = self.current_token
        self.eat(Keywords.VAR, token_suffix=Suffix.INFIX)
        right = self.expr()
        node = fim_ast.VariableDeclaration(left, token, right)
        return node

    def print_statement(self):
        self.eat(Keywords.PRINT)
        node = fim_ast.Print(self.expr())
        return node

    def read_statement(self):
        self.eat(Keywords.READLINE)
        node = fim_ast.Read(self.variable())
        return node

    def prompt_statement(self):
        read_node = self.read_statement()
        node = fim_ast.Prompt(read_node, self.expr())
        return node

    def increment_statement(self):
        self.eat(Keywords.INCREMENT, token_suffix=Suffix.PREFIX)
        node = fim_ast.Increment(self.variable())
        return node

    def decrement_statement(self):
        self.eat(Keywords.DECREMENT, token_suffix=Suffix.PREFIX)
        node = fim_ast.Decrement(self.variable())
        return node

    def finish_call(self, expr):
        parameters = [self.expr()]
        while self.current_token.type == Keywords.AND:
            self.eat(Keywords.AND)
            parameters.append(self.expr())

        return fim_ast.FunctionCall(expr, parameters)

    def variable(self):
        node = fim_ast.Var(self.current_token)
        self.eat(Literals.ID)
        return node

    @staticmethod
    def empty():
        """An empty production"""
        return fim_ast.NoOp()

    def expr(self):
        return self.assignment()

    # def assignment(self):
    #     if self.lexer.peek().type == Keywords.ASSIGN:
    #         left = self.variable()
    #         token = self.current_token
    #         self.eat(Keywords.ASSIGN)
    #         right = self.assignment()
    #         return fim_ast.Assign(left, token, right)
    #     else:
    #         return self.logic()

    def assignment(self):
        expr = self.logic()
        if self.current_token.type == Keywords.ASSIGN:
            equals = self.current_token
            self.eat(Keywords.ASSIGN)
            value = self.assignment()

            if isinstance(expr, fim_ast.Var):
                name = expr
                return fim_ast.Assign(name, value)
            elif isinstance(expr, fim_ast.Get):
                get = expr
                return fim_ast.Set(get.object, get.name, value)
            raise Exception("Invalid assignment target")
        return expr

    def logic(self):
        return self.logic_xor()

    def logic_xor(self):
        if self.current_token.type in (Keywords.XOR,) \
                and self.current_token.suffix == Suffix.PREFIX:
            token = self.current_token
            self.eat(token.type, token_suffix=Suffix.PREFIX)
            left = self.logic_or()
            self.eat(token.type, token_suffix=Suffix.INFIX)
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
                self.eat(Keywords.OR, token_suffix=Suffix.INFIX)

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
                self.eat(Keywords.EQUAL, token_suffix=Suffix.INFIX)

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
                self.eat(Keywords.EQUAL, token_suffix=Suffix.INFIX)
            elif op.type == Keywords.NOT_EQUAL:
                self.eat(Keywords.NOT_EQUAL, token_suffix=Suffix.INFIX)

            right = self.comparison()
            left = fim_ast.BinOp(left, op, right)

        return left

    def comparison(self):
        node = self.term()
        while self.current_token.type in \
                (Keywords.GREATER_THAN,
                 Keywords.GREATER_THAN_OR_EQUAL,
                 Keywords.LESS_THAN_OR_EQUAL,
                 Keywords.LESS_THAN) \
                and self.current_token.suffix == Suffix.INFIX \
                and self.current_token.block == Block.NONE:
            token = self.current_token
            if token.type == Keywords.GREATER_THAN:
                self.eat(Keywords.GREATER_THAN, token_suffix=Suffix.INFIX)
            elif token.type == Keywords.GREATER_THAN_OR_EQUAL:
                self.eat(Keywords.GREATER_THAN_OR_EQUAL,
                         token_suffix=Suffix.INFIX)
            elif token.type == Keywords.LESS_THAN_OR_EQUAL:
                self.eat(Keywords.LESS_THAN_OR_EQUAL, token_suffix=Suffix.INFIX)
            elif token.type == Keywords.LESS_THAN:
                self.eat(Keywords.LESS_THAN, token_suffix=Suffix.INFIX)
            node = fim_ast.BinOp(left=node, op=token, right=self.term())
        return node

    def term(self):
        if self.current_token.type in (Keywords.ADDITION, Keywords.SUBTRACTION) \
                and self.current_token.suffix == Suffix.PREFIX:
            token = self.current_token
            self.eat(token.type, token_suffix=Suffix.PREFIX)
            left = self.term()
            self.eat(token.type, token_suffix=Suffix.INFIX)
            right = self.term()
            node = fim_ast.BinOp(op=token, left=left, right=right)
            return node
        else:
            node = self.factor()
            while self.current_token.type in (
                    Keywords.ADDITION, Keywords.SUBTRACTION, Keywords.AND) \
                    and self.current_token.suffix == Suffix.INFIX and self.current_token.block == Block.NONE:
                token = self.current_token
                if token.type == Keywords.ADDITION:
                    self.eat(Keywords.ADDITION, token_suffix=Suffix.INFIX)
                elif token.type == Keywords.AND:

                    if self.is_currently_parsing_call_arguments_count != 0:
                        return node

                    #   TODO: while typechecking should become ADDITION
                    self.eat(Keywords.AND, token_suffix=Suffix.INFIX)
                elif token.type == Keywords.SUBTRACTION:
                    self.eat(Keywords.SUBTRACTION, token_suffix=Suffix.INFIX)
                node = fim_ast.BinOp(left=node, op=token, right=self.factor())
            return node

    def factor(self):
        if self.current_token.type in (
                Keywords.MULTIPLICATION, Keywords.DIVISION) \
                and self.current_token.suffix == Suffix.PREFIX:
            token = self.current_token
            self.eat(token.type, token_suffix=Suffix.PREFIX,
                     token_block=Block.BEGIN_PARTNER)
            left = self.factor()
            self.eat(token.type, token_suffix=Suffix.INFIX,
                     token_block=Block.END_PARTNER)
            right = self.factor()
            node = fim_ast.BinOp(op=token, left=left, right=right)
            return node
        else:
            node = self.unary()
            while self.current_token.type in (
                    Keywords.MULTIPLICATION, Keywords.DIVISION) \
                    and self.current_token.suffix == Suffix.INFIX and self.current_token.block == Block.NONE:
                token = self.current_token
                if token.type == Keywords.MULTIPLICATION:
                    self.eat(Keywords.MULTIPLICATION)
                elif token.type == Keywords.DIVISION:
                    self.eat(Keywords.DIVISION)
                node = fim_ast.BinOp(left=node, op=token, right=self.unary())
            return node

    def unary(self):
        token = self.current_token
        if token.type == Keywords.NOT:
            self.eat(Keywords.NOT)
            return fim_ast.UnaryOp(token, self.unary())
        else:
            node = self.call()
            return node

    def call(self):
        expr = self.concatenation()
        while True:
            if self.current_token.type == Keywords.LISTING_PARAGRAPH_PARAMETERS:
                self.eat(Keywords.LISTING_PARAGRAPH_PARAMETERS)
                self.is_currently_parsing_call_arguments_count += 1
                expr = self.finish_call(expr)
                self.is_currently_parsing_call_arguments_count -= 1
                if len(expr.arguments) != 0 and isinstance(expr.name,
                                                           fim_ast.Get):
                    expr.name.has_parameters = True
            elif self.current_token.type == Keywords.ACCESS_FROM_OBJECT:
                self.eat(Keywords.ACCESS_FROM_OBJECT)
                name_token = fim_ast.Var(self.current_token)
                self.eat(Literals.ID)
                expr = fim_ast.Get(expr, name_token, False)
            else:
                break

        return expr

    def concatenation(self):
        next_token = self.lexer.peek()
        if self.current_token.type == Literals.STRING \
                and next_token.type != Keywords.PUNCTUATION \
                or next_token.type == Literals.STRING:
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

    def primary(self):
        token = self.current_token
        if token.type == Literals.NUMBER:
            self.eat(Literals.NUMBER)
            return fim_ast.Number(token)
        elif token.type == Literals.STRING:
            self.eat(Literals.STRING)
            return fim_ast.String(token)
        elif token.type == Literals.CHAR:
            self.eat(Literals.CHAR)
            return fim_ast.Char(token)
        elif token.type == Literals.TRUE:
            self.eat(Literals.TRUE)
            return fim_ast.Bool(token)
        elif token.type == Literals.FALSE:
            self.eat(Literals.FALSE)
            return fim_ast.Bool(token)
        elif token.type == Literals.NULL:
            self.eat(Literals.NULL)
            return fim_ast.Null(token)
        else:
            node = self.variable()
            return node

    def parse(self):
        statements = []
        while not self.current_token.type == 'EOF':
            statements.append(self.declaration())

        return fim_ast.Trunk(statements)

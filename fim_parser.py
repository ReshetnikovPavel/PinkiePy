import fim_ast
from lexer import Literals
from lexer import Keywords
from lexer import Suffix
from lexer import Block


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_name, token_block=None, token_suffix=None):
        if self.current_token.name == token_name\
                and ((token_block is None) or (token_block == self.current_token.block)):
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def compound_statement(self):
        # compound_name = self.current_token.name
        # self.eat(compound_name, token_block=Block.BEGIN)
        nodes = self.statement_list()
        # self.eat(compound_name, token_block=Block.END)

        root = fim_ast.Compound()
        for node in nodes:
            root.children.append(node)

        return root

    def statement_list(self):
        node = self.statement()

        results = [node]

        while self.current_token.name == Keywords.PUNCTUATION:
            self.eat(Keywords.PUNCTUATION)
            results.append(self.statement())

        if self.current_token.name == 'NAME':
            self.error()

        return results

    def statement(self):
        #if self.current_token.block == Block.BEGIN:
        #    node = self.compound_statement()
        #el
        if self.current_token.name == Keywords.VAR:
            node = self.assignment_statement()
        else:
            node = self.empty()
        return node

    def assignment_statement(self):
        self.eat(Keywords.VAR)
        left = self.variable()
        token = self.current_token
        self.eat(Keywords.VAR)
        right = self.expr()
        node = fim_ast.Assign(left, token, right)
        return node

    def variable(self):
        node = fim_ast.Var(self.current_token)
        self.eat('NAME')
        return node

    def empty(self):
        """An empty production"""
        return fim_ast.NoOp()

    def factor(self):
        token = self.current_token
        if token.name == Literals.NUMBER:
            self.eat(Literals.NUMBER)
            return fim_ast.Number(token)
        # elif token.name == 'LPAREN':
        #     self.eat('LPAREN')
        #     node = self.expr()
        #     self.eat('RPAREN')
        #     return node
        else:
            node = self.variable()
            return node

    def term(self):
        node = self.factor()
        while self.current_token.name in (Keywords.MULTIPLICATION, Keywords.DIVISION):
            token = self.current_token
            if token.name == Keywords.MULTIPLICATION:
                self.eat(Keywords.MULTIPLICATION)
            elif token.name == Keywords.DIVISION:
                self.eat(Keywords.DIVISION)
            node = fim_ast.BinOp(left=node, op=token, right=self.factor())
        return node

    def expr(self):
        node = self.term()
        while self.current_token.name in (Keywords.ADDITION, Keywords.SUBTRACTION)\
                and self.current_token.suffix == Suffix.INFIX:
            token = self.current_token
            if token.name == Keywords.ADDITION:
                self.eat(Keywords.ADDITION)
            elif token.name == Keywords.SUBTRACTION:
                self.eat(Keywords.SUBTRACTION)
            node = fim_ast.BinOp(left=node, op=token, right=self.term())
        return node

    def parse(self):
        return self.compound_statement()
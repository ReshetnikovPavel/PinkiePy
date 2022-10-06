import copy
import re

import fim_ast
from fim_lexer import Keywords, Token, Literals
from node_visitor import NodeVisitor
from fim_exception import FimCSharpTranslatorException


class CSharpTranslator(NodeVisitor):
    def __init__(self, tree, resolver):
        self.tree = tree
        self.resolver = resolver

    def translate(self):
        return 'using System;\n' \
               f'{self.visit(self.tree)}'

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if node.op.type == Keywords.ADDITION:
            return f'({left}) + ({right})'
        elif node.op.type == Keywords.SUBTRACTION:
            return f'({left}) - ({right})'
        elif node.op.type == Keywords.MULTIPLICATION:
            return f'({left}) * ({right})'
        elif node.op.type == Keywords.DIVISION:
            return f'({left}) / ({right})'
        elif node.op.type == Keywords.GREATER_THAN:
            return f'({left}) > ({right})'
        elif node.op.type == Keywords.LESS_THAN:
            return f'({left}) < ({right})'
        elif node.op.type == Keywords.GREATER_THAN_OR_EQUAL:
            return f'({left}) >= ({right})'
        elif node.op.type == Keywords.LESS_THAN_OR_EQUAL:
            return f'({left}) <= ({right})'
        elif node.op.type == Keywords.EQUAL:
            return f'({left}) == ({right})'
        elif node.op.type == Keywords.NOT_EQUAL:
            return f'({left}) != ({right})'
        elif node.op.type == Keywords.AND:
            if type(left) == float and type(right) == float:
                return f'({left}) + ({right})'
            return f'({left}) && ({right})'
        elif node.op.type == Keywords.OR:
            return f'({left}) || ({right})'
        elif node.op.type == Keywords.XOR:
            return f'({left}) != ({right})'
        elif node.op.type == Keywords.CONCAT:
            return f'({left}).ToString() + ({right}).ToString()'
        elif node.op.type == Keywords.MODULO:
            return f'({left}) % ({right})'
        else:
            raise FimCSharpTranslatorException(
                node.op, f"Unknown operator: {node.op}")

    def visit_UnaryOp(self, node):
        return f'!({self.visit(node.expr)})'

    def visit_Number(self, node):
        return f'{node.value}d'

    def visit_String(self, node):
        return f'"{node.value}"'

    def visit_Char(self, node):
        return f"'{node.value}'"

    def visit_Bool(self, node):
        if node.value is True:
            return 'true'
        return 'false'

    def visit_Null(self, node):
        return 'null'

    def visit_Compound(self, node):
        children = []
        for child in node.children:
            children.append(self.add_semicolon(self.visit(child)))
        return '\n{\n' + '\n'.join(children) + '\n}\n'

    def add_semicolon(self, string):
        return f'{string};'

    def visit_Root(self, node):
        children = [self.visit(child) for child in node.children]
        return ';\n'.join(children) + ';'

    def visit_If(self, node):
        result = f'if ({self.visit(node.condition)})'
        result += self.visit(node.then_branch)
        if node.else_branch is not None:
            result += 'else'
            result += self.visit(node.else_branch)
        return result

    def visit_While(self, node):
        result = f'while ({self.visit(node.condition)})'
        result += self.visit(node.body)
        return result

    def visit_DoWhile(self, node):
        result = 'do'
        result += self.visit(node.body)
        result += f'while ({self.visit(node.condition)})'
        return result

    def visit_For(self, node):
        result = f'for ({self.visit(node.init)};' \
                 f' {self.visit(node.init.left)}' \
                 f' <= {self.visit(node.to_value)};' \
                 f' {self.visit(node.init.left)}++)'
        body = copy.copy(node.body)
        body.children.pop()
        result += self.visit(body)
        return result

    def visit_ForIter(self, node):
        result = f'foreach (var {self.visit(node.init.left)}' \
                 f' in {self.visit(node.iterable)})'
        result += self.visit(node.body)
        return result

    def visit_StatementList(self, node):
        pass

    def visit_NoOp(self, node):
        return ''

    def visit_Assign(self, node):
        type, name = self.convert_type(node.left)
        return f'{self.convert_spaces_to_underscores(name)}' \
               f' = {self.visit(node.right)}'

    def visit_VariableDeclaration(self, node):
        type_left, name_left = self.convert_type(node.left)
        if type_left == 'object':
            type_left = 'var'
        return f'{type_left} {self.convert_spaces_to_underscores(name_left)}' \
               f' = {self.visit(node.right)}'

    def visit_Var(self, node):
        type, name = self.convert_type(node.token)
        variable_name = self.convert_spaces_to_underscores(name)
        return variable_name

    @staticmethod
    def convert_spaces_to_underscores(string):
        return re.sub(r"['\s]", '_', string)

    def visit_FunctionCall(self, node):
        res = f'{self.visit(node.name)}'
        res += '('
        for argument in node.arguments[:-1]:
            res += f'{self.visit(argument)}, '
        res += f'{self.visit(node.arguments[-1])}'
        res += ')'
        return res

    def visit_Return(self, node):
        return f'return {self.visit(node.value)}'

    def visit_Increment(self, node):
        if node.value == 1:
            return f'({self.visit(node.variable)})++'
        return f'({self.visit(node.variable)}) += {node.value}'

    def visit_Decrement(self, node):
        if node.value == 1:
            return f'({self.visit(node.variable)})--'
        return f'({self.visit(node.variable)}) -= {node.value}'

    def visit_Print(self, node):
        return f"Console.WriteLine({self.visit(node.expr)})"

    def visit_Read(self, node):
        return f'{node.variable.value} = Console.ReadLine()'

    def visit_Function(self, node):
        return_type, name = self.convert_type(node.return_type) if node.return_type \
            else ('object', '')
        result = f'public static {return_type} {node.name.value}'
        result += '('
        for argument in node.params[:-1]:
            type, name = self.convert_type(argument)
            result += f'{type}' \
                      f' {self.convert_spaces_to_underscores(name)}, '
        if node.params:
            type, name = self.convert_type(node.params[-1])
            result += f'{type}' \
                      f' {name}'
        result += ')'
        if return_type == 'object':
            node.body.children.append(
                fim_ast.Return(
                    fim_ast.Null(Token(None, None, None, None, None, None))))
        result += self.visit(node.body)
        return result

    def convert_type(self, token):
        type, name = self.resolver.separate_type_str(token)
        if type == Literals.NUMBER:
            return 'double', name
        elif type == Literals.STRING:
            return 'string', name
        elif type == Literals.CHAR:
            return 'char', name
        elif type == Literals.BOOL:
            return 'bool', name
        elif type == Literals.NULL:
            return 'object'
        return 'object', name


    def visit_Class(self, node):
        pass

    def visit_Interface(self, node):
        pass

    def visit_Get(self, node):
        pass

    def visit_Set(self, node):
        pass

    def visit_Switch(self, node):
        res = f'switch ({self.visit(node.variable)})\n'
        res += '{\n'
        for case, body in node.cases.items():
            res += f'case {self.visit(case)}:'
            res += self.visit(body)
            res += 'break;\n'
        res += 'default:'
        res += self.visit(node.default)
        res += 'break;\n'
        res += '}'
        return res

    def visit_Import(self, node):
        return f'using {self.visit(node.name)};'

    def visit_Array(self, node):
        pass

    def visit_ArrayElementAssignment(self, node):
        pass

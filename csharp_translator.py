import copy
import re

import fim_ast
from fim_lexer import Keywords, Token
from node_visitor import NodeVisitor
from fim_exception import FimCSharpTranslatorException


class CSharpTranslator(NodeVisitor):
    def __init__(self, tree, interpreter):
        self.tree = tree
        self.interpreter = interpreter

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
            raise FimCSharpTranslatorException(node.op,
                                               f"Unknown operator: {node.op}")

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
        return f'{node.left.value} = {self.visit(node.right)}'

    def visit_VariableDeclaration(self, node):
        return f'var {node.left.value} = {self.visit(node.right)}'

    def visit_Var(self, node):
        variable_name = re.sub(r"['\s]", '_', node.value)
        if self.interpreter.lookup_variable(node.token, node):
            pass
        return variable_name

    def visit_FunctionCall(self, node):
        pass

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
        return_type = self.visit(node.return_type) if node.return_type \
            else 'object'
        result = f'public static {return_type} {node.name.value}()'
        if return_type == 'object':
            node.body.children.append(
                fim_ast.Return(
                    fim_ast.Null(Token(None, None, None, None, None, None))))
        result += self.visit(node.body)
        return result

    def visit_Class(self, node):
        pass

    def visit_Interface(self, node):
        pass

    def visit_Get(self, node):
        pass

    def visit_Set(self, node):
        pass

    def visit_Switch(self, node):
        pass

    def visit_Import(self, node):
        return f'using {self.visit(node.name)};'

    def visit_Array(self, node):
        pass

    def visit_ArrayElementAssignment(self, node):
        pass

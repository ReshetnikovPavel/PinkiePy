class Report:
    def __init__(self, name, super_class, interfaces, paragraphs, mane_paragraph, programmer_name):
        self.name = name
        self.super_class = super_class
        self.interfaces = interfaces
        self.paragraphs = paragraphs
        self.mane_paragraph = mane_paragraph
        self.programmer_name = programmer_name


class Interface:
    def __init__(self, name, paragraphs, programmer_name):
        self.name = name
        self.paragraphs = paragraphs
        self.programmer_name = programmer_name


class Paragraph:
    def __init__(self, name, return_type, arguments, body):
        self.name = name
        self.return_type = return_type
        self.arguments = arguments
        self.body = body


class Variable:
    def __init__(self, name, fim_type, value):
        self.name = name
        self.type = fim_type
        self.value = value


class Constant(Variable):
    def __init__(self, name, fim_type, value):
        super().__init__(name, fim_type, value)

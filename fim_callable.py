import copy
import special_words
import utility

from environment import Environment


class FimCallable:
    def arity(self):
        pass

    def call(self, interpreter, arguments):
        pass


class FimFunction(FimCallable):
    def __init__(self, declaration, closure):
        self.closure = closure
        self.declaration = declaration

    def call(self, interpreter, arguments):
        environment = Environment(self.closure)
        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].value, arguments[i])
        try:
            interpreter.execute_compound(self.declaration.body.children,
                                         Environment(environment))
        except FimReturn as return_value:
            return return_value.value
        return None

    def arity(self):
        return len(self.declaration.params)

    def bind(self, instance):
        environment = Environment(self.closure)
        environment.define(special_words.this, instance)
        return FimFunction(self.declaration, environment)


class FimReturn(RuntimeError):
    def __init__(self, value):
        super().__init__("Return")
        self.value = value


class FimClass(FimCallable):
    def __init__(self, name, superclass, methods, fields):
        self.name = name
        self.superclass = superclass
        self.methods = methods
        self.fields = self.add_superclass_fields(fields)

    def __str__(self):
        return self.name

    def arity(self):
        return 0

    def call(self, interpreter, arguments):
        instance = FimInstance(self, self.fields)
        return instance

    def add_superclass_fields(self, fields):
        if self.superclass is None:
            return fields

        fields = copy.deepcopy(fields)
        for key, value in self.superclass.fields.items():
            if key not in fields:
                fields[key] = value
        return fields

    def find_method(self, name):
        if name in self.methods:
            return self.methods[name]

        if self.superclass is not None:
            return self.superclass.find_method(name)

        return None


class FimInstance:
    def __init__(self, fim_class, fields):
        self.fim_class = fim_class
        self.fields = copy.copy(fields)
        self.fields[special_words.this] = self

    def __str__(self):
        return f'{self.fim_class.name} instance'

    def get(self, token):
        if token.value in self.fields:
            return self.fields[token.value]

        method = self.fim_class.find_method(token.value)
        if method is not None:
            return method.bind(self)

        raise RuntimeError(f'{self.fim_class.name} has no field {token.value}')

    def set(self, token, value):
        self.fields[token.value] = value


class FimArray:
    def __init__(self, elements):
        self.elements = elements

    def __iter__(self):
        return iter(self.elements)

    def __str__(self):
        return f'{", ".join(map(str, self.elements))}'

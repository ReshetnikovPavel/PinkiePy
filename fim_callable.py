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
            interpreter.execute_compound(self.declaration.body.children, Environment(environment)) #TODO this might be a potential fix
        except FimReturn as return_value:
            return return_value.value
        return None

    def arity(self):
        return len(self.declaration.params)


class FimReturn(RuntimeError):
    def __init__(self, value):
        super().__init__("Return")
        self.value = value


class FimClass(FimCallable):
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods

    def __str__(self):
        return self.name

    def arity(self):
        return 0

    def call(self, interpreter, arguments):
        instance = FimInstance(self)
        return instance

    def find_method(self, name):
        if name in self.methods:
            return self.methods[name]
        return None


class FimInstance:
    def __init__(self, fim_class):
        self.fim_class = fim_class
        self.fields = {}

    def __str__(self):
        return f'{self.fim_class.name} instance'

    def get(self, token):
        if token.value in self.fields:
            return self.fields[token.value]

        method = self.fim_class.find_method(token.value)
        if method is not None:
            return method

        raise RuntimeError(f'{self.fim_class.name} has no field {token.value}')

    def set(self, token, value):
        self.fields[token.value] = value


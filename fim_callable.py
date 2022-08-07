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

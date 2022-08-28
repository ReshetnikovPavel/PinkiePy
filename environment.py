from fim_exception import FimRuntimeException
from fim_exception import FimEnvironmentException


class Environment:
    def __init__(self, enclosing=None):
        self.enclosing = None
        self._values = {}
        if enclosing is not None:
            self.enclosing = enclosing

    def define(self, name, value):
        if name in self._values:
            raise FimEnvironmentException(f'Variable already defined: {name}')
        self._values[name] = value

    def declare(self, name):
        if name.value in self._values:
            raise FimRuntimeException(
                name, f'Variable already defined: {name.value}')
        self._values[name.value] = None

    def get(self, name):
        if name in self._values:
            return self._values.get(name)

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise FimEnvironmentException(f'Undefined variable: {name}')

    def assign(self, name, value):
        if name.value in self._values:
            self._values[name.value] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return

        raise FimRuntimeException(name, f'Undefined variable: {name.value}')

    def modify(self, name, relate, value):
        return self.assign(name, relate(self.get(name.value), value))

    def modify_at(self, distance, name, relate, value):
        return self.assign_at(distance, name,
                              relate(self.get_at(distance, name.value), value))

    def get_at(self, distance, name):
        return self.ancestor(distance).get(name)

    def assign_at(self, distance, token, value):
        self.ancestor(distance)._values[token.value] = value

    def ancestor(self, distance):
        environment = self
        for i in range(distance):
            environment = environment.enclosing
        return environment

    def values(self):
        return self._values.values()

    def items(self):
        return self._values.items()

    def __str__(self):
        return str(self._values)

    def __contains__(self, key):
        return key in self._values

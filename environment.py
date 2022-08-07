class Environment:
    def __init__(self, enclosing=None):
        self.enclosing = None
        self._values = {}
        if enclosing is not None:
            self.enclosing = enclosing

    def define(self, name, value):
        if name in self._values:
            raise NameError('Variable already defined: %s' % name)
        self._values[name] = value

    def get(self, name):
        if name in self._values:
            return self._values.get(name)

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise NameError('Undefined variable: %s' % name)

    def assign(self, name, value):
        if name in self._values:
            self._values[name] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return

        raise NameError('Undefined variable: %s' % name)

    def modify(self, name, relate, value):
        return self.assign(name, relate(self.get(name), value))

    def modify_at(self, distance, name, relate, value):
        return self.assign_at(distance, name, relate(self.get_at(distance, name.value), value))

    def get_at(self, distance, name):
        return self.ancestor(distance).get(name)

    def assign_at(self, distance, token, value):
        self.ancestor(distance)._values[token.value] = value

    def ancestor(self, distance):
        environment = self
        for i in range(distance):
            environment = environment.enclosing
        return environment

    def __str__(self):
        return str(self._values)

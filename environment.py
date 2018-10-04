from run_time_error import RunTimeError

class Environment():
    def __init__(self, enclosing=None):
        self.enclosing = enclosing

        self.values = {}

    def define(self, name, value):
        self.values[name] = value

    def assign(self, name, value):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return

        raise RunTimeError(name, f"Undefined variable '{name.lexeme}'")

    def assign_at(self, distance, name, value):
        self.ancestor(distance).values[name.lexeme] = value

    def get(self, name):
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise RunTimeError(name, f"Undefined variable '{name}'")

    def get_at(self, distance, name):
        return self.ancestor(distance).values[name]

    def ancestor(self, distance):
        environment = self
        for i in range(0, distance):
            environment = environment.enclosing

        return environment

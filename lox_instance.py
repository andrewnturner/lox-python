from run_time_error import RunTimeError

class LoxInstance():
    def __init__(self, klass):
        self.klass = klass

        self.fields = {}

    def get(self, name):
        try:
            return self.fields[name.lexeme]
        except KeyError:
            pass

        method = self.klass.find_method(self, name.lexeme)
        if method is not None:
            return method

        raise RunTimeError(name, f"Undefined property '{name.lexeme}'")

    def set_field(self, name, value):
        self.fields[name.lexeme] = value

    def __str__(self):
        return f"<{self.klass.name} instance>"
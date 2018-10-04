from lox_callable import LoxCallable
from environment import Environment

class LoxFunction(LoxCallable):
    def __init__(self, declaration, closure, is_initializer):
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer

    def arity(self):
        return len(self.declaration.parameters)

    def call(self, interpreter, arguments):
        environment = Environment(self.closure)

        for i in range(0, len(self.declaration.parameters)):
            environment.define(self.declaration.parameters[i].lexeme, arguments[i])
        
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return as e:
            if self.is_initializer:
                return self.closure.get_at(0, 'this')
            return e.value

        if self.is_initializer:
            return self.closure.get_at(0, 'this')

        return None

    def bind(self, instance):
        environment = Environment(self.closure)
        environment.define('this', instance)

        return LoxFunction(self.declaration, environment, self.is_initializer)

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"


class Return(Exception):
    def __init__(self, value):
        super().__init__(self)

        self.value = value
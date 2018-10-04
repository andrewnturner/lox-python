from lox_callable import LoxCallable
from lox_instance import LoxInstance

class LoxClass(LoxCallable):
    def __init__(self, name, superclass, methods):
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def call(self, interpreter, arguments):
        instance = LoxInstance(self)

        try:
            initializer = self.methods['init']
            initializer.bind(instance).call(interpreter, arguments)
        except KeyError:
            pass

        return instance

    def arity(self):
        try:
            initializer = self.methods['init']
            return initializer.arity()
        except KeyError:
            return 0;

    def find_method(self, instance, name):
        try:
            return self.methods[name].bind(instance)
        except KeyError:
            pass

        if self.superclass is not None:
            return self.superclass.find_method(instance, name)

        return None

    def __str__(self):
        return f"<Class {self.name}>"
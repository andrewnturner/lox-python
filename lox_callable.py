class LoxCallable():
    def arity(self):
        raise NotImplemented

    def call(self, interpreter, arguments):
        raise NotImplemented
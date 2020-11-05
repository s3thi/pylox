from lox_instance import LoxInstance


class LoxClass:
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods

    def find_method(self, name):
        if name in self.methods:
            return self.methods[name]

        return None

    def __str__(self):
        return self.name

    def call(self, interpreter, arguments):
        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)

        return instance

    def arity(self):
        initializer = self.find_method("init")

        if initializer is None:
            return 0

        return initializer.arity()

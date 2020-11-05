from lox_runtime_error import LoxRuntimeError


class LoxInstance:
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}

    def __str__(self):
        return self.klass.name + " instance"

    def get(self, name):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)

        raise LoxRuntimeError(f"Undefined property '{name.lexeme}'.")

    def _set(self, name, value):
        self.fields[name.lexeme] = value

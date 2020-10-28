from time import time_ns

from lox_token_type import LoxTokenType
from lox_runtime_error import LoxRuntimeError
from lox_function import LoxFunction
from lox_return import LoxReturn
from environment import Environment


class Interpreter:
    def __init__(self):
        self._globals = Environment()
        self._locals = {}
        self.environment = self._globals

        class Clock:
            def arity(self):
                return 0

            def call(self, interpreter, arguments):
                return time_ns() // 1000_000

            def to_string(self):
                return "<native fn>"

        self._globals.define("clock", Clock())

    def interpret(self, statements):
        try:
            for statement in statements:
                self.execute(statement)
        except LoxRuntimeError as error:
            from lox import Lox

            Lox.runtime_error(error)

    def evaluate(self, expr):
        return expr.accept(self)

    def execute(self, stmt):
        stmt.accept(self)

    def resolve(self, expr, depth):
        self._locals[expr] = depth

    def execute_block(self, statements, environment):
        previous = self.environment
        try:
            self.environment = environment
            for stmt in statements:
                self.execute(stmt)
        finally:
            self.environment = previous

    def visit_block_stmt(self, stmt):
        self.execute_block(stmt.statements, Environment(self.environment))
        return None

    def visit_expression_stmt(self, stmt):
        self.evaluate(stmt.expression)
        return None

    def visit_function_stmt(self, stmt):
        function = LoxFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, function)
        return None

    def visit_if_stmt(self, stmt):
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)

        return None

    def visit_print_stmt(self, stmt):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))
        return None

    def visit_return_stmt(self, stmt):
        value = None

        if stmt.value is not None:
            value = self.evaluate(stmt.value)

        raise LoxReturn(value)

    def visit_var_stmt(self, stmt):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)

        self.environment.define(stmt.name.lexeme, value)
        return None

    def visit_while_stmt(self, stmt):
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)

        return None

    def visit_assign_expr(self, expr):
        value = self.evaluate(expr.value)

        distance = self._locals.get(expr)
        if distance is not None:
            self.environment.assign_at(distance, expr.name, value)
        else:
            self._globals.assign(expr.name, value)

        return value

    def visit_literal_expr(self, expr):
        return expr.value

    def visit_logical_expr(self, expr):
        left = self.evaluate(expr.left)

        if expr.operator.ttype == LoxTokenType.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left

        return self.evaluate(expr.right)

    def visit_grouping_expr(self, expr):
        return self.evaluate(expr.expression)

    def visit_unary_expr(self, expr):
        right = self.evaluate(expr.right)

        if expr.operator.ttype == LoxTokenType.MINUS:
            self.check_number_operand(expr.operator, right)
            return -float(right)
        elif expr.operator.ttype == LoxTokenType.BANG:
            return not self.is_truthy(right)

        return None

    def visit_variable_expr(self, expr):
        return self.lookup_variable(expr.name, expr)

    def lookup_variable(self, name, expr):
        distance = self._locals.get(expr)

        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        else:
            return self._globals.get(name)

    def visit_binary_expr(self, expr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        if expr.operator.ttype == LoxTokenType.MINUS:
            self.check_number_operands(expr.operator, left, right)
            return float(left) - float(right)
        elif expr.operator.ttype == LoxTokenType.SLASH:
            self.check_number_operands(expr.operator, left, right)
            return float(left) / float(right)
        elif expr.operator.ttype == LoxTokenType.STAR:
            self.check_number_operands(expr.operator, left, right)
            return float(left) * float(right)
        elif expr.operator.ttype == LoxTokenType.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return float(left) + float(right)
            elif isinstance(left, str) and isinstance(right, str):
                return str(left) + str(right)
            raise LoxRuntimeError(
                expr.operator, "Operands must be two numbers or two strings."
            )
        elif expr.operator.ttype == LoxTokenType.GREATER:
            self.check_number_operands(expr.operator, left, right)
            return float(left) > float(right)
        elif expr.operator.ttype == LoxTokenType.GREATER_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return float(left) >= float(right)
        elif expr.operator.ttype == LoxTokenType.LESS:
            self.check_number_operands(expr.operator, left, right)
            return float(left) < float(right)
        elif expr.operator.ttype == LoxTokenType.LESS_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return float(left) <= float(right)
        elif expr.operator.ttype == LoxTokenType.BANG_EQUAL:
            return not self.is_equal(left, right)
        elif expr.operator.ttype == LoxTokenType.EQUAL_EQUAL:
            return self.is_equal(left, right)

    def visit_call_expr(self, expr):
        callee = self.evaluate(expr.callee)

        if not hasattr(callee, "call"):
            raise LoxRuntimeError(expr.paren, "Can only call functions and classes.")

        arguments = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))

        if not len(arguments) == callee.arity():
            raise LoxRuntimeError(
                expr.paren,
                f"Expected {callee.arity()} arguments but got {len(arguments)}.",
            )

        return callee.call(self, arguments)

    def is_truthy(self, value):
        if value is None:
            return False

        if isinstance(value, bool):
            return bool(value)

        return True

    def is_equal(self, a, b):
        return a == b

    def check_number_operand(self, operator, operand):
        if isinstance(operand, float):
            return

        raise LoxRuntimeError(operator, "Operand must be a number.")

    def check_number_operands(self, operator, left, right):
        if isinstance(left, float) and isinstance(right, float):
            return

        raise LoxRuntimeError(operator, "Operands must be numbers.")

    def stringify(self, value):
        if value is None:
            return "nil"

        if isinstance(value, float):
            text = str(value)
            if text.endswith(".0"):
                text = text[: len(text) - 2]
            return text

        if isinstance(value, bool):
            return str(value).lower()

        return str(value)

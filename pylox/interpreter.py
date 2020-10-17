from lox_token_type import LoxTokenType
from lox_runtime_error import LoxRuntimeError


class Interpreter:
    def interpret(self, expr):
        try:
            value = self.evaluate(expr)
            print(self.stringify(value))
        except LoxRuntimeError as error:
            from lox import Lox

            Lox.runtime_error(error)

    def evaluate(self, expr):
        return expr.accept(self)

    def visit_literal_expr(self, expr):
        return expr.value

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

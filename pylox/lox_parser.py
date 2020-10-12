from lox_token_type import LoxTokenType
from lox_expr import BinaryExpr, UnaryExpr, GroupingExpr, LiteralExpr


class LoxParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        try:
            return self.expression()
        except SyntaxError:
            return None

    def expression(self):
        return self.equality()

    def equality(self):
        expr = self.comparison()

        while self.match(LoxTokenType.BANG_EQUAL, LoxTokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = BinaryExpr(left=expr, operator=operator, right=right)

        return expr

    def comparison(self):
        expr = self.term()

        while self.match(
            LoxTokenType.GREATER,
            LoxTokenType.GREATER_EQUAL,
            LoxTokenType.LESS,
            LoxTokenType.LESS_EQUAL,
        ):
            operator = self.previous()
            right = self.term()
            expr = BinaryExpr(left=expr, operator=operator, right=right)

        return expr

    def term(self):
        expr = self.factor()

        while self.match(LoxTokenType.MINUS, LoxTokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = BinaryExpr(left=expr, operator=operator, right=right)

        return expr

    def factor(self):
        expr = self.unary()

        while self.match(LoxTokenType.SLASH, LoxTokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = BinaryExpr(left=expr, operator=operator, right=right)

        return expr

    def unary(self):
        if self.match(LoxTokenType.BANG, LoxTokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return UnaryExpr(operator=operator, right=right)

        return self.primary()

    def primary(self):
        if self.match(LoxTokenType.FALSE):
            return LiteralExpr(value=False)

        if self.match(LoxTokenType.TRUE):
            return LiteralExpr(value=True)

        if self.match(LoxTokenType.NIL):
            return LiteralExpr(value=None)

        if self.match(LoxTokenType.NUMBER, LoxTokenType.STRING):
            return LiteralExpr(value=self.previous().literal)

        if self.match(LoxTokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(LoxTokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return GroupingExpr(expr)

        raise self.error(self.peek(), "Expect expression.")

    def match(self, *ttypes):
        for ttype in ttypes:
            if self.check(ttype):
                self.advance()
                return True

        return False

    def consume(self, ttype, message):
        if self.check(ttype):
            return self.advance()

        raise self.error(self.peek(), message)

    def error(self, token, message):
        from lox import Lox

        Lox.token_error(token, message)
        return SyntaxError()

    def synchronize(self):
        self.advance()

        while not self.is_at_end():
            if self.previous().ttype == LoxTokenType.SEMICOLON:
                return

            if (
                self.peek().ttype == LoxTokenType.CLASS
                or self.peek().ttype == LoxTokenType.FUN
                or self.peek().ttype == LoxTokenType.VAR
                or self.peek().ttype == LoxTokenType.FOR
                or self.peek().ttype == LoxTokenType.IF
                or self.peek().ttype == LoxTokenType.WHILE
                or self.peek().ttype == LoxTokenType.PRINT
                or self.peek().ttype == LoxTokenType.RETURN
            ):
                return

            self.advance()

    def check(self, ttype):
        if self.is_at_end():
            return False

        return self.peek().ttype == ttype

    def advance(self):
        if not self.is_at_end():
            self.current = self.current + 1

        return self.previous()

    def is_at_end(self):
        return self.peek().ttype == LoxTokenType.EOF

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

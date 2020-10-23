from lox_token_type import LoxTokenType
from lox_runtime_error import LoxRuntimeError
from lox_ast import (
    AssignExpr,
    BinaryExpr,
    CallExpr,
    UnaryExpr,
    GroupingExpr,
    LiteralExpr,
    LogicalExpr,
    VariableExpr,
    BlockStmt,
    IfStmt,
    PrintStmt,
    ReturnStmt,
    ExpressionStmt,
    FunctionStmt,
    VarStmt,
    WhileStmt,
)


class LoxParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())

        return statements

    def declaration(self):
        try:
            if self.match(LoxTokenType.VAR):
                return self.var_declaration()
            elif self.match(LoxTokenType.FUN):
                return self.function("function")

            return self.statement()
        except LoxRuntimeError as error:
            self.synchronize()
            return None

    def statement(self):
        if self.match(LoxTokenType.FOR):
            return self.for_statement()
        elif self.match(LoxTokenType.IF):
            return self.if_statement()
        elif self.match(LoxTokenType.PRINT):
            return self.print_statement()
        elif self.match(LoxTokenType.RETURN):
            return self.return_statement()
        elif self.match(LoxTokenType.WHILE):
            return self.while_statement()
        elif self.match(LoxTokenType.LEFT_BRACE):
            return BlockStmt(statements=self.block_statement())

        return self.expression_statement()

    def for_statement(self):
        self.consume(LoxTokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        if self.match(LoxTokenType.SEMICOLON):
            initializer = None
        elif self.match(LoxTokenType.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()

        condition = None
        if not self.check(LoxTokenType.SEMICOLON):
            condition = self.expression()

        self.consume(LoxTokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment = None
        if not self.check(LoxTokenType.RIGHT_PAREN):
            increment = self.expression()

        self.consume(LoxTokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        body = self.statement()

        if increment is not None:
            body = BlockStmt(statements=[body, ExpressionStmt(expression=increment)])

        if condition is None:
            condition = LiteralExpr(value=True)

        body = WhileStmt(condition=condition, body=body)

        if initializer is not None:
            body = BlockStmt(statements=[initializer, body])

        return body

    def if_statement(self):
        self.consume(LoxTokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(LoxTokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        then_branch = self.statement()
        else_branch = None

        if self.match(LoxTokenType.ELSE):
            else_branch = self.statement()

        return IfStmt(
            condition=condition, then_branch=then_branch, else_branch=else_branch
        )

    def print_statement(self):
        value = self.expression()
        self.consume(LoxTokenType.SEMICOLON, "Expect ';' after value.")
        return PrintStmt(expression=value)

    def return_statement(self):
        keyword = self.previous()
        value = None

        if not self.check(LoxTokenType.SEMICOLON):
            value = self.expression()

        self.consume(LoxTokenType.SEMICOLON, "Expect ';' after return value.")

        return ReturnStmt(keyword=keyword, value=value)

    def var_declaration(self):
        name = self.consume(LoxTokenType.IDENTIFIER, "Expect variable name.")

        initializer = None
        if self.match(LoxTokenType.EQUAL):
            initializer = self.expression()

        self.consume(LoxTokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return VarStmt(name=name, initializer=initializer)

    def while_statement(self):
        self.consume(LoxTokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(LoxTokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body = self.statement()

        return WhileStmt(condition=condition, body=body)

    def expression_statement(self):
        expr = self.expression()
        self.consume(LoxTokenType.SEMICOLON, "Expect ';' after expression.")
        return ExpressionStmt(expression=expr)

    def function(self, kind):
        name = self.consume(LoxTokenType.IDENTIFIER, f"Expect {kind} name.")
        self.consume(LoxTokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters = []

        if not self.check(LoxTokenType.RIGHT_PAREN):
            matched = True
            while matched:
                if len(parameters) >= 255:
                    self.error(self.peek(), "Can't have more than 255 parameters.")

                parameters.append(
                    self.consume(LoxTokenType.IDENTIFIER, "Expect parameter name.")
                )

                matched = self.match(LoxTokenType.COMMA)

        self.consume(LoxTokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self.consume(LoxTokenType.LEFT_BRACE, "Expect '{' before " + kind + " body.")

        body = self.block_statement()
        return FunctionStmt(name=name, params=parameters, body=body)

    def block_statement(self):
        statements = []
        while not self.check(LoxTokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())

        self.consume(LoxTokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def expression(self):
        return self.assignment()

    def assignment(self):
        expr = self.or_()

        if self.match(LoxTokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, VariableExpr):
                name = expr.name
                return AssignExpr(name=name, value=value)

            self.error(equals, "Invalid assignment target.")

        return expr

    def or_(self):
        expr = self.and_()

        while self.match(LoxTokenType.OR):
            operator = self.previous()
            right = self.and_()
            expr = LogicalExpr(left=expr, operator=operator, right=right)

        return expr

    def and_(self):
        expr = self.equality()

        while self.match(LoxTokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = LogicalExpr(left=expr, operator=operator, right=right)

        return expr

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

        return self.call()

    def call(self):
        expr = self.primary()

        while True:
            if self.match(LoxTokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            else:
                break

        return expr

    def finish_call(self, callee):
        arguments = []

        if not self.check(LoxTokenType.RIGHT_PAREN):
            arguments.append(self.expression())
            while self.match(LoxTokenType.COMMA):
                if len(arguments) >= 255:
                    self.error(self.peek(), "Can't have more than 255 arguments.")

                arguments.append(self.expression())

        paren = self.consume(LoxTokenType.RIGHT_PAREN, "Expect ')' after arguments.")

        return CallExpr(callee=callee, paren=paren, arguments=arguments)

    def primary(self):
        if self.match(LoxTokenType.FALSE):
            return LiteralExpr(value=False)

        if self.match(LoxTokenType.TRUE):
            return LiteralExpr(value=True)

        if self.match(LoxTokenType.NIL):
            return LiteralExpr(value=None)

        if self.match(LoxTokenType.NUMBER, LoxTokenType.STRING):
            return LiteralExpr(value=self.previous().literal)

        if self.match(LoxTokenType.IDENTIFIER):
            return VariableExpr(name=self.previous())

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

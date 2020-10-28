from enum import Enum, auto


class FunctionType(Enum):
    NONE = auto()
    FUNCTION = auto()


class Resolver:
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.scopes = []
        self.current_function = FunctionType.NONE

    def visit_block_stmt(self, stmt):
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()

    def visit_expression_stmt(self, stmt):
        self.resolve_expr(stmt.expression)

    def visit_function_stmt(self, stmt):
        self.declare(stmt.name)
        self.define(stmt.name)

        self.resolve_function(stmt, FunctionType.FUNCTION)

    def visit_if_stmt(self, stmt):
        self.resolve_expr(stmt.condition)
        self.resolve_stmt(stmt.then_branch)

        if stmt.else_branch is not None:
            self.resolve_stmt(stmt.else_branch)

    def visit_print_stmt(self, stmt):
        self.resolve_expr(stmt.expression)

    def visit_return_stmt(self, stmt):
        if self.current_function == FunctionType.NONE:
            from lox import Lox

            Lox.error(stmt.keyword, "Can't return from toplevel code.")

        if stmt.value is not None:
            self.resolve_expr(stmt.value)

    def visit_var_stmt(self, stmt):
        self.declare(stmt.name)

        if stmt.initializer is not None:
            self.resolve_expr(stmt.initializer)

        self.define(stmt.name)

    def visit_while_stmt(self, stmt):
        self.resolve_expr(stmt.condition)
        self.resolve_stmt(stmt.body)

    def visit_assign_expr(self, expr):
        self.resolve_expr(expr.value)
        self.resolve_local(expr, expr.name)

    def visit_binary_expr(self, expr):
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)

    def visit_call_expr(self, expr):
        self.resolve_expr(expr.callee)

        for argument in expr.arguments:
            self.resolve_expr(argument)

    def visit_grouping_expr(self, expr):
        self.resolve_expr(expr.expression)

    def visit_literal_expr(self, expr):
        return

    def visit_logical_expr(self, expr):
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)

    def visit_unary_expr(self, expr):
        self.resolve_expr(expr.right)

    def visit_variable_expr(self, expr):
        if len(self.scopes) > 0 and self.scopes[-1].get(expr.name.lexeme) is False:
            from lox import Lox

            Lox.error(expr.name, "Can't read local variable in its own initializer.")

        self.resolve_local(expr, expr.name)

    def resolve(self, statements):
        for stmt in statements:
            self.resolve_stmt(stmt)

    def resolve_stmt(self, stmt):
        stmt.accept(self)

    def resolve_expr(self, expr):
        expr.accept(self)

    def resolve_function(self, function, fntype):
        enclosing_function = self.current_function
        self.current_function = fntype

        self.begin_scope()

        for param in function.params:
            self.declare(param)
            self.define(param)

        self.resolve(function.body)
        self.end_scope()

        self.current_function = enclosing_function

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name):
        if len(self.scopes) == 0:
            return

        scope = self.scopes[-1]

        if name in scope:
            from lox import Lox

            Lox.error(name, "Variable with this name already exists in this scope.")

        scope[name.lexeme] = False

    def define(self, name):
        if len(self.scopes) == 0:
            return

        self.scopes[-1][name.lexeme] = True

    def resolve_local(self, expr, name):
        for i in range(len(self.scopes) - 1, -1, -1):
            if name.lexeme in self.scopes[i]:
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)

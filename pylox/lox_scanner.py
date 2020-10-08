import re
from lox_token_type import LoxTokenType
from lox_token import LoxToken


IS_DIGIT_REGEX = re.compile("[0-9]")


class LoxScanner:
    def __init__(self, source):
        self.source = source
        self.tokens = []

        # start is the beginning of the token we're scanning. current
        # is the end of the token we're scanning. Taken together, they
        # form a sort of selection area. We keep start constant and
        # increment current for as long as we can recognize the next
        # character. When we can't recognize the next character
        # anymore, we assume that the text from start to current forms
        # a lexeme. We create a token from this, move current forward
        # so that it aligns with start once again, and attempt to
        # identify the next token.
        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(LoxToken(LoxTokenType.EOF, "", None, self.line))
        return self.tokens

    def is_at_end(self):
        return self.current >= len(self.source)

    def scan_token(self):
        c = self.advance()

        if c == "(":
            self.add_token(LoxTokenType.LEFT_PAREN)
        elif c == ")":
            self.add_token(LoxTokenType.RIGHT_PAREN)
        elif c == "{":
            self.add_token(LoxTokenType.LEFT_BRACE)
        elif c == "}":
            self.add_token(LoxTokenType.RIGHT_BRACE)
        elif c == ",":
            self.add_token(LoxTokenType.COMMA)
        elif c == ".":
            self.add_token(LoxTokenType.DOT)
        elif c == "-":
            self.add_token(LoxTokenType.MINUS)
        elif c == "+":
            self.add_token(LoxTokenType.PLUS)
        elif c == ";":
            self.add_token(LoxTokenType.SEMICOLON)
        elif c == "*":
            self.add_token(LoxTokenType.STAR)
        elif c == "!":
            if self.match("="):
                self.add_token(LoxTokenType.BANG_EQUAL)
            else:
                self.add_token(LoxTokenType.BANG)
        elif c == "=":
            if self.match("="):
                self.add_token(LoxTokenType.EQUAL_EQUAL)
            else:
                self.add_token(LoxTokenType.EQUAL)
        elif c == "<":
            if self.match("="):
                self.add_token(LoxTokenType.LESS_EQUAL)
            else:
                self.add_token(LoxTokenType.LESS)
        elif c == ">":
            if self.match("="):
                self.add_token(LoxTokenType.GREATER_EQUAL)
            else:
                self.add_token(LoxTokenType.GREATER)
        elif c == "/":
            if self.match("/"):
                while self.peek() != "\n" and not self.is_at_end():
                    self.advance()
            else:
                self.add_token(LoxTokenType.SLASH)
        elif c == '"':
            self.string()
        elif c == " " or c == "\r" or c == "\t":
            pass
        elif c == "\n":
            self.line = self.line + 1
        else:
            if self.is_digit(c):
                self.number()
            else:
                from lox import Lox

                Lox.error(self.line, f'Unexpected character "{c}".')

    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == "\n":
                self.line = self.line + 1
            self.advance()

        if self.is_at_end():
            from lox import Lox

            Lox.error(self.line, "Unterminated string.")
            return

        # Consume the closing quote.
        self.advance()

        value = self.source[self.start + 1 : self.current - 1]
        self.add_token(LoxTokenType.STRING, value)

    def number(self):
        while self.is_digit(self.peek()):
            self.advance()

        if self.peek() == "." and self.is_digit(self.peek_next()):
            self.advance()

        while self.is_digit(self.peek()):
            self.advance()

        self.add_token(
            LoxTokenType.NUMBER, float(self.source[self.start : self.current])
        )

    def is_digit(self, c):
        return re.match(IS_DIGIT_REGEX, c) is not None

    def match(self, expected):
        if self.is_at_end():
            return False

        if self.source[self.current] != expected:
            return False

        self.current = self.current + 1
        return True

    def peek(self):
        if self.is_at_end():
            return "\0"

        return self.source[self.current]

    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return "\0"

        return self.source[self.current + 1]

    def advance(self):
        self.current = self.current + 1
        return self.source[self.current - 1]

    def add_token(self, ttype, literal=None):
        text = self.source[self.start : self.current]
        token = LoxToken(ttype, text, literal, self.line)
        self.tokens.append(token)

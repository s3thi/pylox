class Token:
    def __init__(self, ttype, lexeme, literal, line):
        self.ttype = ttype
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self):
        s = f"<{self.ttype.name}"

        if len(self.lexeme) > 0:
            s = s + f", {self.lexeme}"

        if self.literal is not None:
            s = s + f", {self.literal}"

        s = s + ">"
        return s

        # return f"Token<type: {self.ttype}, lexeme:{self.lexeme} literal:{self.literal}>"

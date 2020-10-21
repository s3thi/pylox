import sys
from lox_scanner import LoxScanner
from lox_parser import LoxParser
from lox_token_type import LoxTokenType
from interpreter import Interpreter
from ast_printer import ASTPrinter


class Lox:
    @classmethod
    def main(cls):
        cls.interpreter = Interpreter()
        cls.had_error = False
        cls.had_runtime_error = False

        if len(sys.argv) > 2:
            print("Usage: pylox [script]")
            sys.exit(64)
        elif len(sys.argv) == 2:
            cls.run_file(sys.argv[1])
        else:
            cls.run_prompt()

    @classmethod
    def run_file(cls, filename):
        with open(filename) as f:
            cls.run(f.read())

        if cls.had_error:
            sys.exit(65)

        if cls.had_runtime_error:
            sys.exit(70)

    @classmethod
    def run_prompt(cls):
        import readline

        while True:
            try:
                line = input("lox>> ")
                cls.run(line)
                cls.had_error = False
            except EOFError:
                print("\nGoodbye!")
                sys.exit(0)

    @classmethod
    def run(cls, source):
        s = LoxScanner(source)
        tokens = s.scan_tokens()
        parser = LoxParser(tokens)
        statements = parser.parse()

        if cls.had_error:
            return

        cls.interpreter.interpret(statements)

    @classmethod
    def error(cls, line, message):
        cls.report(line, "", message)

    @classmethod
    def token_error(cls, token, message):
        if token.ttype == LoxTokenType.EOF:
            cls.report(token.line, " at end", message)
        else:
            cls.report(token.line, " at '" + token.lexeme + "'", message)

    @classmethod
    def runtime_error(cls, error):
        print(f"{error.message}\n[line {error.token.line}]")
        cls.had_runtime_error = True

    @classmethod
    def report(cls, line, where, message):
        print(f"[line {line}] Error {where}: {message}")
        cls.had_error = True


if __name__ == "__main__":
    Lox.main()

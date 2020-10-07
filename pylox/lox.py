import sys

from scanner import Scanner


class Lox:
    def __init__(self):
        self.had_error = False
    
    def main(self):
        if len(sys.argv) > 2:
            print("Usage: pylox [script]")
            sys.exit(64)
        elif len(sys.argv) == 2:
            self.run_file(sys.argv[1])
        else:
            self.run_prompt()

    def run_file(self, filename):
        with open(filename) as f:
            self.run(f.read())

        if self.had_error:
            sys.exit(65)

    def run_prompt(self):
        import readline

        while True:
            try:
                line = input("lox>> ")
                self.run(line)
                self.had_error = False
            except EOFError:
                print("\nGoodbye!")
                sys.exit(0)

    def run(self, source):
        s = Scanner(source)
        tokens = s.scan_tokens()

        for token in tokens:
            print(token)

    def error(self, line, message):
        self.report(line, "", message)

    def report(self, line, where, message):
        print(f"[line {line}] Error {where}: {message}")
        self.had_error = True


if __name__ == "__main__":
    lox = Lox()
    lox.main()

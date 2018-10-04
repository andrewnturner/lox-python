import sys

from scanner import Scanner
from parser import Parser
from ast_printer import AstPrinter
from token_type import TokenType
from interpreter import Interpreter
from resolver import Resolver

DEBUG = False

class Lox():
    def __init__(self):
        self.interpreter = Interpreter(self)
        
        self.had_error = False
        self.had_runtime_error = False

    def run_file(self, path: str):
        with open(path, 'r') as f:
            source = f.read();

        self.run(source)
        
        if self.had_error:
            sys.exit(65)

        if self.had_runtime_error:
            sys.exit(70)

    def run_prompt(self):
        while True:
            line = input('> ')
            self.run(line)

            self.had_error = False

    def run(self, source: str):
        scanner = Scanner(self, source)
        tokens = scanner.scan_tokens()
        
        if DEBUG:
            print(tokens)

        parser = Parser(self, tokens)
        statements = parser.parse()

        if self.had_error:
            return

        resolver = Resolver(self, self.interpreter)
        resolver.resolve_statements(statements)

        if self.had_error:
            return

        self.interpreter.interpret(statements)

    def error(self, line: int, message: str):
        self.report(line, "", message)

    def report(self, line:int, where: str, message:str):
        print(f'[{line}] Error{where}: {message}')
        self.had_error = True

    def syntax_error(self, token, message):
        if token.token_type == TokenType.EOF:
            self.report(token.line, ' at end', message)
        else:
            self.report(token.line, f" at '{token.lexeme}'", message)

    def runtime_error(self, e):
        message = str(e)
        print(f"[{e.token.line}] RunTimeError: {message}")
        self.had_runtime_error = True
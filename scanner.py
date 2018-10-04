from token_type import TokenType
from token import Token

class Scanner():
    KEYWORDS = {
        'and': TokenType.AND,
        'class': TokenType.CLASS,
        'else': TokenType.ELSE,
        'false': TokenType.FALSE,
        'for': TokenType.FOR,
        'fun': TokenType.FUN,
        'if': TokenType.IF,
        'nil': TokenType.NIL,
        'or': TokenType.OR,
        'print': TokenType.PRINT,
        'return': TokenType.RETURN,
        'super': TokenType.SUPER,
        'this': TokenType.THIS,
        'true': TokenType.TRUE,
        'var': TokenType.VAR,
        'while': TokenType.WHILE,
    }

    def __init__(self, lox, source: str):
        self.lox = lox
        self.source = source

        self.tokens = []
        
        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current;
            self.scan_token()
        
        self.tokens.append(Token(TokenType.EOF, '', None, self.line))

        return self.tokens

    def scan_token(self):
        c = self.advance()

        actions = {
            '(': lambda: self.add_token(TokenType.LEFT_PAREN),
            ')': lambda: self.add_token(TokenType.RIGHT_PAREN),
            '{': lambda: self.add_token(TokenType.LEFT_BRACE),
            '}': lambda: self.add_token(TokenType.RIGHT_BRACE),
            ',': lambda: self.add_token(TokenType.COMMA),
            '.': lambda: self.add_token(TokenType.DOT),
            '-': lambda: self.add_token(TokenType.MINUS),
            '+': lambda: self.add_token(TokenType.PLUS),
            ';': lambda: self.add_token(TokenType.SEMICOLON),
            '*': lambda: self.add_token(TokenType.STAR),
            '!': lambda: self.add_token(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG),
            '=': lambda: self.add_token(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL),
            '<': lambda: self.add_token(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS),
            '>': lambda: self.add_token(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER),
            '/': self.on_slash,
            ' ': lambda: None,
            '\r': lambda: None,
            '\t': lambda: None,
            '\n': self.on_new_line,
            '"': self.string
        }
        try:
            actions[c]()
        except KeyError:
            if self.is_digit(c):
                self.number()
            elif self.is_alpha(c):
                self.identifier()
            else:
                self.lox.error(self.line, f'Invalid character: {c}')

    def advance(self):
        c = self.source[self.current]

        self.current += 1

        return c

    def peek(self):
        if self.is_at_end():
            return '\0'
        
        return self.source[self.current]

    def add_token(self, token_type:TokenType, literal=None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))

    def is_at_end(self):
        return self.current >= len(self.source)

    def match(self, expected:str):
        if self.is_at_end():
            return False

        if self.source[self.current] != expected:
            return False

        self.current += 1

        return True

    def on_slash(self):
        if self.match('/'):
            while (self.peek() != '\n') and (not self.is_at_end()):
                self.advance()
        else:
            self.add_token(TokenType.SLASH)

    def on_new_line(self):
        self.line += 1

    def string(self):
        while  (self.peek() != '"') and (not self.is_at_end()):
            if self.peek() == '\n':
                self.line += 1
            self.advance()

        if self.is_at_end():
            self.lox.error(self.line, "Unterminated string")
            return

        self.advance()

        value = self.source[self.start+1:self.current-1]
        self.add_token(TokenType.STRING, value)

    def is_digit(self, c: str):
        return (c in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])

    def number(self):
        while self.is_digit(self.peek()):
            self.advance()

        if (self.peek() == '.') and (self.is_digit(self.peek_next())):
            self.advance()

            while self.is_digit(self.peek()):
                self.advance()

        value = float(self.source[self.start:self.current])
        self.add_token(TokenType.NUMBER, value)

    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return '\0'
        
        return self.source[self.current + 1]

    def is_alpha(self, c: str):
        return c.isalpha() or (c == '_')

    def is_alphanumeric(self, c:str):
        return self.is_alpha(c) or self.is_digit(c)

    def identifier(self):
        while self.is_alphanumeric(self.peek()):
            self.advance()

        text = self.source[self.start:self.current]

        try:
            token_type = self.KEYWORDS[text]
        except KeyError:
            token_type = TokenType.IDENTIFIER
        
        self.add_token(token_type)
    
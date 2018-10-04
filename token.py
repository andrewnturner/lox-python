from token_type import TokenType

class Token():
    def __init__(self, token_type:TokenType, lexeme:str, literal, line:int):
        self.token_type = token_type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __repr__(self):
        return f'<{self.token_type} {self.lexeme} {self.literal}>'
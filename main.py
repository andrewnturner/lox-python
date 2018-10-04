from expression import *
from token import Token
from token_type import TokenType
from ast_printer import AstPrinter

expr = Binary(
    Unary(
        Token(TokenType.MINUS, '-', None, 1),
        Literal(123)
    ),
    Token(TokenType.STAR, '*', None, 1),
    Grouping(
        Literal(45.67)
    )
)

ast_printer = AstPrinter()
print(ast_printer.print(expr))
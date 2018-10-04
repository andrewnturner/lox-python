from expression_visitor import ExpressionVisitor

class AstPrinter(ExpressionVisitor):
    def print(self, expr):
        return expr.accept(self)
    
    def visit_binary(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping(self, expr):
        return self.parenthesize('group', expr.expression)

    def visit_literal(self, expr):
        if expr.value is None:
            return 'nil'
        return str(expr.value)

    def visit_unary(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def parenthesize(self, name, *exprs):
        expr_strings = [expr.accept(self) for expr in exprs]
        exprs_string = ' '.join(expr_strings)
        return f'({name} ' + exprs_string + ')'
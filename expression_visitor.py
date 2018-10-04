class ExpressionVisitor():
    def visit(self, expr):
        expr.accept(self)

    def visit_binary(self, expr):
        raise NotImplemented

    def visit_grouping(self, expr):
        raise NotImplemented

    def visit_literal(self, expr):
        raise NotImplemented

    def visit_unary(self, expr):
        raise NotImplemented
    

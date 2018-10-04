class StatementVisitor():
    def visit(self, stmt):
        stmt.accept(self)

    def visit_print_statement(self, stmt):
        raise NotImplemented

    def visit_expression_statement(self, stmt):
        raise NotImplemented
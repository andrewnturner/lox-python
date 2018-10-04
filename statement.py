class Statement():
    def accept(self, visitor):
        raise NotImplemented

class ExpressionStatement(Statement):
    def __init__(self, expression):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_expression_statement(self)

class PrintStatement(Statement):
    def __init__(self, expression):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_print_statement(self)

class VarStatement(Statement):
    def __init__(self, name, initializer):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor):
        visitor.visit_var_statement(self)

class BlockStatement(Statement):
    def __init__(self, statements):
        self.statements = statements

    def accept(self, visitor):
        visitor.visit_block_statement(self)

class IfStatement(Statement):
    def __init__(self, condition, then_branch, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor):
        visitor.visit_if_statement(self)

class WhileStatement(Statement):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def accept(self, visitor):
        visitor.visit_while_statement(self)

class FunctionStatement(Statement):
    def __init__(self, name, parameters, body):
        self.name = name
        self.parameters = parameters
        self.body = body

    def accept(self, visitor):
        visitor.visit_function_statement(self)

class ReturnStatement(Statement):
    def __init__(self, keyword, value):
        self.keyword = keyword
        self.value = value

    def accept(self, visitor):
        visitor.visit_return_statement(self) 

class ClassStatement(Statement):
    def __init__(self, name, superclass, methods):
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def accept(self, visitor):
        visitor.visit_class_statement(self) 



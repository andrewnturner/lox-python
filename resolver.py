from function_type import FunctionType
from class_type import ClassType
from expression_visitor import ExpressionVisitor
from statement_visitor import StatementVisitor

class Resolver(ExpressionVisitor, StatementVisitor):
    def __init__(self, lox, interpreter):
        self.lox = lox
        self.interpreter = interpreter

        self.scopes = []
        self.current_function = FunctionType.NONE
        self.current_class = ClassType.NONE

    def resolve_statements(self, statements):
        for statement in statements:
            self.resolve_statement(statement)

    def resolve_statement(self, stmt):
        stmt.accept(self)

    def resolve_expression(self, expr):
        expr.accept(self)

    def resolve_local(self, expr, name):
        for i in range(len(self.scopes), 0, -1):
            if name.lexeme in self.scopes[i-1]:
                self.interpreter.resolve(expr, len(self.scopes) - i)

    def resolve_function(self, function, function_type):
        enclosing_function = self.current_function
        self.current_function = function_type
        
        self.begin_scope()

        for parameter in function.parameters:
            self.declare(parameter)
            self.define(parameter)

        self.resolve_statements(function.body)

        self.end_scope()

        self.current_function = enclosing_function

    def declare(self, name):
        if len(self.scopes) == 0:
            return

        scope = self.scopes[-1]

        if name.lexeme in scope:
            self.lox.error(name, "variable with this name already declared in this scope")

        scope[name.lexeme] = False
    
    def define(self, name):
        if len(self.scopes) == 0:
            return

        scope = self.scopes[-1]
        scope[name.lexeme] = True

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def visit_block_statement(self, stmt):
        self.begin_scope()
        self.resolve_statements(stmt.statements)
        self.endScope()

    def visit_var_statement(self, stmt):
        self.declare(stmt.name)
        
        if stmt.initializer is not None:
            self.resolve_statement(stmt.initializer)

        self.define(stmt.name)

    def visit_variable(self, expr):
        if len(self.scopes) > 0:
            scope = self.scopes[-1]
            if scope.get(expr.name.lexeme, None) == False:
                self.lox.error(expr.name, "Cannot read local variable in its own initializer")
    
        self.resolve_local(expr, expr.name)

    def visit_assign(self, expr):
        self.resolve_expression(expr.value)
        self.resolve_local(expr, expr.name)

    def visit_function_statement(self, stmt):
        self.declare(stmt.name)
        self.define(stmt.name)

        self.resolve_function(stmt, FunctionType.FUNCTION)

    def visit_expression_statement(self, stmt):
        self.resolve_expression(stmt.expression)

    def visit_if_statement(self, stmt):
        self.resolve_statement(stmt.condition)
        self.resolve_statement(stmt.then_branch)
        
        if stmt.else_branch is not None:
            self.resolve_statement(stmt.else_branch)

    def visit_print_statement(self, stmt):
        self.resolve_expression(stmt.expression)

    def visit_return_statement(self, stmt):
        if self.current_function == FunctionType.NONE:
            self.lox.error(stmt.keyword, "Cannot return from top-level code")

        if stmt.value is not None:
            if self.current_function == FunctionType.INITIALIZER:
                self.lox.error(stmt.keyword, "Cannot return a value from initializer")

            self.resolve_expression(stmt.value)

    def visit_while_statement(self, stmt):
        self.resolve_expression(stmt.condition)
        self.resolve_statement(stmt.body)

    def visit_class_statement(self, stmt):
        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS

        self.declare(stmt.name)

        if stmt.superclass is not None:
            self.current_class = ClassType.SUBCLASS
            self.resolve_statement(stmt.superclass)

        self.define(stmt.name)

        if stmt.superclass is not None:
            self.begin_scope()
            self.scopes[-1]['super'] = True

        self.begin_scope()
        self.scopes[-1]['this'] = True

        for method in stmt.methods:
            declaration = FunctionType.METHOD
            if method.name.lexeme == 'init':
                declaration = FunctionType.INITIALIZER
            self.resolve_function(method, declaration)

        self.end_scope()

        if stmt.superclass is not None:
            self.end_scope()

        self.current_class = enclosing_class

    def visit_binary(self, expr):
        self.resolve_expression(expr.left)
        self.resolve_expression(expr.right)

    def visit_call(self, expr):
        self.resolve_expression(expr.callee)

        for argument in expr.arguments:
            self.resolve_expression(argument)

    def visit_grouping(self, expr):
        self.resolve_expression(expr.expression)

    def visit_literal(self, expr):
        pass

    def visit_logical(self, expr):
        self.resolve_expression(expr.left)
        self.resolve_expression(expr.right)

    def visit_unary(self, expr):
        self.resolve_expression(expr.right)

    def visit_get(self, expr):
        self.resolve_expression(expr.obj)

    def visit_set(self, expr):
        self.resolve_expression(expr.value)
        self.resolve_expression(expr.obj)

    def visit_this(self, expr):
        if self.current_class == ClassType.NONE:
            self.lox.syntax_error(expr.keyword, "Cannot use 'this' outside a class")
            return

        self.resolve_local(expr, expr.keyword)

    def visit_super(self, expr):
        if self.current_class == ClassType.NONE:
            self.lox.syntax_error(expr.keyword, "Cannot use 'super' outside a class")
        elif not self.current_class == ClassType.SUBCLASS:
            self.lox.syntax_error(expr.keyword, "Cannot use 'super' in a class with no superclass")

        self.resolve_local(expr, expr.keyword)

    

    
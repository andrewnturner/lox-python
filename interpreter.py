from expression_visitor import ExpressionVisitor
from statement_visitor import StatementVisitor
from token_type import TokenType
from environment import Environment
from run_time_error import RunTimeError
from lox_callable import LoxCallable
from lox_builtins import *
from lox_function import LoxFunction, Return
from lox_class import LoxClass
from lox_instance import LoxInstance

class Interpreter(ExpressionVisitor, StatementVisitor):
    def __init__(self, lox):
        self.lox = lox

        self.globals = Environment()
        self.environment = self.globals

        self.globals.define("clock", Clock())

        self.locals = {}

    def interpret(self, statements):
        try:
            for statement in statements:
                self.execute(statement)
        except RunTimeError as e:
            self.lox.runtime_error(e)

    def execute(self, statement):
        statement.accept(self)

    def resolve(self, expr, depth):
        self.locals[expr] = depth

    def execute_block(self, statements, environment):
        previous = self.environment

        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def evaluate(self, expr):
        return expr.accept(self)

    def lookup_variable(self, name, expr):
        try:
            distance = self.locals[expr]
            return self.environment.get_at(distance, name.lexeme)
        except KeyError:
            return self.globals.get(name)

    def visit_binary(self, expr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        operator_type = expr.operator.token_type
        if operator_type == TokenType.MINUS:
            self.check_number_operands(expr.operator, left, right)
            return left - right
        elif operator_type == TokenType.PLUS:
            both_numbers = (isinstance(left, float) and isinstance(right, float))
            both_strings = (isinstance(left, str) and isinstance(right, str))
            
            if both_numbers or both_strings:
                return left + right
            
            raise RunTimeError(expr.operator, "Operands must be two numbers or two strings")
        elif operator_type == TokenType.SLASH:
            self.check_number_operands(expr.operator, left, right)
            return left / right
        elif operator_type == TokenType.STAR:
            self.check_number_operands(expr.operator, left, right)
            return left * right
        elif operator_type == TokenType.GREATER:
            self.check_number_operands(expr.operator, left, right)
            return left > right
        elif operator_type == TokenType.GREATER_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return left >= right
        elif operator_type == TokenType.LESS:
            self.check_number_operands(expr.operator, left, right)
            return left < right
        elif operator_type == TokenType.LESS_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return left <= right
        elif operator_type == TokenType.BANG_EQUAL:
            return not self.is_equal(left, right)
        elif operator_type == TokenType.EQUAL_EQUAL:
            return self.is_equal(left, right)

        raise Exception("Bad binary operator")

    def visit_grouping(self, expr):
        return self.evaluate(expr.expression)

    def visit_literal(self, expr):
        return expr.value

    def visit_unary(self, expr):
        right = self.evaluate(expr.right)

        if expr.operator.token_type == TokenType.MINUS:
            self.check_number_operand(expr.operator, right)
            return -right
        elif expr.operator.token_type == TokenType.BANG:
            return not self.is_truthy(right)

        raise Exception("Bad unary operator")

    def visit_variable(self, expr):
        return self.lookup_variable(expr.name, expr)

    def visit_assign(self, expr):
        value = self.evaluate(expr.value)

        try:
            distance = self.locals[expr]
            self.environment.assign_at(distance, expr.name, value)
        except KeyError:
            self.globals.assign(expr.name, value)

        return value

    def visit_logical(self, expr):
        left = self.evaluate(expr.left)

        if expr.operator.token_type == TokenType.OR:
            if self.is_truthy(left):
                return left
        elif expr.operator.token_type == TokenType.AND:
            if not self.is_truthy(left):
                return left
        else:
            raise Exception("Bad logical operator")

        return self.evaluate(expr.right)

    def visit_call(self, expr):
        callee = self.evaluate(expr.callee)

        arguments = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))

        if not isinstance(callee, LoxCallable):
            raise RunTimeError(expr.paren, "can only call functions and methods")
        
        if len(arguments) != callee.arity():
            raise RunTimeError(expr.paren, f"Expected {callee.arity()} arguments but got {len(arguments)}")

        return callee.call(self, arguments)

    def visit_get(self, expr):
        obj = self.evaluate(expr.obj)
        if isinstance(obj, LoxInstance):
            return obj.get(expr.name)

        raise RunTimeError("Only instance have properties")

    def visit_this(self, expr):
        return self.lookup_variable(expr.keyword, expr)

    def visit_set(self, expr):
        obj = self.evaluate(expr.obj)
        if not isinstance(obj, LoxInstance):
            raise RunTimeError("Only instances have fields")

        value = self.evaluate(expr.value)
        obj.set_field(expr.name, value)

    def visit_super(self, expr):
        distance = self.locals[expr]
        superclass = self.environment.get_at(distance, 'super')

        obj = self.environment.get_at(distance - 1, 'this')
        method = superclass.find_method(obj, expr.method.lexeme)

        if method is None:
            raise RunTimeError(expr.method, f"Undefined property '{expr.method}'")

        return method

    def visit_expression_statement(self, stmt):
        self.evaluate(stmt.expression)
        
        return None

    def visit_if_statement(self, stmt):
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)

    def visit_print_statement(self, stmt):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))

        return None

    def visit_return_statement(self, stmt):
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)

        raise Return(value)
    
    def visit_while_statement(self, stmt):
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)
        
        return None

    def visit_var_statement(self, stmt):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        
        self.environment.define(stmt.name.lexeme, value)

        return None

    def visit_block_statement(self, stmt):
        self.execute_block(stmt.statements, Environment(self.environment))

    def visit_class_statement(self, stmt):
        superclass = None
        if stmt.superclass is not None:
            superclass = self.evaluate(stmt.superclass)
            if not isinstance(superclass, LoxClass):
                raise RunTimeError("Superclass must be a class")

        self.environment.define(stmt.name.lexeme, None)

        if stmt.superclass is not None:
            self.environment = Environment(self.environment)
            self.environment.define('super', superclass)
        
        methods = {}
        for method in stmt.methods:
            is_initializer = (method.name.lexeme == 'init')
            function = LoxFunction(method, self.environment, is_initializer)
            methods[method.name.lexeme] = function
        
        klass = LoxClass(stmt.name.lexeme, superclass, methods)

        if superclass is not None:
            self.environment = self.environment.enclosing
        
        self.environment.assign(stmt.name, klass)

    def visit_function_statement(self, stmt):
        func = LoxFunction(stmt, self.environment, False)
        self.environment.define(stmt.name.lexeme, func)

        return None

    def is_truthy(self, obj):
        if obj is None:
            return False
        if obj is False:
            return False

        return True

    def is_equal(self, a, b):
        return a == b

    def check_number_operand(self, operator, operand):
        if isinstance(operand, float):
            return
        
        raise RunTimeError(operator, "Operand must be a number")

    def check_number_operands(self, operator, left, right):
        if isinstance(left, float) and isinstance(right, float):
            return
        
        raise RunTimeError(operator, "Operands must be numbers")

    def stringify(self, obj):
        if obj is None:
            return 'nil'

        if isinstance(obj, float):
            text = str(obj)
            if text.endswith('.0'):
                return text[:-2]
            return text

        return str(obj)

    


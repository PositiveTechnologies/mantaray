import logging

from mantaray.errors import MantarayError
from mantaray.symbolic_execution.contexts import GlobalContext, FunctionContext, StatementBlockContext, \
    ConditionalStatementContext, BranchContext
from mantaray.symbolic_execution.expressions import Literal, BinaryOperator, UnaryOperator

logger = logging.getLogger("symbolic_vm")


class SEEngine:
    def __init__(self, deepness):
        self.deepness = deepness
        self.current_context = GlobalContext()

    def conditionalize(self, symbolic_expression):
        return self.current_context.conditionalize(symbolic_expression)

    def try_enter_function(self, descriptor, arguments):
        arguments = map(lambda argument: self.conditionalize(argument), arguments)
        return self._try_enter_context(FunctionContext(self.current_context, descriptor, arguments))

    def leave_function(self):
        returned_value = self.conditionalize(self.current_context.returned_variable)
        self._leave_current_context(FunctionContext)
        return returned_value

    def create_variable(self, name, se_type):
        return self.current_context.create_variable(name, se_type)

    def get_variable_ref(self, name):
        return self.current_context.get_variable_ref(name)

    def create_literal(self, value, se_type):
        return Literal(value, se_type)

    def create_function_call(self, name, arguments):
        pass

    def process_assignment_expr(self, assignee, value):
        value = self.conditionalize(value)
        self.current_context.update_variable(assignee, value)
        return value

    def process_return_statement(self, value):
        value = self.conditionalize(value)
        self.current_context.process_return(value)

    def process_binary_operator(self, argument1, argument2, bop_type):
        argument1 = self.conditionalize(argument1)
        argument2 = self.conditionalize(argument2)
        return BinaryOperator(argument1, argument2, bop_type)

    def process_unary_operator(self, argument, op_type):
        argument = self.conditionalize(argument)
        return UnaryOperator(argument, op_type)

    def try_enter_statement_block(self):
        return self._try_enter_context(StatementBlockContext(self.current_context))

    def leave_statement_block(self):
        self._leave_current_context(StatementBlockContext)

    def try_enter_conditional_statement(self, condition):
        condition = self.conditionalize(condition)
        return self._try_enter_context(ConditionalStatementContext(self.current_context, condition))

    def leave_conditional_statement(self):
        self._leave_current_context(ConditionalStatementContext)

    def try_enter_branch(self, branching_context):
        return self._try_enter_context(branching_context)

    def leave_branch(self):
        self._leave_current_context(BranchContext)

    def _try_enter_context(self, context):
        if context.is_reachable:
            self.current_context = context
            return True

        return False

    def _leave_current_context(self, context_type):
        if not isinstance(self.current_context, context_type):
            raise MantarayError("Inconsistent context: {0}".format(self.current_context))

        self.current_context = self.current_context.leave()

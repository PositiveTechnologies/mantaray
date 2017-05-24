from abc import ABC

from mantaray.errors import MantarayNotImplemented
from mantaray.symbolic_execution.expressions import BinaryOperator, Conditional, Option, UnaryOperator


class SEVisitor(ABC):
    """ An abstract base class for visiting symbolic expression nodes.
    """

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.__generic_visit)
        return visitor(node)

    def visit_Variable(self, variable):
        return variable

    def visit_Conditional(self, conditional):
        visited_options = []

        for option in conditional.options:
            visited_option = Option(option.condition, self.visit(option.value))
            visited_options.append(visited_option)

        return Conditional(conditional.se_type, visited_options)

    def visit_Literal(self, literal):
        return literal

    def visit_BinaryOperator(self, binary_operator):
        argument1 = self.visit(binary_operator.argument1)
        argument2 = self.visit(binary_operator.argument2)
        return BinaryOperator(argument1, argument2, binary_operator.bop_type)

    def visit_UnaryOperator(self, unary_operator):
        argument = self.visit(unary_operator.argument)
        return UnaryOperator(argument, unary_operator.op_type)

    def __generic_visit(self, node):
        raise MantarayNotImplemented(type(node).__name__)

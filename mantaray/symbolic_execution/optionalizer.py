from mantaray.solving.solver import se_simplify, is_sat
from mantaray.symbolic_execution.expressions import Option, SE_TRUE, se_and, BinaryOperator, UnaryOperator
from mantaray.symbolic_execution.visitor import SEVisitor


class Optionalizer(SEVisitor):
    """ Transforms expression into a set of all its possible conditional options
    """
    def __init__(self):
        self.optionalize = self.visit

    def visit_Literal(self, literal):
        yield Option(SE_TRUE, literal)

    def visit_BinaryOperator(self, binary_operator):
        for argument1_option in self.optionalize(binary_operator.argument1):
            for argument2_option in self.optionalize(binary_operator.argument2):
                condition = se_and(argument1_option.condition, argument2_option.condition)
                value = BinaryOperator(argument1_option.value, argument2_option.value, binary_operator.bop_type)
                yield Option(condition, value)

    def visit_Variable(self, variable):
        yield Option(SE_TRUE, variable)

    def visit_Conditional(self, conditional):
        for option in conditional.options:
            value_options = self.optionalize(option.value)
            for value_option in value_options:
                yield Option(se_and(option.condition, value_option.condition), value_option.value)

    def visit_UnaryOperator(self, unary_operator):
        for argument_option in self.optionalize(unary_operator.argument):
            value = UnaryOperator(argument_option.value, unary_operator.op_type)
            yield Option(argument_option.condition, value)

optionalizer = Optionalizer()


def optionalize(s_expression):
    for option in optionalizer.optionalize(s_expression):
        simplified_condition = se_simplify(option.condition)
        simplified_value = se_simplify(option.value)
        if (is_sat(simplified_condition)):
            yield Option(simplified_condition, simplified_value)

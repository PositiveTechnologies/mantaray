import copy

from mantaray.symbolic_execution.expressions import Conditional
from mantaray.symbolic_execution.visitor import SEVisitor


class Conditionalizer(SEVisitor):
    """ Replaces all variables in given expression with their conditionals
    """
    def __init__(self, variables_options):
        self.conditionalize = self.visit
        self.variables_options = variables_options

    def visit_Variable(self, variable):
        if variable in self.variables_options:
            if self.variables_options[variable]:
                return Conditional(variable.se_type, copy.deepcopy(self.variables_options[variable]))
            return variable
        return variable

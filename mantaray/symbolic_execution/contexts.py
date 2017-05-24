import copy
import logging
import uuid
from abc import ABC

from mantaray.symbolic_execution.conditionalizer import Conditionalizer
from mantaray.errors import MantarayError
from mantaray.symbolic_execution.expressions import Variable, SE_TRUE, Option, se_and, se_not
from mantaray.utils import get_random_id

logger = logging.getLogger("context")


class SymbolicContext(ABC):
    """ Abstract base for all symbolic interpretation contexts
    """
    def __init__(self, outer_context):
        self.outer_context = outer_context
        self.id = uuid.uuid4().hex
        self.updated_variables = set()

        if outer_context is not None:
            self.condition = outer_context.condition
            self.variables_refs = copy.deepcopy(outer_context.variables_refs)
            self.variables_options = copy.deepcopy(outer_context.variables_options)
            self.is_reachable = outer_context.is_reachable
        else:
            self.condition = SE_TRUE
            self.variables_refs = {}
            self.variables_options = {}
            self.is_reachable = True

        self.conditionalizer = Conditionalizer(self.variables_options)

    def leave(self):
        """ Context leaving handler
        """
        for name, variable in self.outer_context.variables_refs.items():
            self.outer_context.variables_options[variable] = self.variables_options[variable]

            if variable in self.updated_variables:
                self.outer_context.updated_variables.add(variable)

        return self.outer_context

    def create_variable(self, name, se_type):
        """ Creates and registers new variable 
        """
        variable = Variable(self.id, name, se_type)
        self.variables_refs[name] = variable
        self.variables_options[variable] = []
        logger.info("Variable `{0} {1}` created".format(se_type, name))

        return variable

    def get_variable_ref(self, name):
        """ Returns a reference to existing variable by its name from the current context or the nearest outer one
        """
        variable_ref = self.variables_refs.get(name, None)

        if variable_ref is not None:
            return variable_ref

        raise MantarayError("Can not find variable: `{0}`".format(name))

    def update_variable(self, variable, value):
        """ Updates a scope of the variable for a new option
        """
        variable_options = self.variables_options[variable]

        for option in variable_options:
            if option.condition == self.condition:
                variable_options.remove(option)
            else:
                option.adjunct_condition(se_not(self.condition))

        option = Option(self.condition, value)
        variable_options.append(option)
        self.updated_variables.add(variable)
        logger.info("Value of the `{0}` variable updated for option `{1}`".format(variable, option))

    def conditionalize(self, symbolic_expression):
        return self.conditionalizer.conditionalize(symbolic_expression)

    def adjunct_condition(self, additional_condition, propagate=True):
        self.condition = se_and(self.condition, additional_condition)
        if propagate:
            self.outer_context.adjunct_condition(additional_condition)


class GlobalContext(SymbolicContext):
    def __init__(self):
        super().__init__(None)

    def adjunct_condition(self, *args):
        pass


class LocalContext(SymbolicContext, ABC):
    def __init__(self, outer_context):
        super().__init__(outer_context)
        if hasattr(outer_context, 'returned_variable'):
            self.returned_variable = outer_context.returned_variable

    def process_return(self, se_expression):
        self.update_variable(self.returned_variable, se_expression)
        self.adjunct_condition(se_not(self.condition))
        self.is_reachable = False


class FunctionContext(LocalContext):
    def __init__(self, outer_context, descriptor, arguments):
        super().__init__(outer_context)

        self.returned_variable = self.create_variable(get_random_id("__{0}_ret_".format(descriptor.name)),
                                                      descriptor.return_se_type)

        parameters = []

        for name, se_type in descriptor.parameters.items():
            parameters.append(self.create_variable(name, se_type))

        for parameter, argument in zip(parameters, arguments):
            self.update_variable(parameter, argument)

    def adjunct_condition(self, additional_condition, propagate=False):
        super().adjunct_condition(additional_condition, False)


class StatementBlockContext(LocalContext):
    def __init__(self, outer_context):
        super().__init__(outer_context)


class ConditionalStatementContext(LocalContext):
    def __init__(self, outer_context, statement_condition):
        super().__init__(outer_context)
        self.statement_condition = statement_condition
        self.if_true_context = BranchContext(self, statement_condition)
        self.if_false_context = BranchContext(self, se_not(statement_condition))

    def leave(self):
        rewritten_variables = \
            self.if_true_context.updated_variables.intersection(self.if_false_context.updated_variables)

        for variable in rewritten_variables:
            for option in self.variables_options[variable]:
                self.if_true_context.variables_options[variable].remove(option)
                self.if_false_context.variables_options[variable].remove(option)
                self.variables_options[variable].clear()

        updated_variables = self.if_true_context.updated_variables.union(self.if_false_context.updated_variables)

        for name, variable in self.variables_refs.items():
            self.variables_options[variable].extend(self.if_true_context.variables_options[variable] +
                                                    self.if_false_context.variables_options[variable])

            if variable in updated_variables:
                self.updated_variables.add(variable)

        return super().leave()


class BranchContext(LocalContext):
    def __init__(self, outer_context, statement_condition):
        super().__init__(outer_context)
        self.condition = se_and(self.condition, statement_condition)

    def leave(self):
        return self.outer_context

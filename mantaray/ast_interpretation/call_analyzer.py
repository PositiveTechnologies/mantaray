import logging

from pycparser import c_ast

from mantaray.symbolic_execution.type import SEType

logger = logging.getLogger("call_analyzer")


class FunctionDescriptor:
    def __init__(self, name, return_se_type, parameters, body):
        self.name = name
        self.return_se_type = return_se_type
        self.parameters = parameters
        self.body = body
        self.callees = set()

    def __str__(self):
        parameters_str = ", ".join(map(lambda se_type: se_type.value, self.parameters.values()))
        return "{0} {1}({2})".format(self.return_se_type, self.name, parameters_str)


class CallAnalyzer(c_ast.NodeVisitor):
    def __init__(self):
        self.functions = {}
        self._current_function = None

    def visit_FuncDef(self, function_definition):
        name = function_definition.decl.name
        return_se_type = SEType.get_from_ast(function_definition.decl.type.type)

        parameters = {}
        for parameters_decl in function_definition.decl.type.args.params:
            parameters[parameters_decl.name] = SEType.get_from_ast(parameters_decl.type)

        body = function_definition.body
        function_descriptor = FunctionDescriptor(name, return_se_type, parameters, body)
        self.functions[name] = function_descriptor

        previous_function = self._current_function
        self._current_function = function_descriptor
        self.generic_visit(function_definition)
        self._current_function = previous_function

    def visit_FuncCall(self, function_call):
        callee = function_call.name.name
        self.functions[self._current_function.name].callees.add(callee)

    @staticmethod
    def run(ast):
        call_analyzer = CallAnalyzer()
        call_analyzer.visit(ast)
        return call_analyzer.functions

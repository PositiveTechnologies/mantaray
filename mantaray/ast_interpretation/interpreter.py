import logging

from pycparser import c_ast

from mantaray.symbolic_execution.expressions import BinaryOperatorType, UnaryOperatorType
from mantaray.symbolic_execution.optionalizer import optionalize
from mantaray.symbolic_execution.type import SEType

logger = logging.getLogger("ast_interpreter")


class ASTInterpreter(c_ast.NodeVisitor):
    def __init__(self, se_engine, functions):
        self.se_engine = se_engine
        self.functions = functions
        self.interpret = self.visit

    def visit_Assignment(self, assignment):
        se_rvalue = self.interpret(assignment.rvalue)
        se_lvalue = self.interpret(assignment.lvalue)
        return self.se_engine.process_assignment_expr(se_lvalue, se_rvalue)

    def visit_FuncCall(self, function_call):
        function_name = function_call.name.name
        result = None
        if function_name in self.functions:
            descriptor = self.functions[function_name]
            se_arguments = []

            if function_call.args:
                for expr in function_call.args.exprs:
                    se_arguments.append(self.visit(expr))

            if self.se_engine.try_enter_function(descriptor, se_arguments):
                logger.info("Entering body of function: `{0}`".format(descriptor))
                self.interpret(descriptor.body)
                result = self.se_engine.leave_function()
                logger.info("Leaved body of function: `{0}`".format(descriptor))

                options_str = ""
                for option in optionalize(result):
                    options_str += "    {0},\n".format(option)
                logger.info("`{0}` returned: {{\n{1}}}".format(descriptor, options_str))

        return result

    def visit_Constant(self, constant):
        return self.se_engine.create_literal(constant.value, SEType.get_from_name(constant.type))

    def visit_Decl(self, decl):
        se_type = SEType.get_from_ast(decl.type)
        variable = self.se_engine.create_variable(decl.name, se_type)

        if decl.init is not None:
            se_rvalue = self.interpret(decl.init)
        else:
            # Implicit initialization
            se_rvalue = self.se_engine.create_literal(se_type.default_value, se_type)

        self.se_engine.process_assignment_expr(variable, se_rvalue)
        logger.info("Variable `{0} {1}` initialized with value: `{2}`".format(se_type, variable, se_rvalue))

        return variable

    def visit_ID(self, id):
        if id.name in ("false", "true"):
            return self.se_engine.create_literal(id.name, SEType.BOOL)

        return self.se_engine.get_variable_ref(id.name)

    def visit_Return(self, return_statement):
        return_expr = self.interpret(return_statement.expr)
        self.se_engine.process_return_statement(return_expr)

    def visit_BinaryOp(self, binary_op):
        bop_type = BinaryOperatorType.get_from_sign(binary_op.op)
        argument2 = self.interpret(binary_op.right)
        argument1 = self.interpret(binary_op.left)
        return self.se_engine.process_binary_operator(argument1, argument2, bop_type)

    def visit_UnaryOp(self, unary_op):
        op_type = UnaryOperatorType.get_from_sign(unary_op.op)
        argument = self.interpret(unary_op.expr)
        return self.se_engine.process_unary_operator(argument, op_type)

    def visit_Compound(self, compound_statement):
        if self.se_engine.try_enter_statement_block():
            for statement in compound_statement.block_items:
                if self.se_engine.current_context.is_reachable:
                    self.interpret(statement)
            self.se_engine.leave_statement_block()

    def visit_If(self, if_statement):
        condition = self.interpret(if_statement.cond)

        if self.se_engine.try_enter_conditional_statement(condition):
            if_statement_context = self.se_engine.current_context

            if self.se_engine.try_enter_branch(if_statement_context.if_true_context):
                self.interpret(if_statement.iftrue)
                self.se_engine.leave_branch()

            if if_statement.iffalse is not None:
                if self.se_engine.try_enter_branch(if_statement_context.if_false_context):
                    self.interpret(if_statement.iffalse)
                    self.se_engine.leave_branch()

            self.se_engine.leave_conditional_statement()


    def generic_visit(self, node):
        logger.warning("Unsupported node type: {0}".format(node))

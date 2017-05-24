from z3 import Bool, Real, Int, Not, And, Or, z3

from mantaray.errors import MantarayError, MantarayNotImplemented
from mantaray.symbolic_execution.expressions import UnaryOperatorType, BinaryOperatorType
from mantaray.symbolic_execution.type import SEType
from mantaray.symbolic_execution.visitor import SEVisitor


class SE2SMTConverter(SEVisitor):
    def __init__(self):
        self.transform = self.visit
        self.symbols = {}

    def visit_Variable(self, variable):
        ctors_map = {
            SEType.BOOL: Bool,
            SEType.INT: Int,
            SEType.FLOAT: Real
        }

        ctor = ctors_map.get(variable.se_type, None)

        if ctor is None:
            raise MantarayNotImplemented(variable.se_type)

        self.symbols[variable.name] = variable
        return ctor(variable.name)

    def visit_Conditional(self, conditional):
        raise MantarayError("Conditional can not be properly transformed into SMTLib entities")

    def visit_Literal(self, literal):
        ctors = {
            SEType.BOOL: z3.BoolVal,
            SEType.INT: z3.IntVal,
            SEType.FLOAT: z3.RealVal
        }

        ctor = ctors.get(literal.se_type, None)

        if ctor is not None:
            return ctor(literal.value)

        raise MantarayNotImplemented(literal.se_type)

    def visit_UnaryOperator(self, unary_operator):
        ctors_map = {
            UnaryOperatorType.NOT: Not,
        }

        argument = self.transform(unary_operator.argument)
        ctor = ctors_map.get(unary_operator.op_type, None)

        if ctor is None:
            raise MantarayNotImplemented(unary_operator.op_type)

        return ctor(argument)

    def visit_BinaryOperator(self, binary_operator):
        ctors_map = {
            BinaryOperatorType.AND: And,
            BinaryOperatorType.OR: Or,
            BinaryOperatorType.ADD: lambda arg1, arg2: arg1 + arg2,
            BinaryOperatorType.MINUS: lambda arg1, arg2: arg1 - arg2,
            BinaryOperatorType.MUL: lambda arg1, arg2: arg1 * arg2,
            BinaryOperatorType.DIV: lambda arg1, arg2: arg1 / arg2,
            BinaryOperatorType.EQ: lambda arg1, arg2: arg1 == arg2,
            BinaryOperatorType.NE: lambda arg1, arg2: arg1 != arg2,
            BinaryOperatorType.GT: lambda arg1, arg2: arg1 > arg2,
            BinaryOperatorType.GE: lambda arg1, arg2: arg1 >= arg2,
            BinaryOperatorType.LT: lambda arg1, arg2: arg1 < arg2,
            BinaryOperatorType.LE: lambda arg1, arg2: arg1 <= arg2,
        }

        argument1 = self.transform(binary_operator.argument1)
        argument2 = self.transform(binary_operator.argument2)
        ctor = ctors_map.get(binary_operator.bop_type, None)

        if ctor is None:
            raise MantarayNotImplemented(binary_operator.bop_type)

        return ctor(argument1, argument2)


def se2smt(s_expression):
    se2smt_converter = SE2SMTConverter()
    return se2smt_converter.transform(s_expression), se2smt_converter.symbols

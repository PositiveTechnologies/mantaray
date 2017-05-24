import uuid
from abc import ABC, abstractmethod
from enum import Enum

import collections

from mantaray.errors import MantarayError, MantarayNotImplemented
from mantaray.symbolic_execution.type import SEType


class Option:
    """ Class to represent conditional symbolic values
    """
    def __init__(self, condition, value):
        self.condition = condition
        self.value = value
        self.id = self.id = uuid.uuid4().hex

    def __str__(self):
        return "{0} -> {1}".format(self.condition, self.value)

    def adjunct_condition(self, condition):
        self.condition = se_and(self.condition, condition)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return self.id == other.id

    def __ne__(self, other):
        return not(self == other)


class SymbolicExpression(ABC):
    """ Abstract base class for all symbolic expressions
    """

    @abstractmethod
    def equality_components(self):
        pass

    @abstractmethod
    def get_se_type(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    def __hash__(self):
        return hash(self.equality_components())

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        self_equality_components = self.equality_components()
        other_equality_components = other.equality_components()
        return self_equality_components == other_equality_components

    def __ne__(self, other):
        return not(self == other)


class Variable(SymbolicExpression):
    def __init__(self, context_id, name, se_type):
        self.context_id = context_id
        self.name = name
        self.se_type = se_type

    def equality_components(self):
        return self.context_id, self.name, self.se_type

    def get_se_type(self):
        return self.se_type

    def __str__(self):
        return self.name


class Conditional(SymbolicExpression):
    def __init__(self, se_type, options):
        self.se_type = se_type
        self.options = tuple(options)

    def equality_components(self):
        return self.se_type, self.options

    def get_se_type(self):
        return self.se_type

    def __str__(self):
        return "{{{0}}}".format(", ".join(map(lambda option: str(option), self.options)))


class Literal(SymbolicExpression):
    def __init__(self, value, se_type, implicit = False):
        ctors_map = {
            SEType.CHAR: str,
            SEType.FLOAT: float,
            SEType.INT: int,
            SEType.BOOL: bool
        }

        ctor = ctors_map.get(se_type, None)

        if ctor is None:
            raise MantarayNotImplemented(se_type)

        self.value = ctor(value)
        self.se_type = se_type
        self.implicit = implicit

    def equality_components(self):
        return self.value, self.se_type

    def get_se_type(self):
        return self.se_type

    def __str__(self):
        if self.se_type is SEType.CHAR:
            return "'{0}'".format(self.value)

        if self.se_type is SEType.CHAR_ARRAY:
            return "\"{0}\"".format(self.value)

        if self.se_type is SEType.VOID:
            return "void"

        if self.se_type in (SEType.BOOL, SEType.INT, SEType.FLOAT):
            return str(self.value)

        if self.se_type in (SEType.BOOL_ARRAY, SEType.INT_ARRAY, SEType.FLOAT_ARRAY):
            return "[{0}]".format(", ".join(str(self.value)))

        raise MantarayNotImplemented(self.se_type)


class BinaryOperatorType(Enum):
    AND = "&&"
    OR = "||"
    ADD = "+"
    MINUS = "-"
    MUL = "*"
    DIV = "/"
    EQ = "=="
    NE = "!="
    GT = ">"
    GE = ">="
    LT = "<"
    LE = "<="

    def __str__(self):
        return self.value

    @staticmethod
    def get_from_sign(bop_sign):
        bop_type_list = [member for member in BinaryOperatorType.__members__.values() if member.value == bop_sign]

        if not bop_type_list:
            raise MantarayError("Unknown binary operator type: {0}".format(bop_sign))

        return bop_type_list[0]


class BinaryOperator(SymbolicExpression):
    def __init__(self, argument1, argument2, bop_type):
        self.argument1 = argument1
        self.argument2 = argument2
        self.bop_type = bop_type

    def equality_components(self):
        return self.argument1, self.argument2

    def get_se_type(self):
        se_type1 = self.argument1.get_se_type()
        se_type2 = self.argument2.get_se_type()

        if se_type1 != se_type2:
            raise MantarayError("Incompatible types: `{0}` and `{1}`".format(se_type1, se_type2))

        return se_type1

    @staticmethod
    def create_from_args(bop_type, *args):
        if len(args) == 1 and isinstance(args[0], collections.Iterable):
            args = args[0]

        bop = None

        for argument in args:
            bop = argument if bop is None else BinaryOperator(bop, argument, bop_type)

        return bop

    def __str__(self):
        return "({0} {1} {2})".format(self.argument1, str(self.bop_type), self.argument2)


class UnaryOperatorType(Enum):
    NOT = "!"

    def __str__(self):
        return self.value

    @staticmethod
    def get_from_sign(op_sign):
        op_type_list = [member for member in UnaryOperatorType.__members__.values() if member.value == op_sign]

        if not op_type_list:
            raise MantarayError("Unknown unary operator type: {0}".format(op_sign))

        return op_type_list[0]


class UnaryOperator(SymbolicExpression):
    def __init__(self, argument, op_type):
        self.argument = argument
        self.op_type = op_type

    def equality_components(self):
        return self.argument

    def get_se_type(self):
        return self.argument.get_se_type()

    def __str__(self):
        return "({0}{1})".format(str(self.op_type), self.argument)


SE_TRUE = Literal(True, SEType.BOOL)
SE_FALSE = Literal(False, SEType.BOOL)


def se_and(argument1, argument2):
    return BinaryOperator(argument1, argument2, BinaryOperatorType.AND)


def se_or(argument1, argument2):
    return BinaryOperator(argument1, argument2, BinaryOperatorType.OR)


def se_not(argument):
    return UnaryOperator(argument, UnaryOperatorType.NOT)

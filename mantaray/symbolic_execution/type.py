from enum import Enum

from mantaray.ast_interpretation.typer import get_ast_type
from mantaray.errors import MantarayError


class SEType(Enum):
    """ Enum class to represent types in symbolic expressions
    """

    VOID = "void"
    INT = "int"
    BOOL = "bool"
    CHAR = "char"
    FLOAT = "float"
    INT_ARRAY = "int[]"
    BOOL_ARRAY = "bool[]"
    CHAR_ARRAY = "char[]"
    FLOAT_ARRAY = "float[]"

    @property
    def default_value(self):
        default_values = {
            SEType.VOID: None,
            SEType.INT: 0,
            SEType.BOOL: False,
            SEType.CHAR: '\0',
            SEType.FLOAT: 0.0,
            SEType.INT_ARRAY: [],
            SEType.BOOL_ARRAY: [],
            SEType.CHAR_ARRAY: [],
            SEType.FLOAT_ARRAY: [],
        }

        return default_values.get(self, None)

    def __str__(self):
        return self.value

    @staticmethod
    def get_from_name(type_name):
        se_type_list = [member for member in SEType.__members__.values() if member.value == type_name]

        if not se_type_list:
            raise MantarayError("Unknown type: `{0}`".format(type_name))

        return se_type_list[0]

    @staticmethod
    def get_from_ast(node):
        return SEType.get_from_name(get_ast_type(node))

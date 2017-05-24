import z3


# patch z3api
from mantaray.errors import MantarayError, MantarayNotImplemented
from mantaray.symbolic_execution.expressions import BinaryOperator, BinaryOperatorType, SE_FALSE, SE_TRUE, \
    UnaryOperator, UnaryOperatorType, Literal
from mantaray.symbolic_execution.type import SEType

z3.is_ite = lambda x: z3.is_app_of(x, z3.Z3_OP_ITE)
z3.is_function = lambda x: z3.is_app_of(x, z3.Z3_OP_UNINTERPRETED)
z3.is_array_store = lambda x: z3.is_app_of(x, z3.Z3_OP_STORE)
z3.get_payload = lambda node, i: z3.Z3_get_decl_int_parameter(node.ctx.ref(), node.decl().ast, i)


class AstRefKey:
    def __init__(self, n):
        self.n = n

    def __hash__(self):
        return self.n.hash()

    def __eq__(self, other):
        return self.n.eq(other.n)


def as_key(n):
    assert isinstance(n, z3.AstRef)
    return AstRefKey(n)


class SMT2SEConverter:
    def __init__(self, symbols):
        self.symbols = symbols
        self._memoization = {}
        self._convert_funcs = {
            z3.Z3_OP_AND: lambda args, expr: BinaryOperator.create_from_args(BinaryOperatorType.AND, args),
            z3.Z3_OP_OR: lambda args, expr: BinaryOperator.create_from_args(BinaryOperatorType.OR, args),
            z3.Z3_OP_MUL: lambda args, expr: BinaryOperator.create_from_args(BinaryOperatorType.MUL, args),
            z3.Z3_OP_ADD: lambda args, expr: BinaryOperator.create_from_args(BinaryOperatorType.ADD, args),
            z3.Z3_OP_DIV: lambda args, expr: BinaryOperator(args[0], args[1], BinaryOperatorType.DIV),
            z3.Z3_OP_FALSE: lambda args, expr: SE_FALSE,
            z3.Z3_OP_TRUE: lambda args, expr: SE_TRUE,
            z3.Z3_OP_GT: lambda args, expr: BinaryOperator(args[0], args[1], BinaryOperatorType.GT),
            z3.Z3_OP_GE: lambda args, expr: BinaryOperator(args[0], args[1], BinaryOperatorType.GE),
            z3.Z3_OP_LT: lambda args, expr: BinaryOperator(args[0], args[1], BinaryOperatorType.LT),
            z3.Z3_OP_LE: lambda args, expr: BinaryOperator(args[0], args[1], BinaryOperatorType.LE),
            z3.Z3_OP_SUB: lambda args, expr: BinaryOperator(args[0], args[1], BinaryOperatorType.MINUS),
            z3.Z3_OP_NOT: lambda args, expr: UnaryOperator(args[0], UnaryOperatorType.NOT),
            z3.Z3_OP_EQ: lambda args, expr: BinaryOperator(args[0], args[1], BinaryOperatorType.EQ),
        }

    def transform(self, expr):
        """ Converts a Z3 expression into a symbolic expression tree.
        """
        stack = [expr]
        while len(stack) > 0:
            current = stack.pop()
            key = as_key(current)
            if key not in self._memoization:
                self._memoization[key] = None
                stack.append(current)
                for i in range(current.num_args()):
                    stack.append(current.arg(i))
            elif self._memoization[key] is None:
                args = [self._memoization[as_key(current.arg(i))]
                        for i in range(current.num_args())]
                res = self._single_term(current, args)
                self._memoization[key] = res
            else:
                # we already visited the node, nothing else to do
                pass
        return self._memoization[as_key(expr)]

    def _single_term(self, expr, args):
        decl = z3.Z3_get_app_decl(expr.ctx_ref(), expr.as_ast())
        kind = z3.Z3_get_decl_kind(expr.ctx.ref(), decl)
        # Try to get the conversion function for the given Kind
        fun = self._convert_funcs.get(kind, None)

        if fun is not None:
            return fun(args, expr)

        if z3.is_const(expr):
            # Const or Symbol
            if z3.is_rational_value(expr):
                f = expr.numerator_as_long()/expr.denominator_as_long()
                if f.is_integer():
                    return Literal(int(f), SEType.INT)
                else:
                    return Literal(f, SEType.FLOAT)

            elif z3.is_int_value(expr):
                n = expr.as_long()
                return Literal(n, SEType.INT)
            else:
                # it must be a symbol
                symbol = self.symbols.get(str(expr), None)

                if symbol is not None:
                    return symbol

                raise MantarayError("Symbol %s not found".format(expr))

        # If we reach this point, we did not manage to translate the expression
        raise MantarayNotImplemented(str(expr))


def smt2se(smt_expression, symbols):
    smt2se_converter = SMT2SEConverter(symbols)
    return smt2se_converter.transform(smt_expression)

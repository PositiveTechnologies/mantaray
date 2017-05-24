import z3

from mantaray.solving.se2smt import se2smt
from mantaray.solving.smt2se import smt2se


def se_simplify(s_expression):
    smt_expression_original, symbols = se2smt(s_expression)
    smt_expression_processed = z3.simplify(smt_expression_original)
    s_expression_processed = smt2se(smt_expression_processed, symbols)
    return s_expression_processed


def is_sat(s_expression):
    solver = z3.Solver()
    smt_expression, symbols = se2smt(s_expression)
    solver.add(smt_expression)
    return solver.check() == z3.sat

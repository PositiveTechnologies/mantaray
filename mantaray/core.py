import logging
import os
import sys
from io import StringIO

from pycparser import parse_file, c_parser
from pycparser.c_ast import FuncCall, ID

from mantaray.ast_interpretation.interpreter import ASTInterpreter
from mantaray.ast_interpretation.call_analyzer import CallAnalyzer
from mantaray.symbolic_execution.engine import SEEngine

logger = logging.getLogger("core")


def run(file_name, deepness):
    ast = get_ast(file_name)

    if ast is None:
        logger.error("Fatal error occurred during AST constructing.")
        return

    functions = CallAnalyzer.run(ast)

    call_table_str = ""
    for function_descriptor in functions.values():
        callees_str = ", calls: " + ", ".join(function_descriptor.callees) if function_descriptor.callees else ""
        call_table_str += "    Function: `{0}`{1}\n".format(function_descriptor, callees_str)
    logger.info("Call analysis complete:\n{0}".format(call_table_str))

    entry_points = collect_entry_points(functions)
    for entry_point in entry_points:
        logger.info("Function `{0}` considered as entry point.\n".format(entry_point))
        symbolic_vm = SEEngine(deepness)
        ast_interpreter = ASTInterpreter(symbolic_vm, functions)
        entry_point_call = FuncCall(ID(entry_point.name), [])
        result = ast_interpreter.interpret(entry_point_call)


def get_ast(file_name):
    cpp_path = search_cpp()
    if cpp_path:
        logger.info("{0} will be used as C preprocessor.".format(cpp_path))
    else:
        logger.warning("C preprocessor not found. Only already preprocessed sources will be interpreted correctly.")

    try:
        ast = parse_file(file_name, use_cpp=cpp_path is not None, cpp_path=cpp_path)
    except c_parser.ParseError:
        e = sys.exc_info()[1]
        logger.error("Parse error: {0}.".format(str(e)))
        return

    string_io = StringIO()
    ast.show(buf=string_io, offset=4, attrnames=True, nodenames=True)
    logger.info("{0} successfully parsed:\n{1}".format(file_name, string_io.getvalue()))
    return ast


def search_cpp():
    for cpp_name in ["cpp", "clang-cpp"]:
        for extension in ["", ".exe", ".bat", ".cmd"]:
            found_path = which(cpp_name + extension)
            if found_path is not None:
                return found_path
    return None


def which(executable):
    def is_exe(executable_path):
        return os.path.isfile(executable_path) and os.access(executable_path, os.X_OK)

    file_path, file_name = os.path.split(executable)

    if file_path:
        if is_exe(executable):
            return executable
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, executable)
            if is_exe(exe_file):
                return exe_file

    return None


def collect_entry_points(functions):
    func_called = set()
    for func in functions.values():
        func_called = func_called.union(func.callees)

    entry_points = set()
    for func in functions.values():
        if func.name not in func_called:
            entry_points.add(func)

    return entry_points

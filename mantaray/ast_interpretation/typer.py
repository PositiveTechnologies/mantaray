from pycparser import c_ast

from mantaray.errors import MantarayError


class ASTTyper(c_ast.NodeVisitor):
    """ Resolves ast_type for a given expression
    """

    def visit_ArrayDecl(self, array_decl):
        type_name = self.visit(array_decl.type)
        return type_name + "[]"

    def visit_TypeDecl(self, type_decl):
        return self.visit(type_decl.type)

    def visit_IdentifierType(self, identifier_type):
        return identifier_type.names[0]

    def generic_visit(self, node):
        raise MantarayError("Can not build type from node: `{0}`".format(node))


ast_typer = ASTTyper()


def get_ast_type(ast_expression):
    return ast_typer.visit(ast_expression)

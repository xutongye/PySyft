# third party

# syft relative
from . import request  # noqa: 401
from . import response  # noqa: 401
from . import server_setup  # noqa: 401
from ...ast import add_classes
from ...ast import add_methods
from ...ast import add_modules
from ...ast.globals import Globals


def create_psi_ast() -> Globals:
    ast = Globals()

    modules = ["syft", "syft.lib", "syft.lib.psi", "syft.lib.psi.server_setup"]
    classes = [
        (
            "syft.lib.psi.server_setup",
            "syft.lib.psi.server_setup",
            server_setup.SyServerSteup,
        ),
        (
            "syft.lib.psi.request",
            "syft.lib.psi.request",
            request.SyRequest,
        ),
        (
            "syft.lib.psi.response",
            "syft.lib.psi.response",
            response.SyResponse,
        ),
    ]

    methods = []  # type: ignore

    add_modules(ast, modules)
    add_classes(ast, classes)
    add_methods(ast, methods)

    for klass in ast.classes:
        klass.create_pointer_class()
        klass.create_send_method()
        klass.create_serialization_methods()
        klass.create_storable_object_attr_convenience_methods()

    return ast

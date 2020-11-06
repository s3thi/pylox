import re


def define_ast(base_class_name, productions):
    base_class = type(base_class_name, (object,), {})
    globals()[base_class_name] = base_class

    for production in productions:
        (production_class_name, fields) = tuple(
            map(lambda s: s.strip(), production.split(":"))
        )
        production_class_name = production_class_name + base_class_name

        fields = fields.split(",")
        field_names = list(map(lambda s: s.strip().split(" ")[1], fields))
        globals()[production_class_name] = make_production_class(
            production_class_name, base_class, field_names
        )


def make_production_class(production_class_name, base_class, field_names):
    def __init__(self, **kwargs):
        for f in field_names:
            if f not in kwargs.keys():
                raise TypeError(
                    f'Missing argument "{f}" for class {self.__class__.__name__}'
                )
            setattr(self, f, kwargs[f])

    def accept(self, visitor):
        method_name = re.sub(
            r"([A-Z]+)", r"_\1", f"visit{production_class_name}"
        ).lower()
        return getattr(visitor, method_name)(self)

    production_class = type(
        production_class_name, (base_class,), {"__init__": __init__, "accept": accept}
    )

    return production_class


define_ast(
    "Expr",
    [
        "Assign   : Token name, Expr value",
        "Binary   : Expr left, Token operator, Expr right",
        "Call     : Expr callee, Token paren, List<Expr> arguments",
        "Get      : Expr objekt, Token name",
        "Grouping : Expr expression",
        "Literal  : Object value",
        "Logical  : Expr left, Token operator, Expr right",
        "Set      : Expr objekt, Token name, Expr value",
        "Super    : Token keyword, Token method",
        "This     : Token keyword",
        "Unary    : Token operator, Expr right",
        "Variable : Token name",
    ],
)

define_ast(
    "Stmt",
    [
        "Block      : List<Stmt> statements",
        "Class      : Token name, VariableExpr superclass, List<FunctionStmt> methods",
        "Expression : Expr expression",
        "Function   : Token name, List<Token> params, List<Stmt> body",
        "If         : Expr condition, Stmt then_branch, Stmt else_branch",
        "Print      : Expr expression",
        "Return     : Token keyword, Expr value",
        "Var        : Token name, Expr initializer",
        "While      : Expr condition, Stmt body",
    ],
)

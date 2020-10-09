# TODO: it should be possible to add some sort of runtime type
# checking to this code.


def define_ast(base_class_name, productions):
    base_class = type(base_class_name, (object,), {})
    globals()[base_class_name] = base_class

    for production in productions:
        (production_class_name, fields) = tuple(
            map(lambda s: s.strip(), production.split(":"))
        )

        fields = fields.split(",")
        field_names = list(map(lambda s: s.strip().split(" ")[1], fields))
        globals()[production_class_name] = make_production_class(
            production_class_name, base_class, field_names
        )


def make_production_class(production_class_name, base_class, field_names):
    def __init__(self, **kwargs):
        for (k, v) in kwargs.items():
            if k not in field_names:
                raise TypeError(
                    f"Argument {k} is not valid for class {self.__class__.__name__}"
                )
            setattr(self, k, v)

    production_class = type(
        production_class_name, (base_class,), {"__init__": __init__}
    )

    return production_class


define_ast(
    "Expr",
    [
        "Binary   : Expr left, Token operator, Expr right",
        "Grouping : Expr expression",
        "Literal  : Object value",
        "Unary    : Token operator, Expr right",
    ],
)

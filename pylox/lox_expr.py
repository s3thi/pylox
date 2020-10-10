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
        getattr(visitor, f"visit{production_class_name}")(self)

    production_class = type(
        production_class_name, (base_class,), {"__init__": __init__, "accept": accept}
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

from peano_game.pawff import BoolLit
from peano_game.set import EmptySet, FullSet, NatSet, SetExpr, UnknownSet


def set_decider(set_expr: SetExpr) -> NatSet:
    simplified=set_expr.simplify()
    if type(simplified.form)==BoolLit:
        if simplified.form.value:
            return FullSet()
        else:
            return EmptySet()
    return UnknownSet()

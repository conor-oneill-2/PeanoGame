from peano_game.generator import wff
from peano_game.natset import SetExpr
from peano_game.pawff import Var


def set_wff(i:int) -> SetExpr:
    return SetExpr(
        Var(0),
        wff(i, num_vars_used=1)
    )

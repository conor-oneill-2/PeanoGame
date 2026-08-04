# pyright: reportAttributeAccessIssue=none
# pyright: reportArgumentType=none

from peano_game import pawff
from peano_game.normal_form import first_normal_form
from peano_game.ternary import Ternary


def decider(form:pawff.Form,nf:int=0)->Ternary:
    match type(form):
        case pawff.AtForm:
            return quant_free_eval(form)
        case pawff.NotForm:
            return ~decider(form.form,nf)
        case pawff.AndForm:
            return decider(form.form1,nf)&decider(form.form2,nf)
        case pawff.OrForm:
            return decider(form.form1,nf)|decider(form.form2,nf)
        case pawff.ImpliesForm:
            return (~decider(form.form1,nf))|decider(form.form2,nf)
        case pawff.ForAllForm:
            if nf==0:
                first_nf=first_normal_form(form)
                return decider(first_nf,1)
            return for_all_decider(form.var,form.form)
        case pawff.ExistsForm:
            if nf==0:
                first_nf=first_normal_form(form)
                return decider(first_nf,1)
            return exists_decider(form.var,form.form)

    return Ternary.UNKNOWN

#If there's no variables, just check whether LHS=RHS
def quant_free_eval(form:pawff.AtForm)->Ternary:
    t1_val=form.term1.eval()
    t2_val=form.term2.eval()
    if t1_val==t2_val:
        return Ternary.TRUE
    return Ternary.FALSE

def for_all_decider(var:pawff.Var,form:pawff.Form)->Ternary:
    if type(form)==pawff.AtForm:
        return poly_eq_decider({var},form.form1,form.form2)
    return Ternary.UNKNOWN

def poly_eq_decider(vars,polyform1,polyform2)->Ternary:
    poly1=polyform1.poly(vars)
    poly2=polyform2.poly(vars)
    if poly1==poly2:
        return Ternary.TRUE
    else:
        return Ternary.FALSE

def exists_decider(var:pawff.Var,form:pawff.Form)->Ternary:
    return Ternary.UNKNOWN
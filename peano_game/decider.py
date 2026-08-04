# pyright: reportAttributeAccessIssue=none
# pyright: reportArgumentType=none

from sympy import divisors

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
    vars=[var]
    while type(form)==pawff.ForAllForm:
        vars.append(form.var)
        form=form.form
    
    if type(form)==pawff.AtForm:
        return poly_eq_decider(form.term1,form.term2)

    if type(form)==pawff.OrForm:
        #IMPORTANT: ForAll(x,F|G) is NOT equivalent to ForAll(x,F)|ForAll(x,G)
        #But if ForAll(x,F) is True, then ForAll(x,F|G) is True
        #and if ForAll(x,G) is True, then ForAll(x,F|G) is True
        f1=pawff.ForAllForm(var,form.form1)
        f2=pawff.ForAllForm(var,form.form2)
        f1_res=decider(f1)
        f2_res=decider(f2)
        if f1_res==Ternary.TRUE:
            return Ternary.TRUE
        if f2_res==Ternary.TRUE:
            return Ternary.TRUE

        #If OR(ForAll(x,F),Exists(x,G)) is False, then ForAll(x,F|G) is False
        #since there is at least one x for which F(x) is False, and G(x) is False for all x
        alt1=pawff.ExistsForm(var,form.form1)
        alt2=pawff.ExistsForm(var,form.form2)
        if f1_res|decider(alt2)==Ternary.FALSE:
            return Ternary.FALSE
        if f2_res|decider(alt1)==Ternary.FALSE:
            return Ternary.FALSE

    return Ternary.UNKNOWN

def poly_eq_decider(polyform1:pawff.Term,polyform2:pawff.Term)->Ternary:
    poly1=polyform1.poly()
    poly2=polyform2.poly()
    if poly1==poly2:
        return Ternary.TRUE
    else:
        return Ternary.FALSE

def exists_decider(var:pawff.Var,form:pawff.Form)->Ternary:
    if type(form)==pawff.AtForm:
        return rational_roots_decider(var,form.term1,form.term2)

    if type(form)==pawff.AndForm:
        #IMPORTANT: Exists(x,F&G) is NOT equivalent to Exists(x,F)&Exists(x,G)
        #But if Exists(x,F) is False, then Exists(x,F&G) is False
        #and if Exists(x,G) is False, then Exists(x,F&G) is False
        f1=pawff.ExistsForm(var,form.form1)
        f2=pawff.ExistsForm(var,form.form2)
        f1_res=decider(f1)
        f2_res=decider(f2)
        if f1_res==Ternary.FALSE:
            return Ternary.FALSE
        if f2_res==Ternary.FALSE:
            return Ternary.FALSE

        #If And(ForAll(x,F),Exists(x,G)) is True, then Exists(x,F&G) is True
        #since there is at least one x for which G(x) is True, and F(x) is True for all x
        alt1=pawff.ForAllForm(var,form.form1)
        alt2=pawff.ForAllForm(var,form.form2)
        if f1_res==Ternary.TRUE:  # noqa: SIM102
            if decider(alt2)==Ternary.TRUE:
                return Ternary.TRUE
        if f2_res==Ternary.TRUE:  # noqa: SIM102
            if decider(alt1)==Ternary.TRUE:
                return Ternary.TRUE
    return Ternary.UNKNOWN

def rational_roots_decider(var:pawff.Var,term1:pawff.Term,term2:pawff.Term)->Ternary:
    t1_val=term1(**{str(var):pawff.Zero()}).eval()
    t2_val=term2(**{str(var):pawff.Zero()}).eval()
    diff=abs(t1_val-t2_val)
    #Rational roots theorem states that if if x is an integer root of f(x),
    #x=0, or x divides |f(0)|
    if diff==0:
        return Ternary.TRUE
    divisors_list=divisors(diff)
    for divisor in divisors_list:
        t1_val=term1(**{str(var):pawff.succ_form(divisor)}).eval()
        t2_val=term2(**{str(var):pawff.succ_form(divisor)}).eval()
        if t1_val==t2_val:
            return Ternary.TRUE
    return Ternary.FALSE
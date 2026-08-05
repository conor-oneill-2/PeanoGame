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
            result=Ternary.TRUE
            for iform in form.forms:
                result&=decider(iform,nf)
            return result
        case pawff.OrForm:
            result=Ternary.FALSE
            for iform in form.forms:
                result|=decider(iform,nf)
            return result
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
        iforms=(pawff.ForAllForm(var,iform) for iform in form.forms)
        iforms_dec=(decider(iform) for iform in iforms)
        if any(iforms_dec==Ternary.TRUE):
            return Ternary.TRUE

        #If OR(ForAll(x,F),Exists(x,G)) is False, then ForAll(x,F|G) is False
        #since there is at least one x for which F(x) is False, and G(x) is False for all x
        #and similarly, if ForAll(x,F) is false and for all other terms Exists(x,G) are false,
        #then the whole formula is false
        altforms=(pawff.ExistsForm(var,iform) for iform in form.forms)
        altforms_dec=(decider(altform) for altform in altforms)
        for j in range(len(altforms_dec)):
            result=Ternary.FALSE
            for i, (altform_dec,iform_dec) in enumerate(zip(altforms_dec,iforms_dec)):
                if i==j:
                    check_val=iform_dec
                else:
                    check_val=altform_dec
                if check_val!=Ternary.FALSE:
                    result=check_val
                    break
            if result==Ternary.FALSE:
                return Ternary.FALSE

    if type(form)==pawff.ExistsForm:
        return forall_exists_decider(var,form.var,form.form)

    return Ternary.UNKNOWN

def poly_eq_decider(polyform1:pawff.Term,polyform2:pawff.Term)->Ternary:
    poly1=polyform1.poly()
    poly2=polyform2.poly()
    if poly1==poly2:
        return Ternary.TRUE
    else:
        return Ternary.FALSE

def forall_exists_decider(forall_var:pawff.Var,exists_var:pawff.Var,form:pawff.Form)->Ternary:
    if type(form)==pawff.AtForm:
        #If of the form exists_var=F(forall_var), then result is True
        if form.term1==exists_var and form.term2.vars_used()=={forall_var}:
            return Ternary.TRUE
        if form.term1.vars_used()=={forall_var} and form.term2==exists_var:
            return Ternary.TRUE
    return Ternary.UNKNOWN

def exists_decider(var:pawff.Var,form:pawff.Form)->Ternary:
    if type(form)==pawff.AtForm:
        return rational_roots_decider(var,form.term1,form.term2)

    if type(form)==pawff.AndForm:
        return exists_and_decider(var,*form.forms)

    if type(form)==pawff.ForAllForm:
        return exists_forall_decider(var,form.var,form.form)

    vars={var}
    while type(form)==pawff.ExistsForm:
        vars.add(form.var)
        form=form.form
    return exists_multivar_decider(vars,form)

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

def exists_and_decider(var:pawff.Var,*forms:pawff.Form)->Ternary:
    #IMPORTANT: Exists(x,F&G) is NOT equivalent to Exists(x,F)&Exists(x,G)
    #But if Exists(x,F) is False, then Exists(x,F&G) is False
    #and if Exists(x,G) is False, then Exists(x,F&G) is False
    iforms=(pawff.ExistsForm(var,iform) for iform in forms)
    iforms_dec=(decider(iform) for iform in iforms)
    if any(iform_dec==Ternary.FALSE for iform_dec in iforms_dec):
        return Ternary.FALSE

    #If And(ForAll(x,F),Exists(x,G)) is True, then Exists(x,F&G) is True
    #since there is at least one x for which G(x) is True, and F(x) is True for all x
    altforms=(pawff.ForAllForm(var,iform) for iform in iforms)
    altforms_dec=(decider(altform) for altform in altforms)
    for j in range(len(altforms_dec)):
        result=Ternary.TRUE
        for i, (altform_dec,iform_dec) in enumerate(zip(altforms_dec,iforms_dec)):
            if i==j:
                check_val=iform_dec
            else:
                check_val=altform_dec
            if check_val!=Ternary.TRUE:
                result=check_val
                break
        if result==Ternary.TRUE:
            return Ternary.TRUE

    return Ternary.UNKNOWN

def exists_forall_decider(exists_var:pawff.Var,forall_var:pawff.Var,form:pawff.Form)->Ternary:
    if type(form)==pawff.AtForm:
        #Consider Exists(x,ForAll(y,F(x)=G(y))).
        #For any given value of x, F(x) is fixed, but G(y) varies, so the theorem is false.
        if form.term1.vars_used()=={exists_var} and form.term2.vars_used()=={forall_var}:
            return Ternary.FALSE
        if form.term1.vars_used()=={forall_var} or form.term2.vars_used()=={exists_var}:
            return Ternary.FALSE
    return Ternary.UNKNOWN

def exists_multivar_decider(vars:set[pawff.Var],form:pawff.Form)->Ternary:
    if type(form)==pawff.AtForm:
        #x=F(y,z,...) is True, just by setting x to whatever the RHS evaluates to
        if type(form.term1)==pawff.Var and (form.term1 not in form.term2.vars_used()):
               return Ternary.TRUE
        if type(form.term2)==pawff.Var and (form.term2 not in form.term1.vars_used()):
                return Ternary.TRUE
    return Ternary.UNKNOWN

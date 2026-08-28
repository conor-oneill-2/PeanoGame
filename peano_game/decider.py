from typing import cast

from sympy import (  # pyright: ignore[reportMissingTypeStubs]
    divisors,  # pyright: ignore[reportUnknownVariableType]
)

from peano_game import natset, pawff
from peano_game.ternary import Ternary


def decider(form:pawff.Form,nf:int=0)->Ternary:
    match type(form):
        case pawff.AtForm:
            form=cast(pawff.AtForm, form)
            return quant_free_eval(form)
        case pawff.NotForm:
            form=cast(pawff.NotForm, form)
            return ~decider(form.form,nf)
        case pawff.AndForm:
            form=cast(pawff.AndForm, form)
            result=Ternary.TRUE
            for iform in form.forms:
                result&=decider(iform,nf)
            return result
        case pawff.OrForm:
            form=cast(pawff.OrForm, form)
            result=Ternary.FALSE
            for iform in form.forms:
                result|=decider(iform,nf)
            return result
        case pawff.ImpliesForm:
            form=cast(pawff.ImpliesForm, form)
            return (~decider(form.form1,nf))|decider(form.form2,nf)
        case pawff.ForAllForm:
            form=cast(pawff.ForAllForm, form)
            if nf==0:
                simplified=form.simplify()
                return decider(simplified,1)
            return for_all_decider(form.var,form.form)
        case pawff.ExistsForm:
            form=cast(pawff.ExistsForm, form)
            if nf==0:
                simplified=form.simplify()
                return decider(simplified,1)
            return exists_decider(form.var,form.form)
        case _:
            raise TypeError(f"Unexpected form type: {type(form)}")

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
        set_exprs=(natset.SetExpr(var,iform) for iform in form.forms)
        set_decs=(set_decider(set_expr) for set_expr in set_exprs)
        int_set=natset.intersection(*set_decs)
        return int_set.is_full()

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
        #If expression is of type S(...)=fa_var, then result is False
        #since fa_var can be 0, and LHS>=1
        if type(form.term1)==pawff.Succ and form.term2==forall_var:
            return Ternary.FALSE
        if type(form.term2)==pawff.Succ and form.term1==forall_var:
            return Ternary.FALSE

        #If expression is of type F(e_var)+G(fa_var)=C, then result is False
        #because G(fa_var) can get arbitrarily large, F(e_var) has to get arbitrarily negative
        #but F(e_var) is >= 0, so this is impossible
        if type(form.term1)==pawff.Plus and not form.term2.vars_used():  # noqa: SIM102
            if all(len(term.vars_used())<=1 for term in form.term1.terms):
                return Ternary.FALSE
        if type(form.term2)==pawff.Plus and not form.term1.vars_used():  # noqa: SIM102
            if all(len(term.vars_used())<=1 for term in form.term2.terms):
                return Ternary.FALSE
    return Ternary.UNKNOWN

def exists_decider(var:pawff.Var,form:pawff.Form)->Ternary:
    if type(form)==pawff.AtForm:
        return rational_roots_decider(var,form.term1,form.term2)

    if type(form)==pawff.AndForm:
        set_exprs=(natset.SetExpr(var,iform) for iform in form.forms)
        set_exprs_dec=tuple(set_decider(set_expr) for set_expr in set_exprs)
        union_set=natset.union(*set_exprs_dec)
        return ~union_set.is_empty()

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
    divisors_list=divisors(diff)  # pyright: ignore[reportUnknownVariableType]
    divisors_list=cast(list[int], divisors_list)
    for divisor in divisors_list:
        t1_val=term1(**{str(var):pawff.succ_form(divisor)}).eval()
        t2_val=term2(**{str(var):pawff.succ_form(divisor)}).eval()
        if t1_val==t2_val:
            return Ternary.TRUE
    return Ternary.FALSE


def exists_forall_decider(exists_var:pawff.Var,forall_var:pawff.Var,form:pawff.Form)->Ternary:
    if type(form)==pawff.AtForm:
        #Consider Exists(x,ForAll(y,F(x)=G(y))).
        #For any given value of x, F(x) is fixed, but G(y) varies, so the theorem is false.
        if form.term1.vars_used()=={exists_var} and form.term2.vars_used()=={forall_var}:
            return Ternary.FALSE
        if form.term1.vars_used()=={forall_var} or form.term2.vars_used()=={exists_var}:
            return Ternary.FALSE
        #Similarly, F(x)+G(y)+C=H(x) is impossible since G(y) varies, but H(x)-C1-F(x) is fixed
        if type(form.term1)==pawff.Plus and forall_var not in form.term2.vars_used():  # noqa: SIM102
            #len(term.vars_used())<=1 means it can use exists_var or forall_var but not both
            if all(len(term.vars_used())<=1 for term in form.term1.terms):
                return Ternary.FALSE
        if type(form.term2)==pawff.Plus and forall_var not in form.term1.vars_used():  # noqa: SIM102
            if all(len(term.vars_used())<=1 for term in form.term2.terms):
                return Ternary.FALSE
    return Ternary.UNKNOWN

def exists_multivar_decider(vars:set[pawff.Var],form:pawff.Form)->Ternary:
    if type(form)==pawff.AtForm:
        #x=F(y,z,...) is True, just by setting x to whatever the RHS evaluates to
        if type(form.term1)==pawff.Var and (form.term1 not in form.term2.vars_used()):
               return Ternary.TRUE
        if type(form.term2)==pawff.Var and (form.term2 not in form.term1.vars_used()):
                return Ternary.TRUE

        #If you have F(x,y,...)=0, then given F(x,y,...) is non-negative and non-decreasing in all its variables
        #it is true only if F(0,0,...)=0
        if type(form.term1)==pawff.Zero:
            call_vals={str(var):pawff.Zero() for var in vars}
            return Ternary.TRUE if form.term2.eval(**call_vals)==0 else Ternary.FALSE
        if type(form.term2)==pawff.Zero:
            call_vals={str(var):pawff.Zero() for var in vars}
            return Ternary.TRUE if form.term1(**call_vals).eval()==0 else Ternary.FALSE
    return Ternary.UNKNOWN

def set_decider(set_expr: natset.SetExpr) -> natset.NatSet:
    simplified=set_expr.simplify()
    if simplified.var not in simplified.form.vars_used():
        dec=decider(simplified.form)
        if dec==Ternary.TRUE:
            return natset.FullSet()
        if dec==Ternary.FALSE:
            return natset.EmptySet()
        return natset.UnknownSet()
    if type(simplified.form)==pawff.AtForm:
        t1, t2 = simplified.form.term1, simplified.form.term2
        #Set(x,x=a) is just {a} 
        if type(t1)==pawff.Var and t1 not in t2.vars_used():
                return natset.FiniteNatSet({t2.eval()})
        if type(t2)==pawff.Var and t2 not in t1.vars_used():
                return natset.FiniteNatSet({t1.eval()})
        #Set(x,S(f(x))=0) is empty because LHS>=1
        if type(t1)==pawff.Zero and type(t2)==pawff.Succ:
            return natset.EmptySet()
        if type(t2)==pawff.Zero and type(t1)==pawff.Succ:
            return natset.EmptySet()
        succs=0
        while type(t1)==pawff.Succ:
            succs+=1
            t1=t1.term
        while type(t2)==pawff.Succ:
            succs-=1
            t2=t2.term
        #S^n(t)==S^m(t) iff m==n
        if t1==t2:
            return natset.FullSet() if succs==0 else natset.EmptySet()
        
    if type(simplified.form)==pawff.NotForm:
        comp_expr=natset.SetExpr(simplified.var, simplified.form.form)
        compset=set_decider(comp_expr)
        return compset.complement()

    if type(simplified.form)==pawff.AndForm:
        return natset.intersection(
            *[set_decider(natset.SetExpr(simplified.var, form)) for form in simplified.form.forms]
        )

    if type(simplified.form)==pawff.OrForm:
        return natset.union(
            *[set_decider(natset.SetExpr(simplified.var, form)) for form in simplified.form.forms]
        )
    
    return natset.UnknownSet()

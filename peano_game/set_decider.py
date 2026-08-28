from peano_game import decider, pawff, set
from peano_game.ternary import Ternary


def set_decider(set_expr: set.SetExpr) -> set.NatSet:
    simplified=set_expr.simplify()
    if simplified.var not in simplified.form.vars_used():
        dec=decider.decider(simplified.form)
        if dec==Ternary.TRUE:
            return set.FullSet()
        if dec==Ternary.FALSE:
            return set.EmptySet()
        return set.UnknownSet()
    if type(simplified.form)==pawff.AtForm:
        t1, t2 = simplified.form.term1, simplified.form.term2
        #Set(x,x=a) is just {a} 
        if type(t1)==pawff.Var and t1 not in t2.vars_used():
                return set.FiniteNatSet({t2.eval()})
        if type(t2)==pawff.Var and t2 not in t1.vars_used():
                return set.FiniteNatSet({t1.eval()})
        #Set(x,S(f(x))=0) is empty because LHS>=1
        if type(t1)==pawff.Zero and type(t2)==pawff.Succ:
            return set.EmptySet()
        if type(t2)==pawff.Zero and type(t1)==pawff.Succ:
            return set.EmptySet()
        succs=0
        while type(t1)==pawff.Succ:
            succs+=1
            t1=t1.term
        while type(t2)==pawff.Succ:
            succs-=1
            t2=t2.term
        #S^n(t)==S^m(t) iff m==n
        if t1==t2:
            return set.FullSet() if succs==0 else set.EmptySet()
        
    if type(simplified.form)==pawff.NotForm:
        comp_expr=set.SetExpr(simplified.var, simplified.form.form)
        compset=set_decider(comp_expr)
        return compset.complement()

    if type(simplified.form)==pawff.AndForm:
        return set.intersection(
            *[set_decider(set.SetExpr(simplified.var, form)) for form in simplified.form.forms]
        )

    if type(simplified.form)==pawff.OrForm:
        return set.union(
            *[set_decider(set.SetExpr(simplified.var, form)) for form in simplified.form.forms]
        )
    
    return set.UnknownSet()

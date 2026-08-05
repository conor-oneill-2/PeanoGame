# pyright: reportAttributeAccessIssue=none

from peano_game import pawff


#First TNF includes:
#  S(x)+y -> S(x+y), and x+S(y) -> S(x+y)
#  x+0 -> x, and 0+x -> x
#  0*x -> 0, and x*0 -> 0
#  1*x -> x, and x*1 -> x
#It does not include any theorems that uses the distributive law
#or commutativity/associativity of addition/multiplications
#This will be solved in second_tnf
def first_tnf(term:pawff.Term)->pawff.Term:
    match type(term):
        case pawff.Zero | pawff.Var:
            return term
        case pawff.Succ:
            return pawff.Succ(first_tnf(term.term))
        case pawff.Plus:
            t1=first_tnf(term.term1)
            t2=first_tnf(term.term2)
            
            #S(x)+y -> S(x+y), and x+S(y)->S(x+y)
            numsuccs=0
            while type(t1)==pawff.Succ:
                t1=t1.term
                numsuccs+=1
            while type(t2)==pawff.Succ:
                t2=t2.term
                numsuccs+=1
            
            #x+0 -> x, and 0+x -> x
            if type(t1)==pawff.Zero:
                result=t2
            if type(t2)==pawff.Zero:
                result=t1
            else:
                result=pawff.Plus(t1,t2)
            
            for _ in range(numsuccs):
                result=pawff.Succ(result)
            return result
        case pawff.Times:
            t1=first_tnf(term.term1)
            t2=first_tnf(term.term2)
            
            #0*x -> 0, and x*0 -> 0
            if type(t1)==pawff.Zero:
                return t1
            if type(t2)==pawff.Zero:
                return t2
            
            #1*x -> x, and x*1 -> x
            if type(t1)==pawff.Succ:  # noqa: SIM102
                if type(t1.term)==pawff.Zero:
                    return t2
            if type(t2)==pawff.Succ:  # noqa: SIM102
                if type(t2.term)==pawff.Zero:
                    return t1
            
            return pawff.Times(t1,t2)

    assert(False) #Code unreachable

def first_normal_form(form:pawff.Form,recursive=True) -> pawff.Form:
    match type(form):
        case pawff.AtForm:
            if recursive:
                t1=first_tnf(form.term1)
                t2=first_tnf(form.term2)
            else:
                t1=form.term1
                t2=form.term2
            #S(x)=S(y) => x=y
            while type(t1)==pawff.Succ and type(t2)==pawff.Succ:
                t1=t1.term
                t2=t2.term
            return pawff.AtForm(t1,t2)
        case pawff.NotForm:
            if recursive:
                inner=first_normal_form(form.form,recursive)
            else:
                inner=form.form
            #NOT(NOT(F)) => F
            if type(inner)==pawff.NotForm:
                return inner.form
            return pawff.NotForm(inner)
        case pawff.AndForm:
            if recursive:
                inner_forms=[first_normal_form(iform) for iform in form.forms]
            else:
                inner_forms=form.forms
            #De Morgans Law: ~F & ~G => ~ (F|G)
            if all(type(iform)==pawff.NotForm for iform in inner_forms):
                return pawff.NotForm(pawff.OrForm(*(iform.form for iform in inner_forms)))
            return pawff.AndForm(*inner_forms)
        case pawff.OrForm:
            if recursive:
                inner_forms=[first_normal_form(iform) for iform in form.forms]
            else:
                inner_forms=form.forms
            #De Morgans Law: ~F | ~G => ~ (F&G)
            if all(type(iform)==pawff.NotForm for iform in inner_forms):
                return pawff.NotForm(pawff.AndForm(*(iform.form for iform in inner_forms)))
            return pawff.OrForm(*inner_forms)
        case pawff.ImpliesForm:
            #(F->G) => ~F | G
            return first_normal_form(pawff.OrForm(
                pawff.NotForm(form.form1),
                form.form2
            ))
        case pawff.ForAllForm:
            if recursive:
                inner=first_normal_form(form.form,recursive)
            else:
                inner=form.form

            #ForAll(x,F) => F, if F does not depend on x
            if form.var not in inner.vars_used():
                return inner
            
            #ForAll(x,~F) => ~Exists(x,F)
            if type(inner)==pawff.NotForm:
                #Do not recurse, as recursion would be redundant (inner already in 1NF)
                return pawff.NotForm(first_normal_form(
                    pawff.ExistsForm(form.var,inner.form),
                    False
                ))
            
            #ForAll(x,F&G) => ForAll(x,F)&ForAll(x,G)
            if type(inner)==pawff.AndForm:
                return pawff.AndForm(
                    *(first_normal_form(pawff.ForAllForm(form.var,iform),False) for iform in inner.forms)
                )
            
            return pawff.ForAllForm(form.var,inner)
        case pawff.ExistsForm:
            if recursive:
                inner=first_normal_form(form.form)
            else:
                inner=form.form

            #Exists(x,F) => F, if F does not depend on x
            if form.var not in inner.vars_used():
                return inner
            
            #Exists(x,~F) => ~ForAll(x,F)
            if type(inner)==pawff.NotForm:
                #Do not recurse, as recursion would be redundant (inner already in 1NF)
                return pawff.NotForm(first_normal_form(
                    pawff.ForAllForm(form.var,inner.form),
                    False
                ))

            #Exists(x,F|G) => Exists(x,F)|Exists(x,G)
            if type(inner)==pawff.OrForm:
                #Do not recurse, as recursion would be redundant (inner already in 1NF)
                return pawff.OrForm(
                    *(first_normal_form(pawff.ExistsForm(form.var,iform),False) for iform in inner.forms)
                )

            return pawff.ExistsForm(form.var,inner)

    assert(False) #Code unreachable
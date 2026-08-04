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

def first_normal_form(form:pawff.Form) -> pawff.Form:
    match type(form):
        case pawff.AtForm:
            t1=first_tnf(form.term1)
            t2=first_tnf(form.term2)
            #S(x)=S(y) => x=y
            while type(t1)==pawff.Succ and type(t2)==pawff.Succ:
                t1=t1.term
                t2=t2.term
            return pawff.AtForm(t1,t2)
        case pawff.NotForm:
            inner=first_normal_form(form.form)
            #NOT(NOT(F)) => F
            if type(inner)==pawff.NotForm:
                return inner.form
            return pawff.NotForm(inner)
        case pawff.AndForm:
            f1=first_normal_form(form.form1)
            f2=first_normal_form(form.form2)
            #De Morgans Law: ~F & ~G => ~ (F|G)
            if type(f1)==pawff.NotForm and type(f2)==pawff.NotForm:
                return pawff.NotForm(pawff.OrForm(f1.form,f2.form))
            return pawff.AndForm(f1,f2)
        case pawff.OrForm:
            f1=first_normal_form(form.form1)
            f2=first_normal_form(form.form2)
            #De Morgans Law: ~F | ~G => ~ (F&G)
            if type(f1)==pawff.NotForm and type(f2)==pawff.NotForm:
                return pawff.NotForm(pawff.AndForm(f1.form,f2.form))
            return pawff.OrForm(f1,f2)
        case pawff.ImpliesForm:
            f1=first_normal_form(form.form1)
            f2=first_normal_form(form.form2)
            #(F->G) => (~F)|G
            #However, taking the above simplification is not always desired
            #So we only take the above simplification if we can also perform a further simplification
            #so (~F -> G) => ~~F | G => F|G
            #or (F->~G) => ~F | ~G => ~ (F&G)
            if type(f1)==pawff.NotForm:
                return pawff.OrForm(f1.form,f2)
            if type(f2)==pawff.NotForm:
                return pawff.NotForm(pawff.AndForm(f1,f2.form))
            return pawff.ImpliesForm(f1,f2)
        case pawff.ForAllForm:
            inner=first_normal_form(form.form)

            #ForAll(x,F) => F, if F does not depend on x
            used_vars=set()
            inner.vars_used(used_vars)
            if form.var not in used_vars:
                return inner
            
            #ForAll(x,~F) => ~Exists(x,F)
            if type(inner)==pawff.NotForm:
                return pawff.NotForm(pawff.ExistsForm(form.var,inner))
            
            #ForAll(x,F&G) => ForAll(x,F)&ForAll(x,G)
            if type(inner)==pawff.AndForm:
                return pawff.AndForm(
                    pawff.ForAllForm(form.var,inner.form1),
                    pawff.ForAllForm(form.var,inner.form2)
                )
            
            return pawff.ForAllForm(form.var,inner)
        case pawff.ExistsForm:
            inner=first_normal_form(form.form)

            #Exists(x,F) => F, if F does not depend on x
            used_vars=set()
            inner.vars_used(used_vars)
            if form.var not in used_vars:
                return inner
            
            #Exists(x,~F) => ~ForAll(x,F)
            if type(inner)==pawff.NotForm:
                return pawff.NotForm(pawff.ForAllForm(form.var,inner))

            #Exists(x,F|G) => Exists(x,F)|Exists(x,G)
            if type(inner)==pawff.OrForm:
                return pawff.OrForm(
                    pawff.ExistsForm(form.var,inner.form1),
                    pawff.ExistsForm(form.var,inner.form2)
                )


            return pawff.ExistsForm(form.var,inner)

    assert(False) #Code unreachable
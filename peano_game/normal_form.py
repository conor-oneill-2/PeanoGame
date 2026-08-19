from typing import cast

from peano_game import pawff


#First TNF includes:
#  S(x)+y -> S(x+y), and x+S(y) -> S(x+y)
#  x+0 -> x, and 0+x -> x
#  0*x -> 0, and x*0 -> 0
#  1*x -> x, and x*1 -> x
#  Associativity of addition/multiplication
#It does not include any theorems that uses the distributive law
#or commutativity of addition/multiplications
#This will be solved in future
def first_tnf(term:pawff.Term)->pawff.Term:
    match type(term):
        case pawff.Zero | pawff.Var:
            return term
        case pawff.Succ:
            term=cast(pawff.Succ, term)
            return pawff.Succ(first_tnf(term.term))
        case pawff.Plus:
            term=cast(pawff.Plus, term)
            terms=[first_tnf(term) for term in term.terms]

            #S(x)+y -> S(x+y), and x+S(y)->S(x+y)
            numsuccs=0
            for i, term in enumerate(terms):
                final_term=term
                while type(final_term)==pawff.Succ:
                    final_term=final_term.term
                    numsuccs+=1

                terms[i]=final_term

            #x+0 -> x, and 0+x -> x
            terms=list(filter(lambda t: type(t)!=pawff.Zero, terms))

            #x+(y+z) -> x+y+z
            i=0
            lenterms=len(terms)
            while i<lenterms:
                current_term=terms[i]
                if isinstance(current_term, pawff.Plus):
                    terms.extend(current_term.terms)
                    del terms[i]
                    lenterms-=1
                else:
                    i+=1

            if len(terms)==0:
                result=pawff.Zero()
            elif len(terms)==1:
                result=terms[0]
            else:
                result=pawff.Plus(*terms)

            for _ in range(numsuccs):
                result=pawff.Succ(result)
            return result
        case pawff.Times:
            term=cast(pawff.Times, term)
            terms=[first_tnf(term) for term in term.terms]

            #0*x -> 0
            if any(type(t)==pawff.Zero for t in terms):
                return pawff.Zero()

            #1*x -> x, and x*1 -> x
            terms=list(filter(lambda t: eq_one(t),terms))

            #x*(y*z) -> x*y*z
            i=0
            lenterms=len(terms)
            while i<lenterms:
                current_term=terms[i]
                if isinstance(current_term, pawff.Times):
                    terms.extend(current_term.terms)
                    del terms[i]
                    lenterms-=1
                else:
                    i+=1

            if len(terms)==0:
                return pawff.Succ(pawff.Zero())
            if len(terms)==1:
                return terms[0]
            else:
                return pawff.Times(*terms)
        case _:
            raise ValueError(f"Unexpected term type: {type(term)}")


def eq_one(term:pawff.Term) -> bool:
    if type(term)==pawff.Succ:
        return type(term.term)==pawff.Zero
    return False

def first_normal_form(form:pawff.Form,recursive:bool=True) -> pawff.Form:
    match type(form):
        case pawff.AtForm:
            form=cast(pawff.AtForm, form)
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
            form=cast(pawff.NotForm, form)
            if recursive:
                inner=first_normal_form(form.form,recursive)
            else:
                inner=form.form
            #NOT(NOT(F)) => F
            if type(inner)==pawff.NotForm:
                return inner.form
            return pawff.NotForm(inner)
        case pawff.AndForm:
            form=cast(pawff.AndForm, form)
            if recursive:
                inner_forms=[first_normal_form(iform) for iform in form.forms]
            else:
                inner_forms=form.forms
            #De Morgans Law: ~F & ~G => ~ (F|G)
            if all(type(iform)==pawff.NotForm for iform in inner_forms):
                inner_forms=cast(list[pawff.NotForm], inner_forms)
                return pawff.NotForm(pawff.OrForm(*(iform.form for iform in inner_forms)))
            return pawff.AndForm(*inner_forms)
        case pawff.OrForm:
            form=cast(pawff.OrForm, form)
            if recursive:
                inner_forms=[first_normal_form(iform) for iform in form.forms]
            else:
                inner_forms=form.forms
            #De Morgans Law: ~F | ~G => ~ (F&G)
            if all(type(iform)==pawff.NotForm for iform in inner_forms):
                inner_forms=cast(list[pawff.NotForm], inner_forms)
                return pawff.NotForm(pawff.AndForm(*(iform.form for iform in inner_forms)))
            return pawff.OrForm(*inner_forms)
        case pawff.ImpliesForm:
            form=cast(pawff.ImpliesForm, form)
            #(F->G) => ~F | G
            return first_normal_form(pawff.OrForm(
                pawff.NotForm(form.form1),
                form.form2
            ))
        case pawff.ForAllForm:
            form=cast(pawff.ForAllForm, form)
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
            form=cast(pawff.ExistsForm, form)
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
        case _:
            raise ValueError(f"Unexpected form type: {type(form)}")

# pyright: reportImplicitOverride=false
# pyright: reportUnannotatedClassAttribute=false

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from math import prod
from typing import cast


class Term(ABC):
    #Assume a Term is not a number unless overloaded
    #  Zero overloads to True
    #  Succ(x) overloads to is_num(x)
    def is_num(self)->bool:
        return False

    def val(self)->int:
        raise TypeError(f"{self} is not a number.")

    @abstractmethod
    def eval(self)->int:
        pass

    @abstractmethod
    def vars_used(self) -> set[Var]:
        pass

    @abstractmethod
    def poly(self) -> Poly:
        pass

    @abstractmethod
    def simplify(self) -> Term:
        pass

    @abstractmethod
    def is_simplified(self) -> bool:
        pass

    @abstractmethod
    def __call__(self,**kwargs:Zero|Succ)->Term:
        pass

class Var(Term):
    #Vars are indexed as x_0, x_1, etc.
    def __init__(self,num:int):
        assert(num>=0)
        self.num=num
        self.vars:set[Var]={self}
        self.poly_cache=None

    def vars_used(self) -> set[Var]:
        return self.vars

    def eval(self)->int:
        raise TypeError(f"{self} is not enumerable.")

    def poly(self) -> Poly:
        #Cache result
        if self.poly_cache is None:
            ddictpoly:defaultdict[frozenset[tuple[Var,int]],int]=defaultdict(int)
            ddictpoly[frozenset([(self,1)])]=1 #Key: x_0^1, Val: coefficient=1
            self.poly_cache=Poly(ddictpoly)
        return self.poly_cache

    def simplify(self) -> Term:
        return self

    def is_simplified(self) -> bool:
        return True

    def __eq__(self,other:object):
        if type(other)!=Var:
            return False
        return self.num==other.num

    def __call__(self,**kwargs:Zero|Succ)->Term:
        if str(self) in kwargs:
            return kwargs[str(self)]
        return self

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return "x"+str(self.num)

class Zero(Term):
    def __init__(self):
        self.vars:set[Var]=set()
        self.poly_cache=None

    def vars_used(self) -> set[Var]:
        #Adds all vars used in subterms to result
        #But 0 has no subterms, so passes
        return self.vars

    def poly(self) -> Poly:
        if self.poly_cache is None:
            self.poly_cache=Poly(defaultdict(int))
        return self.poly_cache

    def simplify(self) -> Term:
        return self

    def is_simplified(self) -> bool:
        return True

    def is_num(self):
        return True

    def val(self):
        return 0

    def eval(self):
        return 0

    # def __eq__(self,other):
    #     return type(other)==Zero

    def __call__(self,**kwargs:Zero|Succ):
        return self

    # def __hash__(self):
    #     return hash(str(self))

    def __str__(self):
        return "0"

class Succ(Term):
    def __init__(self,term:Term):
        self.term=term
        self.is_num_cache=None
        self.val_cache=None
        self.eval_cache=None
        self.poly_cache=None
        self.vars=None
        self._is_simplified=self.term.is_simplified()

    def vars_used(self)->set[Var]:
        if self.vars is None:
            self.vars=self.term.vars_used()
        return self.vars

    def is_num(self):
        #Cache of result
        if self.is_num_cache is None:
            self.is_num_cache=self.term.is_num()
        return self.is_num_cache

    def val(self):
        if self.val_cache is not None:
            return self.val_cache

        try:
            self.val_cache=self.term.val()+1
            return self.val_cache
        except TypeError:
            raise TypeError(str(self)+" is not a number.")

    def eval(self)->int:
        # This is not the same as self.val
        # S(0+0) is simplified in val form
        # but S(0+0)=1 in eval form
        if self.eval_cache is None:
            self.eval_cache=self.term.eval()+1
        return self.eval_cache

    def poly(self) -> Poly:
        if self.poly_cache is None:
            inner_poly=self.term.poly()
            self.poly_cache=inner_poly+1
        return self.poly_cache

    def simplify(self) -> Term:
        if self._is_simplified:
            return self
        return Succ(self.term.simplify())

    def is_simplified(self) -> bool:
        return self._is_simplified

    # def __eq__(self,other):
    #     if type(other)!=Succ:
    #         return False
    #     if self.val_cache!=None:
    #         if not other.is_num():
    #             return False
    #         return self.val()==other.val()
    #     return self.term==other.term

    def __call__(self,**kwargs:Zero|Succ):
        return Succ(self.term(**kwargs))

    # def __hash__(self):
    #     return hash(str(self))

    def __str__(self):
        if self.is_num():
            return str(self.val())
        return "S("+str(self.term)+")"

class Plus(Term):
    def __init__(self,*terms:Term):
        self.terms=terms
        self.eval_cache=None
        self.poly_cache=None
        self.vars:None|set[Var]=None
        self._is_simplified=False

    def vars_used(self) -> set[Var]:
        if self.vars is None:
            self.vars=set()
            for term in self.terms:
                self.vars|=term.vars_used()
        return self.vars

    # def is_num(self):
    #     return False
    #     #return is_num(self.term1) and is_num(self.term2)

    # def val(self):
    #     #val is used for the purposes of simplifying lexed expressions into readable form
    #     #so S(S(0)) becomes 2
    #     #2+2 is simplified - we are not converting it to 4, because that is the job of the parser, not the lexer.
    #     #If you want 2+2 to be converted to 4, use eval instead.
    #     raise ValueError("Plus Expression is not Natural Number Expression.")
    #     # if is_num(self.term):
    #     #     return self.term1+self.term2
    #     # raise ValueError(str(self)+" is not a number.")

    def eval(self)->int:
        if self.eval_cache is None:
            self.eval_cache=sum(term.eval() for term in self.terms)
        return self.eval_cache

    def poly(self) -> Poly:
        if self.poly_cache is None:
            self.poly_cache=Poly(defaultdict(int))
            for term in self.terms:
                self.poly_cache+=term.poly()
        return self.poly_cache

    # def __eq__(self,other):
    #     if type(other)!=Plus:
    #         return False
    #     return self.term1==other.term1 and self.term2==other.term2

    def is_simplified(self) -> bool:
        return self._is_simplified

    def simplify(self) -> Term:
        if self._is_simplified:
            return self
        
        terms=[term.simplify() for term in self.terms]

        #S(x)+y -> S(x+y), and x+S(y)->S(x+y)
        numsuccs=0
        for i, term in enumerate(terms):
            final_term=term
            while type(final_term)==Succ:
                final_term=final_term.term
                numsuccs+=1

            terms[i]=final_term

        #x+0 -> x, and 0+x -> x
        terms=list(filter(lambda t: type(t)!=Zero, terms))

        #x+(y+z) -> x+y+z
        i=0
        lenterms=len(terms)
        while i<lenterms:
            current_term=terms[i]
            if isinstance(current_term, Plus):
                terms.extend(current_term.terms)
                del terms[i]
                lenterms-=1
            else:
                i+=1

        if len(terms)==0:
            result=Zero()
        elif len(terms)==1:
            result=terms[0]
        else:
            result=Plus(*terms)
            result._is_simplified=True

        for _ in range(numsuccs):
            result=Succ(result)
        return result
    
    def __call__(self,**kwargs:Zero|Succ):
        return Plus(*(term(**kwargs) for term in self.terms))

    def __str__(self):
        return "+".join(f"({term})" for term in self.terms)

class Times(Term):
    def __init__(self,*terms:Term):
        self.terms=terms
        self.eval_cache=None
        self.poly_cache=None
        self.vars:None|set[Var]=None
        self._is_simplified=False

    def vars_used(self) -> set[Var]:
        if self.vars is None:
            self.vars=set()
            for term in self.terms:
                self.vars|=term.vars_used()
        return self.vars

    def eval(self)->int:
        if self.eval_cache is None:
            self.eval_cache=prod(term.eval() for term in self.terms)
        return self.eval_cache

    def poly(self)->Poly:
        if self.poly_cache is None:
            poly_ddict:defaultdict[frozenset[tuple[Var,int]],int]=defaultdict(int)
            poly_ddict[frozenset()]=succ_form(1)
            self.poly_cache=Poly(poly_ddict)
            for term in self.terms:
                self.poly_cache*=term.poly()
        return self.poly_cache

    def is_simplified(self) -> bool:
        return self._is_simplified

    def simplify(self) -> Term:
        if self._is_simplified:
            return self
        
        terms=[term.simplify() for term in self.terms]

        #0*x -> 0
        if any(type(t)==Zero for t in terms):
            return Zero()

        #1*x -> x, and x*1 -> x
        terms=list(filter(lambda t: eq_one(t),terms))

        #x*(y*z) -> x*y*z
        i=0
        lenterms=len(terms)
        while i<lenterms:
            current_term=terms[i]
            if isinstance(current_term, Times):
                terms.extend(current_term.terms)
                del terms[i]
                lenterms-=1
            else:
                i+=1

        if len(terms)==0:
            return Succ(Zero())
        if len(terms)==1:
            return terms[0]
        else:
            result=Times(*terms)
            result._is_simplified=True
            return result

    # def __eq__(self,other):
    #     if type(other)!=Times:
    #         return False
    #     return self.term1==other.term1 and self.term2==other.term2

    def __call__(self,**kwargs:Zero|Succ):
        return Times(*(term(**kwargs) for term in self.terms))

    def __str__(self):
        return "*".join(f"({term})" for term in self.terms)


class Form(ABC):
    #Given a set, add all vars used in the formula into the set
    @abstractmethod
    def vars_used(self)->set[Var]:
        pass

    @abstractmethod
    def is_simplified(self)->bool:
        pass

    @abstractmethod
    def simplify(self)->Form:
        pass
    

class AtForm(Form):
    def __init__(self,term1:Term,term2:Term):
        self.term1=term1
        self.term2=term2
        self.vars=None
        self._is_simplified=False

    def vars_used(self)->set[Var]:
        if self.vars is None:
            self.vars=self.term1.vars_used()|self.term2.vars_used()
        return self.vars

    # def __eq__(self,other):
    #     if type(other)!=AtForm:
    #         return False
    #     return self.term1==other.term1 and self.term2==other.term2

    # def __call__(self,**kwargs):
    #     return AtForm(self.term1(**kwargs),self.term2(**kwargs))

    def is_simplified(self)->bool:
        return self._is_simplified

    def simplify(self)->Form:
        if self._is_simplified:
            return self
        t1=self.term1.simplify()
        t2=self.term2.simplify()
        #S(x)=S(y) => x=y
        while type(t1)==Succ and type(t2)==Succ:
            t1=t1.term
            t2=t2.term
        result=AtForm(t1,t2)
        result._is_simplified=True
        return result


    def __str__(self):
        return f"{self.term1}={self.term2}"

class NotForm(Form):
    def __init__(self,form:Form):
        self.form=form
        self.vars=None
        self._is_simplified=False

    def vars_used(self)->set[Var]:
        if self.vars is None:
            self.vars=self.form.vars_used()
        return self.vars

    # def __eq__(self,other):
    #     if type(other)!=NotForm:
    #         return False
    #     return self.form==other.form

    # def __call__(self,**kwargs):
    #     return NotForm(self.form(**kwargs))
    def is_simplified(self)->bool:
        return self._is_simplified

    def simplify(self)->Form:
        if self._is_simplified:
            return self
        inner=self.form.simplify()
        #NOT(NOT(F)) => F
        if type(inner)==NotForm:
            return inner.form
        result=NotForm(inner)
        result._is_simplified=True
        return result

    def __str__(self):
        return f"¬({self.form})"

class AndForm(Form):
    def __init__(self,*forms:Form):
        #Tuple conversion to ensure immutability
        #and prevent annoying bugs, at a small cost to speed
        #If you want to modify the forms (for normal form), use a new constructor
        self.forms=tuple(forms)
        self.vars:None|set[Var]=None
        self._is_simplified=False

    def vars_used(self)->set[Var]:
        if self.vars is None:
            self.vars=set()
            for form in self.forms:
                self.vars|=form.vars_used()
        return self.vars

    # def __eq__(self,other):
    #     if type(other)!=AndForm:
    #         return False
    #     return self.form1==other.form1 and self.form2==other.form2

    # def __call__(self,**kwargs):
    #     return AndForm(self.form1(**kwargs),self.form2(**kwargs))
    def is_simplified(self)->bool:
        return self._is_simplified

    def simplify(self)->Form:
        if self._is_simplified:
            return self
        inner_forms=[iform.simplify() for iform in self.forms]
        #De Morgans Law: ~F & ~G => ~ (F|G)
        if all(type(iform)==NotForm for iform in inner_forms):
            inner_forms=cast(list[NotForm], inner_forms)
            result=NotForm(OrForm(*(iform.form for iform in inner_forms)))
            result._is_simplified=True  # pyright: ignore[reportPrivateUsage]
            return result
        result=AndForm(*inner_forms)
        result._is_simplified=True
        return result
        
    def __str__(self):
        return f"{'∧'.join(f"({x})" for x in self.forms)}"

class OrForm(Form):
    def __init__(self,*forms:Form):
        self.forms=tuple(forms)
        self.vars:None|set[Var]=None
        self._is_simplified=False

    def vars_used(self)->set[Var]:
        if self.vars is None:
            self.vars=set()
            for form in self.forms:
                self.vars|=form.vars_used()
        return self.vars

    # def __eq__(self,other):
    #     if type(other)!=OrForm:
    #         return False
    #     return self.form1==other.form1 and self.form2==other.form2

    # def __call__(self,**kwargs):
    #     return OrForm(self.form1(**kwargs),self.form2(**kwargs))
    def is_simplified(self)->bool:
        return self._is_simplified

    def simplify(self)->Form:
        if self._is_simplified:
            return self
        inner_forms=[iform.simplify() for iform in self.forms]
        #De Morgans Law: ~F | ~G => ~ (F&G)
        if all(type(iform)==NotForm for iform in inner_forms):
            inner_forms=cast(list[NotForm], inner_forms)
            result=NotForm(AndForm(*(iform.form for iform in inner_forms)))
            result._is_simplified=True  # pyright: ignore[reportPrivateUsage]
            return result
        result=OrForm(*inner_forms)
        result._is_simplified=True
        return result

    
    def __str__(self):
        return f"{'∨'.join(f"({x})" for x in self.forms)}"

class ImpliesForm(Form):
    def __init__(self,form1:Form,form2:Form):
        self.form1=form1
        self.form2=form2
        self.vars=None
        self._is_simplified=False

    def is_simplified(self)->bool:
        return self._is_simplified

    def simplify(self)->Form:
        if self._is_simplified:
            return self
        #(F->G) => ~F | G
        return OrForm(
            NotForm(self.form1),
            self.form2
        ).simplify()

    
    def vars_used(self)->set[Var]:
        if self.vars is None:
            self.vars=self.form1.vars_used()|self.form2.vars_used()
        return self.vars

    # def __eq__(self,other):
    #     if type(other)!=ImpliesForm:
    #         return False
    #     return self.form1==other.form1 and self.form2==other.form2

    # def __call__(self,**kwargs):
    #     return ImpliesForm(self.form1(**kwargs),self.form2(**kwargs))

    def __str__(self):
        return f"({self.form1})→({self.form2})"

class ForAllForm(Form):
    def __init__(self,var:Var,form:Form):
        self.var=var
        self.form=form
        self.vars=None
        self._is_simplified=False

    #vars_used is used to determine if ForAllForm(x,F)/ExistsForm(x,F)
    #can be reduced to F due to no dependence on x
    #As such, the variable x should not be counted as a used variable
    def vars_used(self)->set[Var]:
        if self.vars is None:
            self.vars=self.form.vars_used()
        return self.vars

    # def __eq__(self,other):
    #     if type(other)!=ForAllForm:
    #         return False
    #     return self.var==other.var and self.form==other.form

    # def __call__(self,**kwargs):
    #     if str(self.var) in kwargs:
    #         return self.form(**kwargs)
    #     return ForAllForm(self.var,self.form(**kwargs))

    def is_simplified(self)->bool:
        return self._is_simplified

    def simplify(self)->Form:
        if self.is_simplified():
            return self
        
        inner=self.form.simplify()

        #ForAll(x,F) => F, if F does not depend on x
        if self.var not in inner.vars_used():
            return inner

        #ForAll(x,~F) => ~Exists(x,F)
        if type(inner)==NotForm:
            result=NotForm(ExistsForm(self.var,inner.form).simplify())
            result._is_simplified=True  # pyright: ignore[reportPrivateUsage]
            return result

        #ForAll(x,F&G) => ForAll(x,F)&ForAll(x,G)
        if type(inner)==AndForm:
            result=AndForm(
                *(ForAllForm(self.var,iform).simplify() for iform in inner.forms)
            )
            result._is_simplified=True  # pyright: ignore[reportPrivateUsage]
            return result

        result=ForAllForm(self.var,inner)
        result._is_simplified=True
        return result


    def __str__(self):
        return f"∀{self.var} ({self.form})"

class ExistsForm(Form):
    def __init__(self,var:Var,form:Form):
        self.var=var
        self.form=form
        self.vars=None
        self._is_simplified=False

    #vars_used is used to determine if ForAllForm(x,F)/ExistsForm(x,F)
    #can be reduced to F due to no dependence on x
    #As such, the variable x should not be counted as a used variable
    def vars_used(self)->set[Var]:
        if self.vars is None:
            self.vars=self.form.vars_used()
        return self.vars

    # def __eq__(self,other):
    #     if type(other)!=ExistsForm:
    #         return False
    #     return self.var==other.var and self.form==other.form

    # def __call__(self,**kwargs):
    #     if self.var in kwargs:
    #         return self.form(**kwargs)
    #     return ExistsForm(self.var,self.form(**kwargs))

    def is_simplified(self)->bool:
        return self._is_simplified

    def simplify(self)->Form:
        if self._is_simplified:
            return self
        
        inner=self.form.simplify()

        #Exists(x,F) => F, if F does not depend on x
        if self.var not in inner.vars_used():
            return inner

        #Exists(x,~F) => ~ForAll(x,F)
        if type(inner)==NotForm:
            #Do not recurse, as recursion would be redundant (inner already in 1NF)
            result=NotForm(
                ForAllForm(self.var,inner.form).simplify()
            )
            result._is_simplified=True  # pyright: ignore[reportPrivateUsage]
            return result

        #Exists(x,F|G) => Exists(x,F)|Exists(x,G)
        if type(inner)==OrForm:
            #Do not recurse, as recursion would be redundant (inner already in 1NF)
            result=OrForm(
                *(ExistsForm(self.var,iform).simplify() for iform in inner.forms)
            )
            result._is_simplified=True  # pyright: ignore[reportPrivateUsage]
            return result

        result=ExistsForm(self.var,inner)
        result._is_simplified=True
        return result

    
    def __str__(self):
        return f"∃{self.var} ({self.form})"

#Take an int n and return a S(S(...S(0))) corresponding to n
def succ_form(n:int):
    assert(n>=0)
    if n==0:
        return Zero()
    return Succ(succ_form(n-1))

def eq_one(term:Term) -> bool:
    if type(term)==Succ:
        return type(term.term)==Zero
    return False

def dictsum(d1:frozenset[tuple[Var,int]],d2:frozenset[tuple[Var,int]])->frozenset[tuple[Var,int]]:
    result:set[tuple[Var,int]]=set()
    for k,v in d1:
        result.add((k,v))
    for k,v in d2:
        for k2,v2 in result:
            if k==k2:
                result.remove((k2,v2))
                val=v2
        val=0
        result.add((k,v+val))
    return frozenset(result)

class Poly:
    def __init__(self,poly:defaultdict[frozenset[tuple[Var,int]],int]):
        self.poly=poly

    def __eq__(self,other:object) -> bool:
        if type(other)!=Poly:
            return False
        return self.poly==other.poly

    def __add__(self,other:int|Poly)->Poly:
        if type(other)==int:
            poly=self.poly.copy()
            poly[frozenset()]+=other
            return Poly(poly)
        assert(type(other)==Poly)
        poly=self.poly.copy()
        for k,v in other.poly.items():
            poly[k]+=v
        return Poly(poly)

    def __mul__(self,other:int|Poly)->Poly:
        if type(other)==int:
            poly=self.poly.copy()
            for k in poly:
                poly[k]*=other
            return Poly(poly)
        assert(type(other)==Poly)
        poly:defaultdict[frozenset[tuple[Var,int]],int]=defaultdict(int)
        for k1,v1 in self.poly.items():
            for k2,v2 in other.poly.items():
                poly[dictsum(k1,k2)]+=v1*v2
        return Poly(poly)

    def __str__(self):
        return str(self.poly)

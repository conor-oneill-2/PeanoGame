from abc import ABC, abstractmethod
from collections import defaultdict

from peano_game.poly import Poly


class Term:
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
    def vars_used(self,result:set) -> None:
        pass

    @abstractmethod
    def poly(self) -> Poly:
        pass

class Var(Term):
    #Vars are indexed as x_0, x_1, etc.
    def __init__(self,num:int):
        assert(num>=0)
        self.num=num
        self.poly_cache=None
    
    def vars_used(self,result:set) -> None:
        if self not in result:
            result.add(self)
    
    def eval(self)->int:
        raise TypeError(f"{self} is not enumerable.")
    
    def __eq__(self,other):
        if type(other)!=Var:
            return False
        return self.num==other.num

    def poly(self) -> Poly:
        #Cache result
        if self.poly_cache!=None:
            return self.poly_cache
        
        ddictpoly=defaultdict(int)
        ddictpoly[{(self,1)}]=1
        self.poly_cache=Poly(ddictpoly)
        return self.poly_cache
    
    # def __call__(self,**kwargs):
    #     if str(self) in kwargs:
    #         return kwargs[str(self)]
    #     return self
    
    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return "x"+str(self.num)

class Zero(Term):
    #Adds all vars used in subterms to result
    #But 0 has no subterms, so passes
    def vars_used(self,result:set) -> None:
        pass
    
    def poly(self) -> Poly:
        return Poly(defaultdict(int))

    # def can_eval(self):
    #     return True

    def is_num(self):
        return True

    def val(self):
        return 0

    def eval(self):
        return 0
    
    # def __eq__(self,other):
    #     return type(other)==Zero
    
    # def __call__(self,**kwargs):
    #     return self
    
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
    
    def vars_used(self,result:set)->None:
        self.vars_used(result)
    
    # def can_eval(self):
    #     return self.term.can_eval()
    
    def is_num(self):
        #Cache of result
        if self.is_num_cache==None:
            self.is_num_cache=self.term.is_num()        
        return self.is_num_cache
    
    def val(self):
        if self.val_cache!=None:
            return self.val_cache
        
        try:
            self.val_cache=self.term.val()+1
            return self.val_cache
        except TypeError:
            raise TypeError(str(self)+" is not a number.")
    
    # This is not the same as self.val
    # S(0+0) is simplified in val form
    # but S(0+0)=1 in eval form
    def eval(self)->int:
        if self.eval_cache!=None:
            return self.eval_cache
        
        self.eval_cache=self.term.eval()+1
        return self.eval_cache

    def poly(self) -> Poly:
        if self.poly_cache!=None:
            return self.poly_cache

        inner_poly=self.term.poly()
        self.poly_cache=inner_poly+1
        return self.poly_cache
            
        
    # def __eq__(self,other):
    #     if type(other)!=Succ:
    #         return False
    #     if self.val_cache!=None:
    #         if not other.is_num():
    #             return False
    #         return self.val()==other.val()
    #     return self.term==other.term
    
    # def __call__(self,**kwargs):
    #     return Succ(self.term(**kwargs))
    
    # def __hash__(self):
    #     return hash(str(self))

    def __str__(self):
        if self.is_num():
            return str(self.val())
        return "S("+str(self.term)+")"

class Plus(Term):
    def __init__(self,term1:Term,term2:Term):
        self.term1=term1
        self.term2=term2
        self.eval_cache=None
    
    def vars_used(self,result:set) -> None:
        self.term1.vars_used(result)
        self.term2.vars_used(result)
    
    # def can_eval(self):
    #     return self.term1.can_eval() and self.term2.can_eval()
    
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
        if self.eval_cache==None:
            self.eval_cache=self.term1.eval()+self.term2.eval()
        return self.eval_cache
    
    # def __eq__(self,other):
    #     if type(other)!=Plus:
    #         return False
    #     return self.term1==other.term1 and self.term2==other.term2
    
    # def __call__(self,**kwargs):
    #     return Plus(self.term1(**kwargs),self.term2(**kwargs))

    def __str__(self):
        return str(self.term1)+"+"+str(self.term2)

class Times(Term):
    def __init__(self,term1:Term,term2:Term):
        self.term1=term1
        self.term2=term2
        self.eval_cache=None
    
    def vars_used(self,result:set) -> None:
        self.term1.vars_used(result)
        self.term2.vars_used(result)
    
    # def can_eval(self):
    #     return self.term1.can_eval() and self.term2.can_eval()
    
    # def is_num(self):
    #     return False
    #     #return is_num(self.term1) and is_num(self.term2)
    
    # def val(self):
    #     #val is used for the purposes of simplifying lexed expressions into readable form
    #     #so S(S(0)) becomes 2
    #     #If you want 2+2 to be converted to 4, use eval instead.
    #     raise ValueError("Times term is not a natural number expression.")
    #     # if is_num(self.term):
    #     #     return self.term1*self.term2
    #     # raise ValueError(str(self)+" is not a number.")
    
    def eval(self)->int:
        if self.eval_cache==None:
            self.eval_cache=self.term1.eval()*self.term2.eval()
        return self.eval_cache
    
    # def __eq__(self,other):
    #     if type(other)!=Times:
    #         return False
    #     return self.term1==other.term1 and self.term2==other.term2
    
    # def __call__(self,**kwargs):
    #     return Times(self.term1(**kwargs),self.term2(**kwargs))
    
    def __str__(self):
        t1str=str(self.term1)
        if type(self.term1)==Plus:
            t1str="("+t1str+")"
        t2str=str(self.term2)
        if type(self.term2)==Plus:
            t2str="("+t2str+")"
        return t1str+"*"+t2str


class Form(ABC):
    #Given a set, add all vars used in the formula into the set
    @abstractmethod
    def vars_used(self,result:set)->None:
        pass

class AtForm(Form):
    def __init__(self,term1:Term,term2:Term):
        self.term1=term1
        self.term2=term2
    
    def vars_used(self,result:set)->None:
        self.term1.vars_used(result)
        self.term2.vars_used(result)
    
    # def __eq__(self,other):
    #     if type(other)!=AtForm:
    #         return False
    #     return self.term1==other.term1 and self.term2==other.term2
    
    # def __call__(self,**kwargs):
    #     return AtForm(self.term1(**kwargs),self.term2(**kwargs))

    def __str__(self):
        return f"{self.term1}={self.term2}"

class NotForm(Form):
    def __init__(self,form:Form):
        self.form=form
    
    def vars_used(self,result:set)->None:
        self.form.vars_used(result)
    
    # def __eq__(self,other):
    #     if type(other)!=NotForm:
    #         return False
    #     return self.form==other.form
    
    # def __call__(self,**kwargs):
    #     return NotForm(self.form(**kwargs))
    
    def __str__(self):
        return f"¬({self.form})"

class AndForm(Form):
    def __init__(self,form1:Form,form2:Form):
        self.form1=form1
        self.form2=form2

    def vars_used(self,result:set)->None:
        self.form1.vars_used(result)
        self.form2.vars_used(result)
    
    # def __eq__(self,other):
    #     if type(other)!=AndForm:
    #         return False
    #     return self.form1==other.form1 and self.form2==other.form2

    # def __call__(self,**kwargs):
    #     return AndForm(self.form1(**kwargs),self.form2(**kwargs))

    def __str__(self):
        return f"({self.form1})∧({self.form2})"

class OrForm(Form):
    def __init__(self,form1:Form,form2:Form):
        self.form1=form1
        self.form2=form2

    def vars_used(self,result:set)->None:
        self.form1.vars_used(result)
        self.form2.vars_used(result)

    # def __eq__(self,other):
    #     if type(other)!=OrForm:
    #         return False
    #     return self.form1==other.form1 and self.form2==other.form2

    # def __call__(self,**kwargs):
    #     return OrForm(self.form1(**kwargs),self.form2(**kwargs))

    def __str__(self):
        return f"({self.form1})∨({self.form2})"

class ImpliesForm(Form):
    def __init__(self,form1:Form,form2:Form):
        self.form1=form1
        self.form2=form2

    def vars_used(self,result:set)->None:
        self.form1.vars_used(result)
        self.form2.vars_used(result)

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

    #vars_used is used to determine if ForAllForm(x,F)/ExistsForm(x,F)
    #can be reduced to F due to no dependence on x
    #As such, the variable x should not be counted as a used variable
    def vars_used(self,result:set)->None:
        self.form.vars_used(result)

    # def __eq__(self,other):
    #     if type(other)!=ForAllForm:
    #         return False
    #     return self.var==other.var and self.form==other.form

    # def __call__(self,**kwargs):
    #     if str(self.var) in kwargs:
    #         return self.form(**kwargs)
    #     return ForAllForm(self.var,self.form(**kwargs))

    def __str__(self):
        return f"∀{self.var} ({self.form})"

class ExistsForm(Form):
    def __init__(self,var:Var,form:Form):
        self.var=var
        self.form=form
        self.vars=None
        self.free=None

    #vars_used is used to determine if ForAllForm(x,F)/ExistsForm(x,F)
    #can be reduced to F due to no dependence on x
    #As such, the variable x should not be counted as a used variable
    def vars_used(self,result:set)->None:
        self.form.vars_used(result)

    # def __eq__(self,other):
    #     if type(other)!=ExistsForm:
    #         return False
    #     return self.var==other.var and self.form==other.form

    # def __call__(self,**kwargs):
    #     if self.var in kwargs:
    #         return self.form(**kwargs)
    #     return ExistsForm(self.var,self.form(**kwargs))
    
    def __str__(self):
        return f"∃{self.var} ({self.form})"

#Take an int n and return a S(S(...S(0))) corresponding to n
def succ_form(n:int):
    assert(n>=0)
    if n==0:
        return Zero()
    return Succ(succ_form(n-1))

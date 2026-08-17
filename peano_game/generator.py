from math import isqrt
from typing import cast

from peano_game import pawff


#A bijective function k->(x,y) where k,x,y are natural numbers (x may be now less than y)
def bij(k:int):
    assert(k>=0)
    xplusy=(isqrt(8*k+5)-1)//2
    k0=(xplusy*(xplusy+1))//2
    y=k-k0
    x=xplusy-y
    return (x,y)

#Inverse of bij, sends (x,y)-> k
def bij_inv(x:int,y:int):
    assert(x>=0 and y>=0)
    xplusy=x+y
    #Smallest k with correct xplusy val
    k0=(xplusy*(xplusy+1))//2
    return y+k0

def term_wff(godel_num:int,num_vars_used:int) -> pawff.Term:
    if godel_num==0:
        return pawff.Zero()
    if godel_num<=num_vars_used:
        return pawff.Var(godel_num-1)
    #remainder
    rem=godel_num-num_vars_used-1
    match rem%3:  # pyright: ignore[reportMatchNotExhaustive]
        case 0:
            return pawff.Succ(term_wff(rem//3,num_vars_used))
        case 1:
            x,y=bij(rem//3)
            return pawff.Plus(
                term_wff(x,num_vars_used),
                term_wff(y,num_vars_used)
            )
        case 2:
            x,y=bij(rem//3)
            return pawff.Times(
                term_wff(x,num_vars_used),
                term_wff(y,num_vars_used)
            )

    assert(False) #Code unreachable

def godel_term(wff:pawff.Term,num_vars_used:int) -> int:
    match type(wff):
        case pawff.Zero:
            return 0
        case pawff.Var:
            wff=cast(pawff.Var, wff)
            assert(wff.num<num_vars_used)
            return wff.num+1
        case pawff.Succ:
            wff=cast(pawff.Succ, wff)
            sub=godel_term(wff.term,num_vars_used)
            return 3*sub+num_vars_used+1
        case pawff.Plus:
            wff=cast(pawff.Plus, wff)
            assert(len(wff.terms)==2)
            sub1=godel_term(wff.terms[0],num_vars_used)
            sub2=godel_term(wff.terms[1],num_vars_used)
            return 3*bij_inv(sub1,sub2)+num_vars_used+2
        case pawff.Times:
            wff=cast(pawff.Times, wff)
            assert(len(wff.terms)==2)
            sub1=godel_term(wff.terms[0],num_vars_used)
            sub2=godel_term(wff.terms[1],num_vars_used)
            return 3*bij_inv(sub1,sub2)+num_vars_used+3
        case _:
            raise ValueError(f"Unexpected term type: {type(wff)}")

def wff(godel_num:int,num_vars_used:int=0) -> pawff.Form:
    assert(godel_num>=0)
    match godel_num%7:  # pyright: ignore[reportMatchNotExhaustive]
        case 0:
            x,y=bij(godel_num//7)
            return pawff.AtForm(term_wff(x,num_vars_used),term_wff(y,num_vars_used))
        case 1:
            return pawff.NotForm(wff(godel_num//7,num_vars_used))
        case 2:
            #Theoretically, since x and y is symmetric around x and y, you could assume godel(x)>=godel(y)
            x,y=bij(godel_num//7)
            return pawff.AndForm(wff(x,num_vars_used),wff(y,num_vars_used))
        case 3:
            #Theoretically, x and y are symmetric
            x,y=bij(godel_num//7)
            return pawff.OrForm(wff(x,num_vars_used),wff(y,num_vars_used))
        case 4:
            x,y=bij(godel_num//7)
            return pawff.ImpliesForm(wff(x,num_vars_used),wff(y,num_vars_used))
        case 5:
            return pawff.ForAllForm(
                pawff.Var(num_vars_used),
                wff(godel_num//7,num_vars_used+1))
        case 6:
            return pawff.ExistsForm(
                pawff.Var(num_vars_used),
                wff(godel_num//7,num_vars_used+1)
            )

    assert(False) #Code unreachable

def godel(wff:pawff.Form,num_vars_used:int=0) -> int:
    match type(wff):
        case pawff.AtForm:
            wff=cast(pawff.AtForm, wff)
            k=bij_inv(
                godel_term(wff.term1,num_vars_used),
                godel_term(wff.term2,num_vars_used)
            )
            return 7*k
        case pawff.NotForm:
            wff=cast(pawff.NotForm, wff)
            return 7*godel(wff.form,num_vars_used)+1
        case pawff.AndForm:
            wff=cast(pawff.AndForm, wff)
            assert(len(wff.forms)==2)
            k=bij_inv(
                godel(wff.forms[0],num_vars_used),
                godel(wff.forms[1],num_vars_used)
            )
            return 7*k+2
        case pawff.OrForm:
            wff=cast(pawff.OrForm, wff)
            assert(len(wff.forms)==2)
            k=bij_inv(
                godel(wff.forms[0],num_vars_used),
                godel(wff.forms[1],num_vars_used)
            )
            return 7*k+3
        case pawff.ImpliesForm:
            wff=cast(pawff.ImpliesForm, wff)
            k=bij_inv(
                godel(wff.form1,num_vars_used),
                godel(wff.form2,num_vars_used)
            )
            return 7*k+4
        case pawff.ForAllForm:
            wff=cast(pawff.ForAllForm, wff)
            assert(wff.var.num==num_vars_used)
            return 7*godel(wff.form,num_vars_used+1)+5
        case pawff.ExistsForm:
            wff=cast(pawff.ExistsForm, wff)
            assert(wff.var.num==num_vars_used)
            return 7*godel(wff.form,num_vars_used+1)+6
        case _:
            raise ValueError(f"Unexpected form type: {type(wff)}")

if __name__=="__main__":
    for i in range(100):
        print(wff(i))
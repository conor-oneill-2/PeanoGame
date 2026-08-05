from peano_game.decider import decider
from peano_game.generator import wff
from peano_game.normal_form import first_normal_form
from peano_game.ternary import Ternary


def iterate_until_unknown():
    i=0
    while True:
        form=wff(i)
        result=decider(form)
        print(i,form,result)
        if result==Ternary.UNKNOWN:
            break
        i+=1

def detailed_decider(godel_num:int):
    form=wff(godel_num)
    print(form)
    fnf=first_normal_form(form)
    print(fnf)
    result=decider(form)
    print(result)
    
if __name__=="__main__":
    detailed_decider(1392)
    #iterate_until_unknown()

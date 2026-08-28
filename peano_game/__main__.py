from peano_game.decider import decider
from peano_game.generator import wff
from peano_game.ternary import Ternary


def iterate_until_unknown():
    i:int=0
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
    simplified=form.simplify()
    print(simplified)
    result=decider(form) #Unsimplified - decider will simplify if necessary
    print(result)
    
if __name__=="__main__":
    detailed_decider(110)
    #iterate_until_unknown()

from peano_game.decider import decider, set_decider
from peano_game.generator import wff
from peano_game.natset import UnknownSet
from peano_game.set_generator import set_wff
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

def set_iterate_until_unknown():
    i:int=0
    while True:
        form=set_wff(i)
        result=set_decider(form)
        print(i,form,result)
        if result==UnknownSet():
            break
        i+=1

def detailed_decider(godel_num:int):
    form=wff(godel_num)
    print(form)
    simplified=form.simplify()
    print(simplified)
    result=decider(form) #Unsimplified - decider will simplify if necessary
    print(result)

def set_detailed_decider(godel_num:int):
    form=set_wff(godel_num)
    print(form)
    result=set_decider(form)
    print(result)
    
if __name__=="__main__":
    # detailed_decider(42243)
    iterate_until_unknown()

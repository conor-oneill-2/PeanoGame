from peano_game.decider import decider
from peano_game.generator import wff
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

if __name__=="__main__":
    # form=wff(54)
    # print(form)
    # result=decider(form)
    iterate_until_unknown()
from peano_game.generator import *


def test_bij():
    for i in range(1000):
        assert(bij_inv(*bij(i))==i)

def test_bij_inv():
    for i in range(100):
        for j in range(100):
            assert(bij(bij_inv(i,j))==(i,j))

def test_term():
    for i in range(10000):
        for j in range(10):
            wff=term_wff(i,j)
            godel_i=godel_term(wff,j)
            assert(godel_i==i)

def test_form():
    for i in range(100000):
        for j in range(3):
            wff_i=wff(i,j)
            godel_i=godel(wff_i,j)
            assert(godel_i==i)

from __future__ import annotations

from collections import defaultdict

from peano_game.pawff import Var


class Poly:
    def __init__(self,poly:defaultdict[set[tuple[Var,int]],int]):
        self.poly=poly
        
    def __eq__(self,other):
        return self.poly==other.poly

    def __add__(self,other:int|Poly)->Poly:
        if type(other)==int:
            poly=self.poly.copy()
            poly[set()]+=other
            return Poly(poly)
        assert(type(other)==Poly)
        poly=self.poly.copy()
        for k,v in other.poly.items():
            poly[k]+=v
        return Poly(poly)
    
    def __str__(self):
        return str(self.poly)
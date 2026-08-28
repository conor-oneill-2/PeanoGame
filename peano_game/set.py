# pyright: reportImplicitOverride=false
# pyright: reportUnannotatedClassAttribute=false

from abc import ABC, abstractmethod
from typing import final

from peano_game.pawff import Form, Var
from peano_game.ternary import Ternary


class SetExpr:
    def __init__(self,var:Var,form:Form):
        self.var=var
        self.form=form

    def simplify(self) -> "SetExpr":
        return SetExpr(self.var, self.form.simplify())

    def __str__(self)->str:
        return f"SetExpr({self.var},{self.form})"

class NatSet(ABC):
    @abstractmethod
    def __contains__(self, item:int)->Ternary:
        pass

    @abstractmethod
    def simplify(self)->"NatSet":
        pass

    @abstractmethod
    def is_empty(self)->Ternary:
        pass

    @abstractmethod
    def is_full(self)->Ternary:
        pass

    @abstractmethod
    def complement(self)->"NatSet":
        pass
    

class FiniteNatSet(NatSet):
    def __init__(self, items:set[int]):
        self._items = items

    def __contains__(self, item:int)->Ternary:
        return Ternary.TRUE if item in self._items else Ternary.FALSE

    def simplify(self)->NatSet:
        if not self._items:
            return EmptySet()
        return self

    def is_empty(self)->Ternary:
        return Ternary.TRUE if not self._items else Ternary.FALSE

    def is_full(self)->Ternary:
        return Ternary.FALSE

    def complement(self)->NatSet:
        return FiniteComplementSet(self._items)

    def get_items(self)->set[int]:
        return self._items

    def __repr__(self)->str:
        return f"FiniteNatSet({self._items})"

@final
class EmptySet(FiniteNatSet):
    def __init__(self):
        super().__init__(set())

    def __contains__(self, item:int)->Ternary:
        return Ternary.FALSE

    def simplify(self)->NatSet:
        return self

    def is_empty(self)->Ternary:
        return Ternary.TRUE

    def complement(self)->NatSet:
        return FullSet()

    def __repr__(self)->str:
        return "EmptySet()"

class FiniteComplementSet(NatSet):
    def __init__(self, items:set[int]):
        self._items = items

    def __contains__(self, item:int)->Ternary:
        return Ternary.FALSE if item in self._items else Ternary.TRUE

    def simplify(self)->NatSet:
        if not self._items:
            return FullSet()
        return self

    def is_empty(self)->Ternary:
        return Ternary.FALSE

    def is_full(self)->Ternary:
        return Ternary.TRUE if not self._items else Ternary.FALSE

    def complement(self)->NatSet:
        return FiniteNatSet(self._items)

    def get_comp_items(self)->set[int]:
        return self._items

    def __repr__(self)->str:
        return f"FiniteComplementSet({self._items})"

@final
class FullSet(FiniteComplementSet):
    def __init__(self):
        super().__init__(set())

    def __contains__(self, item:int)->Ternary:
        return Ternary.TRUE

    def simplify(self)->NatSet:
        return self

    def complement(self)->NatSet:
        return EmptySet()    

    def __repr__(self)->str:
        return "FullSet()"

class IntersectionSet(NatSet):
    def __init__(self, *sets:NatSet):
        self._sets = sets
    
    def __contains__(self, item:int)->Ternary:
        return Ternary.TRUE if all(item in s for s in self._sets) else Ternary.FALSE

    def simplify(self)->NatSet:
        if len(self._sets) == 0:
            return FullSet()
        if len(self._sets) == 1:
            return self._sets[0].simplify()

        simp_sets = {s.simplify() for s in self._sets}
        if any(type(s)==UnknownSet for s in simp_sets):
            return UnknownSet()

        finite_set = next((s for s in simp_sets if isinstance(s, FiniteNatSet)), None)
        if finite_set:
            set_nums = finite_set.get_items()
            all_matching_nums:set[int]=set()
            for num in set_nums:
                if all(num in s for s in self._sets):
                    all_matching_nums.add(num)
            return FiniteNatSet(all_matching_nums)

        return IntersectionSet(*simp_sets)

    def is_empty(self)->Ternary:
        return Ternary.UNKNOWN

    def is_full(self)->Ternary:
        res=Ternary.FALSE
        for set in self._sets:
            set_res=set.is_full()
            res|= set_res
            if res==Ternary.TRUE:
                break
        return res

    def complement(self)->NatSet:
        return UnionSet(*[s.complement() for s in self._sets])

    def __repr__(self)->str:
        return f"IntersectionSet({self._sets})"

class UnionSet(NatSet):
    def __init__(self, *sets:NatSet):
        self._sets = sets
    
    def __contains__(self, item:int)->Ternary:
        return Ternary.TRUE if any(item in s for s in self._sets) else Ternary.FALSE

    def simplify(self)->NatSet:
        if len(self._sets) == 0:
            return EmptySet()
        if len(self._sets) == 1:
            return self._sets[0].simplify()

        simp_sets = {s.simplify() for s in self._sets}
        if any(type(s)==UnknownSet for s in simp_sets):
            return UnknownSet()

        finite_comp_set = next((s for s in simp_sets if isinstance(s, FiniteComplementSet)), None)
        if finite_comp_set:
            set_nums = finite_comp_set.get_comp_items()
            all_non_matching_nums:set[int]=set()
            for num in set_nums:
                if all(num not in s for s in self._sets):
                    all_non_matching_nums.add(num)
            return FiniteComplementSet(all_non_matching_nums)

        return UnionSet(*simp_sets)

    def is_empty(self)->Ternary:
        res=Ternary.TRUE
        for set in self._sets:
            set_res=set.is_empty()
            res&= set_res
            if res==Ternary.FALSE:
                break
        return res

    def is_full(self)->Ternary:
        return Ternary.UNKNOWN

    def complement(self)->NatSet:
        return IntersectionSet(*[s.complement() for s in self._sets])

    def __repr__(self)->str:
        return f"UnionSet({self._sets})"

class UnknownSet(NatSet):
    def __init__(self):
        pass

    def __contains__(self, item:int)->Ternary:
        return Ternary.UNKNOWN

    def simplify(self)->NatSet:
        return self

    def is_empty(self)->Ternary:
        return Ternary.UNKNOWN

    def is_full(self)->Ternary:
        return Ternary.UNKNOWN

    def complement(self)->NatSet:
        return UnknownSet()

    def __eq__(self, other:object) -> bool:
        return isinstance(other, UnknownSet)

    def __repr__(self)->str:
        return "UnknownSet()"

def intersection(*sets:NatSet)->NatSet:
    return IntersectionSet(*sets).simplify()

def union(*sets:NatSet)->NatSet:
    return UnionSet(*sets).simplify()
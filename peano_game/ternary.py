from enum import Enum


class Ternary(Enum):
    TRUE="TRUE"
    UNKNOWN="UNKNOWN"
    FALSE="FALSE"

    #__invert__ is technically meant for *bitwise* not,
    #but close enough for our purposes
    #same for __and__ and __or__, since __bool__ does not suit our purposes
    def __invert__(self):
        if self==Ternary.TRUE:
            return Ternary.FALSE
        if self==Ternary.FALSE:
            return Ternary.TRUE
        return self
    
    def __and__(self,other):
        if (self==Ternary.FALSE) or (other==Ternary.FALSE):
            return Ternary.FALSE
        if (self==Ternary.TRUE) and (other==Ternary.TRUE):
            return Ternary.TRUE
        return Ternary.UNKNOWN
    
    def __or__(self,other):
        if (self==Ternary.TRUE) or (other==Ternary.TRUE):
            return Ternary.TRUE
        if (self==Ternary.FALSE) and (other==Ternary.FALSE):
            return Ternary.FALSE
        return Ternary.UNKNOWN
    
    def __str__(self):
        return self.value
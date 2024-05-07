from .value import Value

class Boolean(Value):

    def __init__(self, value):
        super().__init__()
        self.value = value

    def get_comparison_eq(self, other):
        from . import Numero, Chamuyo, Nada
        if isinstance(other, (Numero, Boolean, Chamuyo, Nada)):
            return Boolean(self.value == other.value).set_context(self.context), None
    
        return None, Value.illegal_operation(self, other)
    
    def get_comparison_ne(self, other):
        from . import Numero, Chamuyo, Nada
        if isinstance(other, (Numero, Boolean, Chamuyo, Nada)):
            return Boolean(self.value != other.value).set_context(self.context), None
    
        return None, Value.illegal_operation(self, other)
    
    def notted(self):
        return Boolean(not self.value).set_context(self.context), None

    def is_true(self):
        return self.value

    def copy(self):
        copy = Boolean(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def __str__(self):
        return "posta" if self.value else "trucho"
    
    def __repr__(self):
        return "posta" if self.value else "trucho"
    
Boolean.posta = Boolean(True)
Boolean.trucho = Boolean(False)
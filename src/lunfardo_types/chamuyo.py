from .value import Value
from .numero import Numero
from .boolean import Posta, Trucho

class Chamuyo(Value):

    def __init__(self, value):
        super().__init__()
        self.value = value

    def added_to(self, other):
        if isinstance(other, Chamuyo):
            return Chamuyo(self.value + other.value).set_context(self.context), None
        
        return None, Value.illegal_operation(self, other)
    
    def multiplied_by(self, other):
        if isinstance(other, Numero):
            return Chamuyo(self.value * other.value).set_context(self.context), None
        
        return None, Value.illegal_operation(self, other)
    
    def get_comparison_eq(self, other):
        if isinstance(other, (Chamuyo, Numero)):
            result = self.value == other.value
            if result:
                return Posta(result).set_context(self.context), None
            
            return Trucho(result).set_context(self.context), None
    
        return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def get_comparison_ne(self, other):
        if isinstance(other, (Chamuyo, Numero)):
            result = self.value!= other.value
            if result:
                return Posta(result).set_context(self.context), None
            
            return Trucho(result).set_context(self.context), None
    
        return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def is_true(self):
        if len(self.value) > 0:
            return Posta(True).set_context(self.context), None
        
        return Trucho(False).set_context(self.context), None
    
    def copy(self):
        copy = Chamuyo(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def __str__(self):
        return f'"{self.value}"'

    def __repr__(self):
        return f'"{self.value}"'
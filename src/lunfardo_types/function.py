from .value import Value
from lunfardo_parser import RTResult
from interpreter import SymbolTable, Interpreter
from context import Context
from errors import RTError
import os

class BaseFunction(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name or "<anonymous>"

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context
    
    def check_args(self, arg_names, args):
        res = RTResult()

        if args:
            if len(args) > len(arg_names):
                return res.failure(RTError(
                    self.pos_start, self.pos_end,
                    f"too many args passed into '{self.name}'() (expected {len(arg_names)}, got {len(args)})",
                    self.context
                ))
        
        
            if len(args) < len(arg_names):
                return res.failure(RTError(
                    self.pos_start,
                    self.pos_end,
                    f"too few args passed into '{self.name}'() (expected {len(arg_names)}, got {len(args)})",
                    self.context
                ))
        
        return res.success(None)
    
    def populate_args(self, arg_names, args, exec_ctx):
        if not args:
            return
        for i, arg_name in enumerate(arg_names):
            arg_value = args[i]
            arg_value.set_context(exec_ctx)
            exec_ctx.symbol_table.set(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, exec_ctx):
        res = RTResult()
        res.register(self.check_args(arg_names, args))
        
        if res.error:
            return res
        
        self.populate_args(arg_names, args, exec_ctx)

        return res.success(None)

class Function(BaseFunction):

    def __init__(self, name, body_node, arg_names):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names

    def execute(self, args, current_context):
        res = RTResult()
        # Cada vez que creamos una nueva funcion, es necesario crear un nuevo contexto con una nueva symbol table, que son destruidos una vez que la funcion retorna.
        interpreter = Interpreter()
        execution_context = self.generate_new_context()

        res.register(self.check_and_populate_args(self.arg_names, args, execution_context))
        
        if res.error:
            return res

        value = res.register(interpreter.visit(self.body_node, execution_context))
        if res.error:
            return res
        
        return res.success(value)
    
    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy
    
    def __str__(self):
        return f"<laburo {self.name}>"

    def __repr__(self):
        return f"<laburo {self.name}>"

class BuiltInFunction(BaseFunction):

    def __init__(self, name):
        super().__init__(name)


    def execute(self, args, current_context):
        res = RTResult()
        execution_context = self.generate_new_context()

        method_name = f'exec_{self.name}'
        method = getattr(self, method_name, self.no_visit_method)

        res.register(self.check_and_populate_args(method.arg_names, args, execution_context))
        if res.error:
            return res
        
        return_value = res.register(method(execution_context))
        if res.error:
            return res
        
        return res.success(return_value)
    
    def no_visit_method(self, node, context):
        raise Exception(f'No exec_{self.name} method defined.')
    
    def copy(self):
        copy = BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy
    
    def __repr__(self):
        return f"<curro {self.name}>"
    
    #########################################
    # MARK:CURROS (BUILT-INT FUNCTIONS)
    #########################################

    def exec_chamu(self, exec_ctx):
        from . import String, Number
        value = exec_ctx.symbol_table.get('value')
        
        if not value:
            return RTResult().failure(RTError(
                self.pos_start,
                self.pos_end,
                f"pocos argumentos pasados en '{self.name}'() (se espera 1, se obtuvo 0)",
                exec_ctx
            ))
        
        if isinstance(value, Number):
            return RTResult().success(String(value.value))
        
        if isinstance(value, String):
            return RTResult().success(value)
        
        if isinstance(value, BaseFunction):
            return RTResult().success(String(str(value)))
    
    exec_chamu.arg_names = ['value']
    
    def exec_num(self, exec_ctx):
        from . import String, Number
        value = exec_ctx.symbol_table.get('value')
        
        if not value:
            return RTResult().failure(RTError(
                self.pos_start,
                self.pos_end,
                f"pocos argumentos pasados en '{self.name}'() (se espera 1, se obtuvo 0)",
                exec_ctx
            ))
        
        if isinstance(value, Number):
            return RTResult().success(value)
        
        if isinstance(value, String):
            # check if string is a valid string
            try:
                new_value = int(value.value)
            except ValueError:
                return RTResult().failure(RTError(
                    self.pos_start,
                    self.pos_end,
                    f"Literal invalido para '{self.name}()' con base 10: '{value.value}'",
                    exec_ctx
                ))
            
            return RTResult().success(Number(new_value))
        
        if isinstance(value, BaseFunction):
            return RTResult().failure(RTError(
                self.pos_start,
                self.pos_end,
                f"El argumento de {self.name}() debe ser un chamuyo o un número, no un 'laburo'",
                exec_ctx
            ))
    
    exec_num.arg_names = ['value']
    
    def exec_matear(self, exec_ctx):
        from . import Number
        value = exec_ctx.symbol_table.get('value')
        if value is not None: 
            print(value)
        else:
            print()
        return RTResult().success(Number.null)
    
    exec_matear.arg_names = ['value']
    
    def exec_morfar(self, exec_ctx):
        from . import String
        _prefix = exec_ctx.symbol_table.get('value')
        if _prefix is not None:
            text = input(_prefix)
        else:
            text = input()
        return RTResult().success(String(text))
    
    exec_morfar.arg_names = ['value']

    def exec_limpiavidrios(self, exec_ctx):
        from . import Number
        os.system('cls' if os.name == 'nt' else 'clear')
        return RTResult().success(Number.null)
    
    exec_limpiavidrios.arg_names = []
    
    def exec_es_num(self, exec_ctx):
        from . import Number
        is_number = isinstance(exec_ctx.symbol_table.get('value'), Number)
        return RTResult().success(Number.true if is_number else Number.false)
    
    exec_es_num.arg_names = ['value']
    
    def exec_es_chamu(self, exec_ctx):
        from . import Number, String
        is_string = isinstance(exec_ctx.symbol_table.get('value'), String)
        return RTResult().success(Number.true if is_string else Number.false)
    
    exec_es_chamu.arg_names = ['value']
    
    def exec_es_coso(self, exec_ctx):
        from . import Number, LList
        is_list = isinstance(exec_ctx.symbol_table.get('value'), LList)
        return RTResult().success(Number.true if is_list else Number.false)
    
    exec_es_coso.arg_names = ['value']
    
    def exec_es_laburo(self, exec_ctx):
        from . import Number
        is_func = isinstance(exec_ctx.symbol_table.get('value'), BaseFunction)
        return RTResult().success(Number.true if is_func else Number.false)
    
    exec_es_laburo.arg_names = ['value']
    
    def exec_guardar(self, exec_ctx):
        from . import Number, LList
        list_ = exec_ctx.symbol_table.get('list')
        value = exec_ctx.symbol_table.get('value')

        if not isinstance(list_, LList):
            return RTResult().failure(RTError(
                self.pos_start,
                self.pos_end,
                "First argument must be type list.",
                exec_ctx
            ))
        
        list_.elements.append(value)
        return RTResult().success(Number.null)
    
    exec_guardar.arg_names = ['list', 'value']
    
    def exec_sacar(self, exec_ctx):
        from . import Number, LList
        list_ = exec_ctx.symbol_table.get('list')
        index = exec_ctx.symbol_table.get('index')

        if not isinstance(list_, LList):
            return RTResult().failure(RTError(
                self.pos_start,
                self.pos_end,
                "First argument must be type list.",
                exec_ctx
            ))
        
        if not isinstance(index, Number):
            return RTResult().failure(RTError(
                self.pos_start,
                self.pos_end,
                "Second argument must be type number.",
                exec_ctx
            ))
        
        try:
            popped = list_.elements.pop(index.value)
        except IndexError:
            return RTResult().failure(RTError(
                self.pos_start,
                self.pos_end,
                f"Element at index '{index.value}' could not be removed from list becase index is out of bounds.",
                exec_ctx
            ))
        
        return RTResult().success(popped)
    
    exec_sacar.arg_names = ['list', 'index']

    def exec_extender(self, exec_ctx):
        from . import Number, LList
        listA = exec_ctx.symbol_table.get('listA')
        listB = exec_ctx.symbol_table.get('listB')

        if not isinstance(listA, LList):
            return RTResult().failure(RTError(
                self.pos_start,
                self.pos_end,
                "First argument must be type list.",
                exec_ctx
            ))

        if not isinstance(listB, LList):
            return RTResult().failure(RTError(
                self.pos_start,
                self.pos_end,
                "Second argument must be type list.",
                exec_ctx
            ))
        
        listA.elements.extend(listB.elements)

        return RTResult().success(Number.null)

    exec_extender.arg_names = ['listA', 'listB']

BuiltInFunction.matear          = BuiltInFunction('matear')
BuiltInFunction.morfar          = BuiltInFunction('morfar')
BuiltInFunction.limpiavidrios   = BuiltInFunction('limpiavidrios')
BuiltInFunction.es_num          = BuiltInFunction('es_num')
BuiltInFunction.es_chamu        = BuiltInFunction('es_chamu')
BuiltInFunction.es_coso         = BuiltInFunction('es_coso')
BuiltInFunction.es_laburo       = BuiltInFunction('es_laburo')
BuiltInFunction.guardar         = BuiltInFunction('guardar')
BuiltInFunction.sacar           = BuiltInFunction('sacar')
BuiltInFunction.extender        = BuiltInFunction('extender')
BuiltInFunction.chamu           = BuiltInFunction('chamu')
BuiltInFunction.num             = BuiltInFunction('num')






from lunfardo import Lexer
from lunfardo_parser import Parser
from interpreter import Interpreter
from context import Context

def execute(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error

    # Generate AST
    parser = Parser(tokens)
    ast = parser.parse()

    # Run
    interpreter = Interpreter()
    context = Context('<program>')
    result = interpreter.visit(ast.node, context)

    return result.value, result.error

def run():
    while True:
        text = input('Lunfardo > ')
        result, error = execute('<stdin>', text)

        if error:
            print(error.as_string())
        else:
            print(result)

if __name__ == '__main__':
    run()
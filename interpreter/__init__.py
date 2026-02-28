from .lexer import Lexer
from .parser import Parser
from .evaluator import Interpreter
from .errors import SproutError

def run_source(source, output_fn=None, input_fn=None):
    """Run a Sprout source string. Returns list of output lines."""
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        tree = parser.parse()
        interp = Interpreter(output_fn=output_fn, input_fn=input_fn)
        interp.run(tree)
    except SproutError as e:
        if output_fn:
            output_fn(f"\n🌿 Error: {e}")
        else:
            print(f"\n🌿 Error: {e}")

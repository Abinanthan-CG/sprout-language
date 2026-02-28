import math
import random as _random
from .errors import SproutError


def _fmt(val):
    """Convert a Sprout value to a display string."""
    if val is True:  return "true"
    if val is False: return "false"
    if val is None:  return ""
    if isinstance(val, float) and val == int(val):
        return str(int(val))
    if isinstance(val, list):
        return "[" + ", ".join(_fmt(v) for v in val) + "]"
    return str(val)


def _make(fn):
    """Wrap a simple Python fn so it matches the (args, out, inp) calling convention."""
    return fn


# ── individual built-ins ──────────────────────────────────────────────────────

def _length(args, out, inp):
    if len(args) != 1:
        raise SproutError("🌿 'length' needs exactly 1 thing — e.g.  length(mylist)")
    v = args[0]
    if isinstance(v, (str, list)):
        return len(v)
    raise SproutError(f"🌿 Can't get the length of '{_fmt(v)}'.")

def _round_fn(args, out, inp):
    if not args:
        raise SproutError("🌿 'round' needs a number — e.g.  round(3.7)")
    places = int(args[1]) if len(args) > 1 else 0
    result = round(float(args[0]), places)
    return int(result) if places == 0 else result

def _random_fn(args, out, inp):
    if len(args) == 0: return _random.random()
    if len(args) == 2: return _random.randint(int(args[0]), int(args[1]))
    raise SproutError("🌿 'random' takes 0 or 2 arguments:  random()  or  random(1, 10)")

def _join(args, out, inp):
    if len(args) < 1:
        raise SproutError("🌿 'join' needs a list — e.g.  join(mylist, \", \")")
    lst = args[0]
    sep = str(args[1]) if len(args) > 1 else ""
    if not isinstance(lst, list):
        raise SproutError("🌿 'join' needs a list as its first argument.")
    return sep.join(_fmt(v) for v in lst)

def _number(args, out, inp):
    if len(args) != 1:
        raise SproutError("🌿 'number' needs exactly 1 argument — e.g.  number(\"42\")")
    try:
        v = args[0]
        if isinstance(v, str):
            return float(v) if '.' in v else int(v)
        return float(v)
    except (ValueError, TypeError):
        raise SproutError(f"🌿 I can't turn '{args[0]}' into a number.")

def _text(args, out, inp):
    if len(args) != 1:
        raise SproutError("🌿 'text' needs exactly 1 argument — e.g.  text(42)")
    return _fmt(args[0])

def _add_to(args, out, inp):
    if len(args) != 2:
        raise SproutError("🌿 'add' needs 2 arguments:  add(mylist, item)")
    lst = args[0]
    if not isinstance(lst, list):
        raise SproutError("🌿 'add' needs a list as its first argument.")
    lst.append(args[1])
    return lst

def _remove_from(args, out, inp):
    if len(args) != 2:
        raise SproutError("🌿 'remove' needs 2 arguments:  remove(mylist, index)")
    lst, idx = args[0], int(args[1])
    if not isinstance(lst, list):
        raise SproutError("🌿 'remove' needs a list as its first argument.")
    if idx < 0 or idx >= len(lst):
        raise SproutError(f"🌿 Index {idx} is out of range.")
    lst.pop(idx)
    return lst

def _contains(args, out, inp):
    if len(args) != 2:
        raise SproutError("🌿 'contains' needs 2 arguments:  contains(mylist, item)")
    return args[1] in args[0]

def _uppercase(args, out, inp):
    if len(args) != 1: raise SproutError("🌿 'uppercase' needs 1 argument.")
    return str(args[0]).upper()

def _lowercase(args, out, inp):
    if len(args) != 1: raise SproutError("🌿 'lowercase' needs 1 argument.")
    return str(args[0]).lower()

def _split(args, out, inp):
    if len(args) < 1: raise SproutError("🌿 'split' needs at least 1 argument.")
    sep = str(args[1]) if len(args) > 1 else " "
    return str(args[0]).split(sep)

def _floor(args, out, inp):
    if len(args) != 1: raise SproutError("🌿 'floor' needs 1 number.")
    return int(math.floor(float(args[0])))

def _ceil(args, out, inp):
    if len(args) != 1: raise SproutError("🌿 'ceil' needs 1 number.")
    return int(math.ceil(float(args[0])))

def _abs_fn(args, out, inp):
    if len(args) != 1: raise SproutError("🌿 'abs' needs 1 number.")
    return abs(args[0])

def _max_fn(args, out, inp):
    if not args: raise SproutError("🌿 'max' needs at least 1 argument.")
    if len(args) == 1 and isinstance(args[0], list): return max(args[0])
    return max(args)

def _min_fn(args, out, inp):
    if not args: raise SproutError("🌿 'min' needs at least 1 argument.")
    if len(args) == 1 and isinstance(args[0], list): return min(args[0])
    return min(args)

def _sqrt(args, out, inp):
    if len(args) != 1: raise SproutError("🌿 'sqrt' needs 1 number.")
    return math.sqrt(float(args[0]))

def _pow(args, out, inp):
    if len(args) != 2: raise SproutError("🌿 'pow' needs 2 numbers: base and exponent.")
    return math.pow(float(args[0]), float(args[1]))

def _type(args, out, inp):
    if len(args) != 1: raise SproutError("🌿 'type' needs exactly 1 argument.")
    val = args[0]
    if isinstance(val, bool): return "boolean"
    if isinstance(val, (int, float)): return "number"
    if isinstance(val, str): return "string"
    if isinstance(val, list): return "list"
    import types
    if callable(val) or isinstance(val, types.FunctionType) or type(val).__name__ == "SproutFunction":
        return "function"
    return "unknown"

def _wait(args, out, inp):
    import time
    secs = float(args[0]) if args else 1
    time.sleep(secs)
    return None

def _nl(args, out, inp):
    out("")
    return None


BUILTINS = {
    'length':    _length,
    'round':     _round_fn,
    'random':    _random_fn,
    'join':      _join,
    'number':    _number,
    'text':      _text,
    'add':       _add_to,
    'remove':    _remove_from,
    'contains':  _contains,
    'uppercase': _uppercase,
    'lowercase': _lowercase,
    'split':     _split,
    'floor':     _floor,
    'ceil':      _ceil,
    'abs':       _abs_fn,
    'max':       _max_fn,
    'min':       _min_fn,
    'sqrt':      _sqrt,
    'pow':       _pow,
    'type':      _type,
    'wait':      _wait,
    'newline':   _nl,
    'pi':        math.pi,
    'e':         math.e,
}


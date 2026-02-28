from .ast_nodes import *
from .errors import SproutError, SproutReturn, SproutBreak, SproutContinue
from .builtins import BUILTINS, _fmt



class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def get(self, name, line=0):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name, line)
        raise SproutError(
            f"🌿 I don't know what '{name}' is.\n"
            f"   Hint: Use 'grow {name} as ...' to create it first.", line)

    def set(self, name, value):
        self.vars[name] = value

    def assign(self, name, value, line=0):
        if name in self.vars:
            self.vars[name] = value
            return
        if self.parent:
            self.parent.assign(name, value, line)
            return
        raise SproutError(
            f"🌿 I don't know what '{name}' is.\n"
            f"   Hint: Use 'grow {name} as ...' to create it first, then you can change it.", line)


class SproutFunction:
    def __init__(self, name, params, body, closure):
        self.name = name
        self.params = params
        self.body = body
        self.closure = closure


class Interpreter:
    def __init__(self, output_fn=None, input_fn=None):
        self.out = output_fn or print
        self.inp = input_fn or input
        self._globals = Environment()
        for name, fn in BUILTINS.items():
            self._globals.set(name, fn)

    def run(self, program):
        self._exec_block(program.body, self._globals)

    # ── block & statement dispatch ────────────────────────────────────────────
    def _exec_block(self, stmts, env):
        for stmt in stmts:
            self._exec(stmt, env)

    def _exec(self, node, env):
        t = type(node)

        if t is BloomStmt:
            self.out(_fmt(self._eval(node.value, env)))

        elif t is GrowStmt:
            env.set(node.name, self._eval(node.value, env))

        elif t is AssignStmt:
            env.assign(node.name, self._eval(node.value, env), node.line)

        elif t is HarvestStmt:
            prompt = _fmt(self._eval(node.prompt, env))
            try:
                raw = self.inp(prompt)
            except EOFError:
                raw = ""
            # auto-coerce to number if possible
            try:
                val = int(raw) if '.' not in raw else float(raw)
            except (ValueError, AttributeError):
                val = raw
            env.set(node.name, val)

        elif t is WhenStmt:
            chosen = node.then_block if self._truthy(self._eval(node.condition, env)) else node.else_block
            if chosen is not None:
                self._exec_block(chosen, Environment(env))

        elif t is WaterStmt:
            n = self._eval(node.count, env)
            if not isinstance(n, (int, float)):
                raise SproutError(f"🌿 'water' needs a number, not '{_fmt(n)}'", node.line)
            for _ in range(int(n)):
                try:
                    self._exec_block(node.body, Environment(env))
                except SproutBreak:
                    break
                except SproutContinue:
                    continue

        elif t is WhilstStmt:
            while self._truthy(self._eval(node.condition, env)):
                try:
                    self._exec_block(node.body, Environment(env))
                except SproutBreak:
                    break
                except SproutContinue:
                    continue

        elif t is EachStmt:
            lst = self._eval(node.iterable, env)
            if not isinstance(lst, list):
                raise SproutError("🌿 'each...in' needs a list to loop over.", node.line)
            for item in lst:
                inner = Environment(env)
                inner.set(node.var_name, item)
                try:
                    self._exec_block(node.body, inner)
                except SproutBreak:
                    break
                except SproutContinue:
                    continue


        elif t is PlantStmt:
            env.set(node.name, SproutFunction(node.name, node.params, node.body, env))

        elif t is BearStmt:
            raise SproutReturn(self._eval(node.value, env))

        elif t is StopStmt:
            raise SproutBreak()

        elif t is SkipStmt:
            raise SproutContinue()

        elif t is ExprStmt:
            self._eval(node.expr, env)


    # ── expression evaluator ──────────────────────────────────────────────────
    def _eval(self, node, env):
        t = type(node)

        if t is NumberLiteral:  return node.value
        if t is StringLiteral:  return node.value
        if t is BoolLiteral:    return node.value
        if t is Identifier:     return env.get(node.name, node.line)

        if t is ListLiteral:
            return [self._eval(e, env) for e in node.elements]

        if t is IndexExpr:
            obj = self._eval(node.obj, env)
            idx = self._eval(node.index, env)
            if isinstance(obj, str):
                if not isinstance(idx, (int, float)):
                    raise SproutError("🌿 The index must be a number.", node.line)
                i = int(idx)
                if i < 0 or i >= len(obj):
                    raise SproutError(
                        f"🌿 Index {i} is out of range. The string has {len(obj)} character(s).", node.line)
                return obj[i]
            if not isinstance(obj, list):
                raise SproutError("🌿 You can only use '[...]' on a list or string.", node.line)
            if not isinstance(idx, (int, float)):
                raise SproutError("🌿 The index inside '[...]' must be a number.", node.line)
            i = int(idx)
            if i < 0 or i >= len(obj):
                raise SproutError(
                    f"🌿 Index {i} is out of range. The list has {len(obj)} item(s) (0 to {len(obj)-1}).", node.line)
            return obj[i]


        if t is BinOp:
            return self._binop(node, env)

        if t is UnaryOp:
            val = self._eval(node.operand, env)
            if node.op == '-':
                if not isinstance(val, (int, float)):
                    raise SproutError(f"🌿 Can't negate '{_fmt(val)}' — only numbers can be negated.", node.line)
                return -val
            if node.op == 'not':
                return not self._truthy(val)

        if t is FuncCall:
            return self._call(node, env)

        raise SproutError(f"🌿 Unknown node: {t.__name__}", 0)

    def _binop(self, node, env):
        op = node.op
        # short-circuit booleans
        if op == 'and':
            return self._truthy(self._eval(node.left, env)) and self._truthy(self._eval(node.right, env))
        if op == 'or':
            return self._truthy(self._eval(node.left, env)) or self._truthy(self._eval(node.right, env))

        l = self._eval(node.left, env)
        r = self._eval(node.right, env)

        if op == '+':
            if isinstance(l, str) or isinstance(r, str):
                return _fmt(l) + _fmt(r)
            if isinstance(l, list) and isinstance(r, list):
                return l + r
            return l + r
        if op == '-': return l - r
        if op == '*': return l * r
        if op == '/':
            if r == 0:
                raise SproutError("🌿 You can't divide by zero!", node.line)
            return l / r
        if op == '%': return l % r
        if op == '==': return l == r
        if op == '!=': return l != r
        if op == '<':  return l < r
        if op == '>':  return l > r
        if op == '<=': return l <= r
        if op == '>=': return l >= r
        raise SproutError(f"🌿 Unknown operator '{op}'", node.line)

    def _call(self, node, env):
        fn = env.get(node.name, node.line)
        args = [self._eval(a, env) for a in node.args]

        if callable(fn):  # built-in
            try:
                return fn(args, self.out, self.inp)
            except SproutError:
                raise
            except Exception as e:
                raise SproutError(f"🌿 Error in '{node.name}': {e}", node.line)

        if isinstance(fn, SproutFunction):
            if len(args) != len(fn.params):
                raise SproutError(
                    f"🌿 '{fn.name}' expects {len(fn.params)} argument(s) but got {len(args)}.", node.line)
            fn_env = Environment(fn.closure)
            for p, a in zip(fn.params, args):
                fn_env.set(p, a)
            try:
                self._exec_block(fn.body, fn_env)
                return None
            except SproutReturn as r:
                return r.value

        raise SproutError(f"🌿 '{node.name}' is not something I can call.", node.line)

    @staticmethod
    def _truthy(val):
        return val not in (None, False, 0, 0.0, "", [])

from .lexer import Lexer
from .ast_nodes import *
from .errors import SproutError


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # ── navigation ────────────────────────────────────────────────────────────
    def _cur(self):
        return self.tokens[self.pos]

    def _peek(self, offset=1):
        p = self.pos + offset
        return self.tokens[p] if p < len(self.tokens) else self.tokens[-1]

    def _advance(self):
        tok = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def _check(self, *types):
        return self._cur().type in types

    def _match(self, *types):
        if self._check(*types):
            return self._advance()
        return None

    def _expect(self, type_, msg=None):
        if self._cur().type == type_:
            return self._advance()
        tok = self._cur()
        raise SproutError(msg or f"Expected '{type_}' but got '{tok.value}'", tok.line)

    # ── top level ─────────────────────────────────────────────────────────────
    def parse(self):
        body = []
        while not self._check('EOF'):
            body.append(self._statement())
        return Program(body=body)

    # ── statements ────────────────────────────────────────────────────────────
    def _statement(self):
        t = self._cur()

        if t.type == 'BLOOM':     return self._bloom()
        if t.type == 'GROW':      return self._grow()
        if t.type == 'HARVEST':   return self._harvest()
        if t.type == 'WHEN':      return self._when()
        if t.type == 'WATER':     return self._water()
        if t.type == 'WHILST':    return self._whilst()
        if t.type == 'EACH':      return self._each()
        if t.type == 'PLANT':     return self._plant()
        if t.type == 'BEAR':      return self._bear()
        if t.type == 'STOP':      tok = self._advance(); return StopStmt(line=tok.line)
        if t.type == 'SKIP':      tok = self._advance(); return SkipStmt(line=tok.line)

        # assignment: IDENT = expr
        if t.type == 'IDENT' and self._peek().type == 'ASSIGN':
            return self._assign()

        return ExprStmt(expr=self._expr(), line=t.line)

    def _bloom(self):
        tok = self._advance()
        return BloomStmt(value=self._expr(), line=tok.line)

    def _grow(self):
        tok = self._advance()
        name = self._expect('IDENT', "After 'grow' I need a name — e.g.  grow score as 0").value
        self._expect('AS', f"After 'grow {name}' I need 'as' — e.g.  grow {name} as 0")
        return GrowStmt(name=name, value=self._expr(), line=tok.line)

    def _assign(self):
        name_tok = self._advance()
        self._advance()          # '='
        return AssignStmt(name=name_tok.value, value=self._expr(), line=name_tok.line)

    def _harvest(self):
        tok = self._advance()
        name = self._expect('IDENT',
            "After 'harvest' I need a name — e.g.  harvest answer with \"What?\"").value
        self._expect('WITH',
            f"After 'harvest {name}' I need 'with' — e.g.  harvest {name} with \"What?\"")
        return HarvestStmt(name=name, prompt=self._expr(), line=tok.line)

    def _when(self):
        tok = self._advance()
        cond = self._expr()
        then = self._block()
        else_ = None
        if self._match('OTHERWISE'):
            else_ = self._block()
        return WhenStmt(condition=cond, then_block=then, else_block=else_, line=tok.line)

    def _water(self):
        tok = self._advance()
        count = self._expr()
        self._expect('TIMES', "After 'water <number>' I need 'times' — e.g.  water 5 times { }")
        return WaterStmt(count=count, body=self._block(), line=tok.line)

    def _whilst(self):
        tok = self._advance()
        return WhilstStmt(condition=self._expr(), body=self._block(), line=tok.line)

    def _each(self):
        tok = self._advance()
        var = self._expect('IDENT', "After 'each' I need a name — e.g.  each item in colors { }").value
        self._expect('IN', f"After 'each {var}' I need 'in' — e.g.  each {var} in mylist {{ }}")
        return EachStmt(var_name=var, iterable=self._expr(), body=self._block(), line=tok.line)

    def _plant(self):
        tok = self._advance()
        name = self._expect('IDENT', "After 'plant' I need a function name — e.g.  plant greet with name { }").value
        params = []
        if self._match('WITH'):
            params.append(self._expect('IDENT').value)
            while self._match('AND'):
                params.append(self._expect('IDENT').value)
        return PlantStmt(name=name, params=params, body=self._block(), line=tok.line)

    def _bear(self):
        tok = self._advance()
        return BearStmt(value=self._expr(), line=tok.line)

    def _block(self):
        self._expect('LBRACE', "I was expecting '{' to start a block.")
        stmts = []
        while not self._check('RBRACE') and not self._check('EOF'):
            stmts.append(self._statement())
        self._expect('RBRACE', "I was expecting '}' to end the block.")
        return stmts

    # ── expressions ───────────────────────────────────────────────────────────
    def _expr(self):    return self._or()

    def _or(self):
        left = self._and()
        while self._check('OR'):
            op = self._advance()
            left = BinOp(left=left, op='or', right=self._and(), line=op.line)
        return left

    def _and(self):
        left = self._not()
        while self._check('AND'):
            op = self._advance()
            left = BinOp(left=left, op='and', right=self._not(), line=op.line)
        return left

    def _not(self):
        if self._check('NOT'):
            op = self._advance()
            return UnaryOp(op='not', operand=self._not(), line=op.line)
        return self._cmp()

    def _cmp(self):
        left = self._add()
        OPS = {'EQ': '==', 'NEQ': '!=', 'LT': '<', 'GT': '>', 'LTE': '<=', 'GTE': '>='}
        while self._cur().type in OPS:
            op = self._advance()
            left = BinOp(left=left, op=OPS[op.type], right=self._add(), line=op.line)
        return left

    def _add(self):
        left = self._mul()
        while self._check('PLUS', 'MINUS'):
            op = self._advance()
            left = BinOp(left=left, op=op.value, right=self._mul(), line=op.line)
        return left

    def _mul(self):
        left = self._unary()
        while self._check('STAR', 'SLASH', 'PERCENT'):
            op = self._advance()
            left = BinOp(left=left, op=op.value, right=self._unary(), line=op.line)
        return left

    def _unary(self):
        if self._check('MINUS'):
            op = self._advance()
            return UnaryOp(op='-', operand=self._primary(), line=op.line)
        return self._primary()

    def _primary(self):
        tok = self._cur()
        node = self._atom()
        # postfix index: node[expr]
        while self._check('LBRACKET'):
            self._advance()
            idx = self._expr()
            self._expect('RBRACKET')
            node = IndexExpr(obj=node, index=idx, line=tok.line)
        return node

    def _atom(self):
        tok = self._cur()

        if self._check('NUMBER'):
            self._advance()
            return NumberLiteral(value=tok.value, line=tok.line)

        if self._check('STRING'):
            self._advance()
            return StringLiteral(value=tok.value, line=tok.line)

        if self._check('TRUE'):
            self._advance()
            return BoolLiteral(value=True, line=tok.line)

        if self._check('FALSE'):
            self._advance()
            return BoolLiteral(value=False, line=tok.line)

        if self._check('LBRACKET'):
            return self._list_literal()

        if self._check('LPAREN'):
            self._advance()
            node = self._expr()
            self._expect('RPAREN')
            return node

        if self._check('IDENT'):
            name_tok = self._advance()
            if self._check('LPAREN'):           # function call: name(args)
                self._advance()
                args = []
                if not self._check('RPAREN'):
                    args.append(self._expr())
                    while self._match('COMMA'):
                        args.append(self._expr())
                self._expect('RPAREN')
                return FuncCall(name=name_tok.value, args=args, line=name_tok.line)
            return Identifier(name=name_tok.value, line=name_tok.line)

        raise SproutError(
            f"🌿 I don't know what to do with '{tok.value}' here.", tok.line)

    def _list_literal(self):
        tok = self._advance()   # '['
        elements = []
        if not self._check('RBRACKET'):
            elements.append(self._expr())
            while self._match('COMMA'):
                elements.append(self._expr())
        self._expect('RBRACKET')
        return ListLiteral(elements=elements, line=tok.line)

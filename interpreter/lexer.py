from .errors import SproutError

# ── Token types ──────────────────────────────────────────────────────────────
TT = {
    'BLOOM': 'BLOOM', 'GROW': 'GROW', 'AS': 'AS',
    'HARVEST': 'HARVEST', 'WITH': 'WITH',
    'WHEN': 'WHEN', 'OTHERWISE': 'OTHERWISE',
    'WHILST': 'WHILST', 'WATER': 'WATER', 'TIMES': 'TIMES',
    'PLANT': 'PLANT', 'BEAR': 'BEAR',
    'AND': 'AND', 'OR': 'OR', 'NOT': 'NOT',
    'TRUE': 'TRUE', 'FALSE': 'FALSE',
    'EACH': 'EACH', 'IN': 'IN',
    'NUMBER': 'NUMBER', 'STRING': 'STRING', 'IDENT': 'IDENT',
    'PLUS': 'PLUS', 'MINUS': 'MINUS', 'STAR': 'STAR',
    'SLASH': 'SLASH', 'PERCENT': 'PERCENT',
    'EQ': 'EQ', 'NEQ': 'NEQ',
    'LT': 'LT', 'GT': 'GT', 'LTE': 'LTE', 'GTE': 'GTE',
    'ASSIGN': 'ASSIGN',
    'LBRACE': 'LBRACE', 'RBRACE': 'RBRACE',
    'LBRACKET': 'LBRACKET', 'RBRACKET': 'RBRACKET',
    'LPAREN': 'LPAREN', 'RPAREN': 'RPAREN',
    'COMMA': 'COMMA', 'EOF': 'EOF',
}

KEYWORDS = {
    'bloom': 'BLOOM', 'grow': 'GROW', 'as': 'AS',
    'harvest': 'HARVEST', 'with': 'WITH',
    'when': 'WHEN', 'otherwise': 'OTHERWISE',
    'whilst': 'WHILST', 'water': 'WATER', 'times': 'TIMES',
    'plant': 'PLANT', 'bear': 'BEAR',
    'and': 'AND', 'or': 'OR', 'not': 'NOT',
    'true': 'TRUE', 'false': 'FALSE',
    'each': 'EACH', 'in': 'IN',
    'stop': 'STOP', 'skip': 'SKIP',
}


class Token:
    __slots__ = ('type', 'value', 'line')

    def __init__(self, type_, value, line=0):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f'Token({self.type}, {self.value!r})'


class Lexer:
    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.line = 1

    # ── helpers ──────────────────────────────────────────────────────────────
    def _peek(self, offset=0):
        p = self.pos + offset
        return self.source[p] if p < len(self.source) else None

    def _advance(self):
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
        return ch

    def _error(self, msg):
        raise SproutError(f"🌿 {msg}", self.line)

    # ── public ────────────────────────────────────────────────────────────────
    def tokenize(self):
        tokens = []
        while self.pos < len(self.source):
            ch = self._peek()

            if ch in ' \t\r':
                self._advance()
            elif ch == '\n':
                self._advance()
            elif ch == '~':                              # comment
                while self.pos < len(self.source) and self._peek() != '\n':
                    self._advance()
            elif ch in ('"', "'"):
                tokens.append(self._read_string(ch))
            elif ch.isdigit():
                tokens.append(self._read_number())
            elif ch.isalpha() or ch == '_':
                tokens.append(self._read_ident())
            else:
                tokens.append(self._read_symbol())

        tokens.append(Token('EOF', None, self.line))
        return tokens

    def _read_string(self, quote):
        line = self.line
        self._advance()          # opening quote
        chars = []
        while self.pos < len(self.source) and self._peek() != quote:
            ch = self._advance()
            if ch == '\\':
                esc = self._advance()
                chars.append({'n': '\n', 't': '\t', '\\': '\\',
                              '"': '"', "'": "'"}.get(esc, esc))
            else:
                chars.append(ch)
        if self.pos >= len(self.source):
            self._error("String was never closed — did you forget a closing quote?")
        self._advance()          # closing quote
        return Token('STRING', ''.join(chars), line)

    def _read_number(self):
        line = self.line
        chars = []
        while self.pos < len(self.source) and self._peek().isdigit():
            chars.append(self._advance())
        if self.pos < len(self.source) and self._peek() == '.':
            chars.append(self._advance())
            while self.pos < len(self.source) and self._peek().isdigit():
                chars.append(self._advance())
            return Token('NUMBER', float(''.join(chars)), line)
        return Token('NUMBER', int(''.join(chars)), line)

    def _read_ident(self):
        line = self.line
        chars = []
        while self.pos < len(self.source) and (self._peek().isalnum() or self._peek() == '_'):
            chars.append(self._advance())
        word = ''.join(chars)
        ttype = KEYWORDS.get(word.lower(), 'IDENT')
        return Token(ttype, word, line)

    def _read_symbol(self):
        line = self.line
        ch = self._advance()
        two = ch + (self._peek() or '')
        doubles = {'==': 'EQ', '!=': 'NEQ', '<=': 'LTE', '>=': 'GTE'}
        if two in doubles:
            self._advance()
            return Token(doubles[two], two, line)
        singles = {
            '+': 'PLUS', '-': 'MINUS', '*': 'STAR', '/': 'SLASH', '%': 'PERCENT',
            '<': 'LT', '>': 'GT', '=': 'ASSIGN',
            '{': 'LBRACE', '}': 'RBRACE',
            '[': 'LBRACKET', ']': 'RBRACKET',
            '(': 'LPAREN', ')': 'RPAREN',
            ',': 'COMMA',
        }
        if ch in singles:
            return Token(singles[ch], ch, line)
        self._error(f"I don't recognise the character '{ch}'")

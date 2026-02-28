"""
tests/test_interpreter.py — Sprout language test suite
Run with:  python -m pytest tests/ -v
"""
import sys, os, io
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from interpreter.lexer import Lexer
from interpreter.parser import Parser
from interpreter.evaluator import Interpreter
from interpreter.errors import SproutError
import pytest


def run(source, inputs=None):
    """Run Sprout source; return list of output lines."""
    lines = []
    inp_iter = iter(inputs or [])

    def out(line): lines.append(str(line))
    def inp(prompt): return str(next(inp_iter, ""))

    tokens = Lexer(source).tokenize()
    tree   = Parser(tokens).parse()
    Interpreter(output_fn=out, input_fn=inp).run(tree)
    return lines


def run_err(source):
    """Run and expect a SproutError."""
    with pytest.raises(SproutError):
        run(source)


# ── bloom (print) ─────────────────────────────────────────────────────────────
def test_bloom_string():
    assert run('bloom "Hello!"') == ["Hello!"]

def test_bloom_number():
    assert run('bloom 42') == ["42"]

def test_bloom_expression():
    assert run('bloom 3 + 4') == ["7"]

def test_bloom_string_concat():
    assert run('bloom "Hi " + "there"') == ["Hi there"]


# ── variables ─────────────────────────────────────────────────────────────────
def test_grow_and_bloom():
    assert run('grow x as 10\nbloom x') == ["10"]

def test_assign():
    assert run('grow x as 1\nx = 99\nbloom x') == ["99"]

def test_grow_string():
    assert run('grow s as "hello"\nbloom s') == ["hello"]

def test_variable_not_found():
    run_err('bloom undefined_var')


# ── arithmetic ────────────────────────────────────────────────────────────────
def test_add():      assert run('bloom 2 + 3')   == ["5"]
def test_sub():      assert run('bloom 10 - 4')  == ["6"]
def test_mul():      assert run('bloom 3 * 4')   == ["12"]
def test_div():      assert run('bloom 10 / 4')  == ["2.5"]
def test_mod():      assert run('bloom 10 % 3')  == ["1"]
def test_neg():      assert run('bloom -5')       == ["-5"]
def test_div_zero(): run_err('bloom 1 / 0')


# ── comparisons & booleans ────────────────────────────────────────────────────
def test_eq_true():  assert run('bloom 5 == 5') == ["true"]
def test_eq_false(): assert run('bloom 5 == 6') == ["false"]
def test_lt():       assert run('bloom 3 < 5')  == ["true"]
def test_gt():       assert run('bloom 5 > 9')  == ["false"]
def test_and():      assert run('bloom true and false') == ["false"]
def test_or():       assert run('bloom false or true')  == ["true"]
def test_not():      assert run('bloom not true')        == ["false"]


# ── when / otherwise ─────────────────────────────────────────────────────────
def test_when_true():
    assert run('when 1 == 1 {\n  bloom "yes"\n}') == ["yes"]

def test_when_false_otherwise():
    assert run('when 1 == 2 {\n  bloom "yes"\n} otherwise {\n  bloom "no"\n}') == ["no"]

def test_when_nested():
    src = '''
grow x as 5
when x > 3 {
    when x > 10 { bloom "big" } otherwise { bloom "medium" }
} otherwise { bloom "small" }
'''
    assert run(src) == ["medium"]


# ── water (repeat) ────────────────────────────────────────────────────────────
def test_water():
    assert run('water 3 times {\n  bloom "hi"\n}') == ["hi", "hi", "hi"]

def test_water_zero():
    assert run('water 0 times {\n  bloom "hi"\n}') == []

def test_water_stop():
    assert run('water 5 times {\n  bloom "hi"\n  stop\n}') == ["hi"]

def test_water_skip():
    src = 'grow i as 0\nwhilst i < 3 {\n  i = i + 1\n  when i == 2 { skip }\n  bloom i\n}'
    assert run(src) == ["1", "3"]

# ── whilst ────────────────────────────────────────────────────────────────────

def test_whilst():
    src = 'grow i as 0\nwhilst i < 3 {\n  bloom i\n  i = i + 1\n}'
    assert run(src) == ["0", "1", "2"]


# ── each ──────────────────────────────────────────────────────────────────────
def test_each():
    src = 'grow lst as [1, 2, 3]\neach x in lst {\n  bloom x\n}'
    assert run(src) == ["1", "2", "3"]

def test_each_strings():
    src = 'each c in ["a","b","c"] {\n  bloom c\n}'
    assert run(src) == ["a", "b", "c"]


# ── plant / bear (functions) ──────────────────────────────────────────────────
def test_function_no_args():
    src = 'plant hi {\n  bloom "Hello"\n}\nhi()'
    assert run(src) == ["Hello"]

def test_function_with_args():
    src = 'plant add with a and b {\n  bear a + b\n}\nbloom add(3, 4)'
    assert run(src) == ["7"]

def test_function_return():
    src = 'plant double with n {\n  bear n * 2\n}\ngrow r as double(5)\nbloom r'
    assert run(src) == ["10"]

def test_recursion():
    src = '''
plant factorial with n {
    when n <= 1 { bear 1 }
    bear n * factorial(n - 1)
}
bloom factorial(5)
'''
    assert run(src) == ["120"]


# ── lists & strings ───────────────────────────────────────────────────────────
def test_list_index():
    assert run('grow l as [10, 20, 30]\nbloom l[1]') == ["20"]

def test_string_index():
    assert run('grow s as "hello"\nbloom s[0]') == ["h"]
    assert run('bloom "cat"[2]') == ["t"]

def test_list_out_of_range():
    run_err('grow l as [1, 2]\nbloom l[5]')

def test_string_out_of_range():
    run_err('bloom "hi"[-1]')


# ── built-ins ─────────────────────────────────────────────────────────────────
def test_length_list():  assert run('bloom length([1,2,3])') == ["3"]
def test_length_str():   assert run('bloom length("hello")') == ["5"]
def test_round():        assert run('bloom round(3.7)')       == ["4"]
def test_uppercase():    assert run('bloom uppercase("hi")')  == ["HI"]
def test_lowercase():    assert run('bloom lowercase("HI")')  == ["hi"]
def test_number():       assert run('bloom number("42")')     == ["42"]
def test_text():         assert run('bloom text(99)')         == ["99"]
def test_join():         assert run('bloom join(["a","b","c"], "-")') == ["a-b-c"]
def test_abs():          assert run('bloom abs(-7)')          == ["7"]
def test_max():          assert run('bloom max(3, 9, 1)')     == ["9"]
def test_min():          assert run('bloom min(3, 9, 1)')     == ["1"]
def test_pow():          assert run('bloom pow(2, 3)')        == ["8"]
def test_type():         assert run('bloom type(5)')          == ["number"]

def test_type_str():     assert run('bloom type("hi")')       == ["string"]
def test_constants():    assert run('bloom pi > 3.14')        == ["true"]



# ── harvest (input) ───────────────────────────────────────────────────────────
def test_harvest_string():
    src = 'harvest x with "?"\nbloom x'
    assert run(src, inputs=["Alice"]) == ["Alice"]

def test_harvest_number_coerce():
    src = 'harvest n with "?"\nbloom n + 1'
    assert run(src, inputs=["9"]) == ["10"]

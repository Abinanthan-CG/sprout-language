#!/usr/bin/env python3
"""
sprout.py — run a .sprout file or start the interactive REPL

  python sprout.py              → REPL
  python sprout.py hello.sprout → run file
"""

import sys
import os

# Make sure the interpreter package is importable regardless of cwd
sys.path.insert(0, os.path.dirname(__file__))

from interpreter.lexer import Lexer
from interpreter.parser import Parser
from interpreter.evaluator import Interpreter
from interpreter.errors import SproutError

VERSION = "1.0.0"
BANNER = f"""
  🌱  Welcome to Sprout v{VERSION}  🌱
  ───────────────────────────────
  Type your code and press Enter.
  Type  exit  or  quit  to leave.
  Type  help  for a quick guide.
"""

HELP_TEXT = """
┌─────────────────────────────────────────────┐
│  Sprout Quick Guide 🌿                       │
├─────────────────────────────────────────────┤
│  bloom "Hello!"           → print something │
│  grow name as "Alice"     → make a variable │
│  harvest x with "Guess: " → ask for input   │
│  when x > 5 { ... }       → if statement   │
│  otherwise { ... }        → else            │
│  water 10 times { ... }   → repeat N times  │
│  whilst x < 10 { ... }    → while loop      │
│  each item in list { .. } → for-each loop   │
│  plant add with a and b { → make a function │
│      bear a + b           →   return value  │
│  }                                          │
│  ~ this is a comment                        │
└─────────────────────────────────────────────┘
"""


def run_source(source: str, filename="<sprout>"):
    """Lex → parse → evaluate a Sprout source string."""
    try:
        tokens = Lexer(source).tokenize()
        tree = Parser(tokens).parse()
        Interpreter().run(tree)
    except SproutError as e:
        print(f"\n🌿  Error in {filename}:")
        print(f"   {e}\n")
    except Exception as e:
        print(f"\n💥  Unexpected problem: {e}\n")


def run_file(path: str):
    """Run a .sprout file."""
    try:
        with open(path, encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"🌿  File not found: '{path}'")
        sys.exit(1)
    run_source(source, filename=path)


def repl():
    """Interactive Read-Eval-Print Loop."""
    print(BANNER)
    buf = []

    while True:
        prompt = "  sprout> " if not buf else "       > "
        try:
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print("\n\n  🌱  Goodbye! Keep growing!\n")
            break

        if line.strip().lower() in ("exit", "quit"):
            print("\n  🌱  Goodbye! Keep growing!\n")
            break

        if line.strip().lower() == "help":
            print(HELP_TEXT)
            continue

        buf.append(line)

        # Decide whether the buffer is "complete":
        # complete when braces are balanced and not empty
        full = "\n".join(buf)
        if full.count("{") == full.count("}") and full.strip():
            run_source(full, "<repl>")
            buf = []


if __name__ == "__main__":
    if len(sys.argv) == 1:
        repl()
    elif len(sys.argv) == 2:
        run_file(sys.argv[1])
    else:
        print("Usage:  python sprout.py [file.sprout]")
        sys.exit(1)

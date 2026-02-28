# 🌱 Sprout — A Programming Language for Everyone

> **Note:** This language was "vibecoded" for fun and to test the capabilities of AI agents! 🤖✨ Everything from the lexer to the web playground was built autonomously based on natural language prompts.

Sprout is a programming language designed so that **even young children can read and write it**. It uses a natural, plant-based vocabulary and prioritizes readability, instant visual feedback, and friendly error messages.

---

## ✨ Try It Right Now

Open **`playground/index.html`** in any browser — **no installation needed**.  
The full Sprout interpreter runs right in the page.

---

## 🚀 Quick Start (CLI)

**Requirements:** Python 3.8+

```bash
# Run a Sprout program
python sprout.py examples/hello.sprout

# Start the interactive REPL
python sprout.py
```

---

## 📖 Language Guide

### 🌸 Print something — `bloom`

```sprout
bloom "Hello, World! 🌍"
bloom "The answer is " + 42
```

### 📦 Variables — `grow`

```sprout
grow name as "Alice"
grow score as 100
grow pi as 3.14159
```

### ✏️ Change a variable

```sprout
score = score + 10
name = "Bob"
```

### ❓ Ask for input — `harvest`

```sprout
harvest name with "What is your name? "
bloom "Hello, " + name + "!"
```

### 🤔 Conditions — `when` / `otherwise`

```sprout
when score > 90 {
    bloom "🏆 Amazing score!"
} otherwise {
    bloom "Keep trying! 🌱"
}
```

### 🔁 Repeat N times — `water`

```sprout
water 5 times {
    bloom "🌿 Growing..."
}
```

### 🔄 While loop — `whilst`

```sprout
grow x as 1
whilst x <= 10 {
    bloom x
    x = x + 1
}
```

### 📋 For-each loop — `each ... in`

```sprout
grow fruits as ["Apple", "Banana", "Mango"]
each fruit in fruits {
    bloom "🍎 " + fruit
}
```

### 🌿 Functions — `plant` / `bear`

```sprout
plant add with a and b {
    bear a + b
}

bloom "Result: " + add(3, 7)
```

### 💬 Comments

```sprout
~ This is a comment — Sprout ignores it!
```

---

## 🔢 Built-in Functions

| Function           | What it does             | Example                        |
| ------------------ | ------------------------ | ------------------------------ |
| `length(x)`        | Length of string or list | `length("hello")` → 5          |
| `number(x)`        | Convert to number        | `number("42")` → 42            |
| `text(x)`          | Convert to text          | `text(42)` → "42"              |
| `random(a,b)`      | Random integer a..b      | `random(1,10)`                 |
| `round(n)`         | Round a number           | `round(3.7)` → 4               |
| `floor(n)`         | Round down               | `floor(3.9)` → 3               |
| `ceil(n)`          | Round up                 | `ceil(3.1)` → 4                |
| `abs(n)`           | Absolute value           | `abs(-5)` → 5                  |
| `max(a,b)`         | Largest of values        | `max(3,7)` → 7                 |
| `min(a,b)`         | Smallest of values       | `min(3,7)` → 3                 |
| `sqrt(n)`          | Square root              | `sqrt(16)` → 4                 |
| `uppercase(s)`     | ALL CAPS                 | `uppercase("hi")` → "HI"       |
| `lowercase(s)`     | all lowercase            | `lowercase("HI")` → "hi"       |
| `join(lst, sep)`   | Join list into string    | `join(["a","b"], "-")` → "a-b" |
| `split(s, sep)`    | Split string to list     | `split("a,b", ",")`            |
| `contains(lst, x)` | Check if list has x      | `contains(nums, 5)`            |
| `add(lst, x)`      | Add x to list            | `add(fruits, "Kiwi")`          |
| `remove(lst, i)`   | Remove item at index     | `remove(lst, 0)`               |

---

## 📂 Project Structure

```
new language/
├── sprout.py              ← CLI entry point
├── interpreter/
│   ├── lexer.py           ← Tokenizer
│   ├── parser.py          ← AST builder
│   ├── evaluator.py       ← Tree-walking interpreter
│   ├── builtins.py        ← Built-in functions
│   ├── ast_nodes.py       ← AST dataclasses
│   └── errors.py          ← Friendly error classes
├── examples/
│   ├── hello.sprout
│   ├── guessing_game.sprout
│   ├── countdown.sprout
│   ├── quiz.sprout
│   └── functions.sprout
├── playground/
│   └── index.html         ← Browser playground (no install!)
└── tests/
    └── test_interpreter.py
```

---

## 🎓 Graduating to Python

Sprout concepts map directly to Python:

| Sprout               | Python               |
| -------------------- | -------------------- |
| `grow x as 5`        | `x = 5`              |
| `bloom "hi"`         | `print("hi")`        |
| `harvest x with "?"` | `x = input("?")`     |
| `when x > 5 { }`     | `if x > 5:`          |
| `otherwise { }`      | `else:`              |
| `water 5 times { }`  | `for _ in range(5):` |
| `whilst x < 10 { }`  | `while x < 10:`      |
| `each i in lst { }`  | `for i in lst:`      |
| `plant f with x { }` | `def f(x):`          |
| `bear value`         | `return value`       |

---

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
```

---

_Made with 🌱 love for curious minds everywhere._

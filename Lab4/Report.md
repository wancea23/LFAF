# Regular Expressions – Variant 3

### Course: Formal Languages & Finite Automata
### Author: Morosanu Ion

---

## Theory

A regular expression is a sequence of characters that defines a search pattern. They are used to describe sets of strings in a compact and formal way. Regular expressions are closely related to finite automata — in fact, every regular expression corresponds to a finite automaton that recognizes the same language, and vice versa.

Regular expressions are built from basic elements combined using operators:

- **Concatenation** — symbols written one after another mean they must appear in that order. For example `AB` means A followed by B.
- **Alternation (`|`)** — means "or". For example `A|B` means either A or B.
- **Kleene star (`*`)** — means zero or more repetitions of the preceding element.
- **Plus (`+`)** — means one or more repetitions of the preceding element.
- **Question mark (`?`)** — means zero or one occurrence (optional).
- **Exponent (`^N`)** — means exactly N repetitions of the preceding element.

Regular expressions are widely used in compilers, text editors, search engines, and input validation. Processing a regular expression dynamically means parsing its structure and interpreting each operator rather than hardcoding the output.

---

## Objectives

* Understand what regular expressions are and what they are used for.
* Implement a program that dynamically interprets regular expressions and generates valid strings conforming to them.
* Handle operators: `+`, `*`, `?`, `^N`, `|`, and grouping with parentheses.
* Limit unbounded repetitions (`*`, `+`) to a maximum of 5 to avoid extremely long strings.
* Implement a bonus step-by-step processing trace showing how each part of the regex is handled.

---

## Implementation description

The implementation is a single Python file with two functions: `get_count()` and `generate()`, plus a data section defining the three Variant 3 regular expressions.

The `get_count()` function translates a quantifier into a concrete repetition count. It receives the quantifier detected after a character or group and returns a random integer in the appropriate range: `+` gives 1–5, `*` gives 0–5, `?` gives 0 or 1, and an exact tuple from `^N` returns exactly N. If no quantifier is present it returns 1.

```python
def get_count(quantifier):
    if quantifier is None:
        return 1
    if quantifier == '+':
        return random.randint(1, MAX_REPEAT)
    if quantifier == '*':
        return random.randint(0, MAX_REPEAT)
    if quantifier == '?':
        return random.randint(0, 1)
    if isinstance(quantifier, tuple):
        return quantifier[1]
    return 1
```

The `generate()` function is the core of the implementation. It walks through the regex string character by character using an index `i`. When it encounters a `(` it finds the matching `)` by tracking depth, extracts the inside, splits by `|` to get the options, then checks what quantifier follows the closing parenthesis. When it encounters a plain character, it checks the next character for a quantifier in the same way. In both cases it calls `get_count()` to determine how many times to repeat, randomly picks from the options that many times, appends the result to the output string, and records the step for the processing trace.

```python
def generate(regex):
    result = ""
    steps = []
    i = 0

    while i < len(regex):
        if regex[i] == '(':
            j = i + 1
            depth = 1
            while j < len(regex) and depth > 0:
                if regex[j] == '(':
                    depth += 1
                elif regex[j] == ')':
                    depth -= 1
                j += 1

            inside = regex[i+1:j-1]
            options = inside.split('|')

            quantifier = None
            if j < len(regex) and regex[j] in ('+', '*', '?'):
                quantifier = regex[j]
                j += 1
            elif j < len(regex) and regex[j] == '^':
                n = int(regex[j+1])
                quantifier = ('exact', n)
                j += 2

            count = get_count(quantifier)
            chosen = [random.choice(options) for _ in range(count)]
            part = "".join(chosen)
            result += part
            steps.append(f"  group ({inside}) x{count} -> '{part}'")
            i = j

        else:
            char = regex[i]
            j = i + 1

            quantifier = None
            if j < len(regex) and regex[j] in ('+', '*', '?'):
                quantifier = regex[j]
                j += 1
            elif j < len(regex) and regex[j] == '^':
                n = int(regex[j+1])
                quantifier = ('exact', n)
                j += 2

            count = get_count(quantifier)
            part = char * count
            result += part
            steps.append(f"  char '{char}' x{count} -> '{part}'")
            i = j

    return result, steps
```

The three Variant 3 regular expressions are defined as plain strings and passed into `generate()`. For each regex, 5 sample strings are generated and printed, followed by the step-by-step processing trace of the last generation.

```python
regexes = [
    "O(P|Q|R)+2(3|4)",
    "A*B(C|D|E)F(G|H|I)^2",
    "J+K(L|M|N)*O?(P|Q)^3",
]
```

---

## Conclusions / Results

The regular expression generator was successfully implemented for all three Variant 3 expressions. The program dynamically interprets each regex without hardcoding any specific output, correctly handles all required operators, and caps unbounded repetitions at 5.

**Regex 1: `O(P|Q|R)+2(3|4)`**

Starts with `O`, followed by one or more of `P`, `Q`, or `R`, then the literal `2`, then either `3` or `4`.

```
Regex: O(P|Q|R)+2(3|4)
Samples:
  OPPP23
  OQ23
  OPPQPP23
  OQ24
  ORRQ24
Processing steps:
  char 'O' x1 -> 'O'
  group (P|Q|R) x3 -> 'PRP'
  char '2' x1 -> '2'
  group (3|4) x1 -> '3'
```

**Regex 2: `A*B(C|D|E)F(G|H|I)^2`**

Zero or more `A`, then `B`, then one of `C/D/E`, then `F`, then exactly two picks from `G/H/I`.

```
Regex: A*B(C|D|E)F(G|H|I)^2
Samples:
  AAAABEFIG
  AAAAABEFII
  AAAABCFIH
  AAABDFGI
  BEFGG
Processing steps:
  char 'A' x0 -> ''
  char 'B' x1 -> 'B'
  group (C|D|E) x1 -> 'D'
  char 'F' x1 -> 'F'
  group (G|H|I) x2 -> 'HI'
```

**Regex 3: `J+K(L|M|N)*O?(P|Q)^3`**

One or more `J`, then `K`, then zero or more of `L/M/N`, then an optional `O`, then exactly three picks from `P/Q`.

```
Regex: J+K(L|M|N)*O?(P|Q)^3
Samples:
  JJJJKLNMNQQQ
  JJJKNNNNLOQPQ
  JJKMNLQQQ
  JJJJKMQPQ
  JJJJKOPQQ
Processing steps:
  char 'J' x4 -> 'JJJJ'
  char 'K' x1 -> 'K'
  group (L|M|N) x0 -> ''
  char 'O' x1 -> 'O'
  group (P|Q) x3 -> 'QQP'
```

All outputs match the expected examples from the task: `{OPP23, OQQQQ24}`, `{AAABCFGG, AAAAAABDFHH}`, `{JJKLOPPP, JKNQQQ}`. The processing trace correctly shows the order in which each part of the regex is evaluated, satisfying the bonus requirement.

---

## References

1. FCIM UTM — Formal Languages & Finite Automata course page: https://else.fcim.utm.md/course/view.php?id=98
2. Task description: https://github.com/filpatterson/DSL_laboratory_works/blob/master/4_regular_expressions/task.md
3. Regular expressions – Wikipedia: https://en.wikipedia.org/wiki/Regular_expression
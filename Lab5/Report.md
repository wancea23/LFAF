# Lab 5 — Chomsky Normal Form

**Course:** Formal Languages & Finite Automata  
**Author:** Morosanu Ion 
**Variant:** 15

---

## Theory

A **Context-Free Grammar** G = (V_N, V_T, P, S) is in **Chomsky Normal Form (CNF)** when every production has one of two shapes:

```
A → B C      (exactly two non-terminals)
A → a        (exactly one terminal)
```

(with the sole exception that S → ε is permitted if ε is in the language).

Any CFG can be reduced to CNF in five successive steps:

| # | Step | What it removes |
|---|------|-----------------|
| 1 | Eliminate ε-productions | A → ε for A ≠ S |
| 2 | Eliminate unit/renaming productions | A → B |
| 3 | Eliminate inaccessible symbols | symbols unreachable from S |
| 4 | Eliminate non-productive symbols | symbols that never yield a terminal string |
| 5 | Binarise & replace terminals | produces pure CNF shape |

---

## Objectives

1. Understand Chomsky Normal Form.  
2. Implement each normalisation step as a distinct method.  
3. Wrap everything in a reusable `Grammar` class that accepts **any** grammar (bonus ✓).  
4. Verify correctness with unit tests.

---

## Variant 15 Grammar

```
G = (V_N, V_T, P, S)
V_N = { S, A, B, C, D }
V_T = { a, b }

1.  S → A C          6.  A → a S
2.  S → b A          7.  A → A B a b
3.  S → B            8.  B → a
4.  S → a A          9.  B → b S
5.  A → ε           10.  C → a b C
                    11.  D → A B
```

---

## Implementation

### Project Structure

```
cnf/
├── grammar.py   # Grammar class — all 5 normalisation steps
└── main.py      # Variant 15 definition, runner, unit tests
```

### `Grammar` class (grammar.py)

Productions are stored as `dict[str, set[tuple[str, ...]]]`; an empty
tuple `()` represents ε. Every public method mutates `self` in-place and
returns a diagnostic value (nullable set, removed symbols, …).

```python
class Grammar:
    def __init__(self, VN, VT, productions, start): ...
    def eliminate_epsilon(self)          -> set: ...
    def eliminate_unit_productions(self) -> None: ...
    def eliminate_inaccessible(self)     -> set: ...
    def eliminate_non_productive(self)   -> set: ...
    def to_cnf(self)                     -> None: ...
    def normalize(self)                  -> Grammar: ...   # full pipeline
```

`normalize()` chains all five steps and prints each intermediate grammar.

#### Step 1 — Eliminate ε-productions

Find the *nullable* set (fixed-point computation), then for every
production containing a nullable symbol generate all variants obtained
by deleting any subset of those occurrences:

```python
nullable_pos = [i for i, s in enumerate(prod) if s in nullable]
for r in range(len(nullable_pos) + 1):
    for remove in combinations(nullable_pos, r):
        new_prod = tuple(s for i, s in enumerate(prod) if i not in remove)
        ...
```

#### Step 2 — Eliminate unit productions

Build the reflexive-transitive *unit closure* by repeatedly finding
A →* B chains, then replace each (A, B) pair with B's non-unit
productions added directly under A.

#### Step 3 — Eliminate inaccessible symbols

BFS/fixed-point reachability from S; any non-terminal not visited is
dropped along with all its productions.

#### Step 4 — Eliminate non-productive symbols

Grow the *productive* set bottom-up: a symbol is productive when at
least one of its productions consists only of terminals and already
productive non-terminals. Remove the rest.

#### Step 5 — Convert to CNF

Two kinds of new helper variables are introduced:

- `T1`, `T2`, … — stand-in for a terminal inside a production of
  length ≥ 2 (e.g. `T1 → a`).
- `X1`, `X2`, … — right-fold binarisation variable for productions of
  length ≥ 3 (e.g. `X1 → T1 T2`).

The transformation loops until a fixed point is reached (all productions
already satisfy CNF).

---

## Trace — Variant 15

### After Step 1 (ε-elimination)

Nullable = { A }. Productions added by dropping A from every occurrence:

```
S → A C | C | b A | b | B | a A | a
A → A B a b | B a b | a S
D → A B | B
```

### After Step 2 (unit elimination)

Unit pairs: (S,B), (S,C), (D,B).  
Non-unit productions of B and C are folded into S and D:

```
S → A C | a | a A | a b C | b | b A | b S
D → A B | a | b S
```

### After Step 3 (inaccessible)

D is unreachable from S → removed.

### After Step 4 (non-productive)

C → a b C has no base case; C never produces a terminal string.  
C (and S → A C, S → a b C) are removed.

Grammar before CNF conversion:

```
S → a | a A | b | b A | b S
A → a S | A B a b | B a b
B → a | b S
```

### After Step 5 (CNF)

New variables introduced:

| Variable | Production | Represents |
|----------|------------|------------|
| T1       | T1 → a     | terminal a in long rules |
| T2       | T2 → b     | terminal b in long rules |
| X1       | X1 → T1 T2 | the substring "ab" |
| X2       | X2 → B X1  | the substring "Bab" |

**Final CNF grammar:**

```
S  → T1 A  |  T2 A  |  T2 S  |  a  |  b
A  → T1 S  |  A X2  |  B X1
B  → a     |  T2 S
T1 → a
T2 → b
X1 → T1 T2
X2 → B X1
```

---

## Unit Tests

Six tests are executed automatically by `main.py`:

| # | Test | Result |
|---|------|--------|
| 1 | Variant 15 final grammar satisfies CNF rules | PASS ✓ |
| 2 | Start symbol S preserved in final VN | PASS ✓ |
| 3 | No ε-productions remain (except possibly S) | PASS ✓ |
| 4 | No unit productions remain | PASS ✓ |
| 5 | Trivial grammar (S→a \| b) unchanged | PASS ✓ |
| 6 | Grammar with nullable A normalises correctly | PASS ✓ |

---

## Conclusions

- The five normalisation steps must be applied in the order shown; later
  steps rely on the invariants established by earlier ones (e.g. step 3
  is cheaper after step 2 has removed spurious unit derivations).
- Non-productive symbol removal (step 4) can discard reachable symbols —
  C was reachable from S but still non-productive.
- The `Grammar` class accepts any CFG, not just Variant 15, satisfying
  the bonus requirement.

---

## References

1. [Chomsky Normal Form — Wikipedia](https://en.wikipedia.org/wiki/Chomsky_normal_form)  
2. Hopcroft, Motwani, Ullman — *Introduction to Automata Theory, Languages, and Computation*, 3rd ed.
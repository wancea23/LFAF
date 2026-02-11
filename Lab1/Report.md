# Grammar to Finite Automaton Conversion – Variant 15

### Course: Formal Languages & Finite Automata  
### Author: Ion Moroșanu  

----

## Theory

A formal grammar is defined as a 4-tuple \( G = (V_N, V_T, P, S) \), where:
- \( V_N \) represents the set of non-terminals,
- \( V_T \) represents the set of terminals,
- \( P \) represents the production rules,
- \( S \) is the start symbol.

A right-linear grammar is a type of regular grammar where production rules have the form:

- \( A → aB \)
- \( A → a \)

Such grammars are equivalent to finite automata. Each production can be directly transformed into a transition of a finite automaton.

For this laboratory work, the given grammar is:

**VN** = {S, A, B}  
**VT** = {a, b, c}  

**Productions**:

- S → aS  
- S → bS  
- S → cA  
- A → aB  
- B → aB  
- B → bB  
- B → c  

Since the grammar is right-linear, it can be converted into a deterministic finite automaton (DFA).

---

## Objectives:

* Implement a Grammar class capable of generating valid strings.
* Convert the grammar into a Finite Automaton.
* Implement a FiniteAutomaton class that verifies if a string belongs to the language.
* Demonstrate the functionality through execution examples.
* Respect the requirement of using the two main classes.

---

## Implementation description

The implementation was done in Python in a single file containing two main classes: `Grammar` and `FiniteAutomaton`.

The `Grammar` class stores the sets of non-terminals, terminals, and the start symbol. It contains a method `generate_string()` which simulates the application of production rules randomly until a terminal string is obtained.

The `to_finite_automaton()` method converts the grammar into a finite automaton by mapping each production rule to a transition. For example, the production `S → aS` becomes a transition from state S to S on symbol `a`.

The `FiniteAutomaton` class contains the states, alphabet, transition function, start state, and final states. The method `string_belong_to_language()` simulates the automaton step by step and verifies whether the final state is reached after reading the entire input string.

The `main()` function demonstrates:
- generation of 5 valid strings,
- validation of multiple test strings.

---

### Code snippet - FiniteAutomaton class

```python
class FiniteAutomaton:
    def __init__(self, states, alphabet, transitions, start_state, final_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.final_states = final_states

    def string_belong_to_language(self, input_string: str) -> bool:
        current_state = self.start_state

        for symbol in input_string:
            if symbol not in self.alphabet:
                return False

            if current_state not in self.transitions:
                return False

            if symbol not in self.transitions[current_state]:
                return False

            current_state = self.transitions[current_state][symbol]

        return current_state in self.final_states
```

### Code snippet - Grammar class

```python
class Grammar:
    def __init__(self):
        self.non_terminals = {"S", "A", "B"}
        self.terminals = {"a", "b", "c"}
        self.start_symbol = "S"

    def generate_string(self) -> str:
        current = self.start_symbol
        result = ""

        while current != "FINAL":
            if current == "S":
                choice = random.choice(["a", "b", "c"])
                if choice in ["a", "b"]:
                    result += choice
                    current = "S"
                else:
                    result += "c"
                    current = "A"

            elif current == "A":
                result += "a"
                current = "B"

            elif current == "B":
                choice = random.choice(["a", "b", "c"])
                if choice in ["a", "b"]:
                    result += choice
                    current = "B"
                else:
                    result += "c"
                    current = "FINAL"

        return result
```
### Code snippet - Main execution

```python
def main():
    grammar = Grammar()

    print("Generated strings:")
    for i in range(5):
        print(f"{i+1}. {grammar.generate_string()}")

    fa = grammar.to_finite_automaton()

    print("\nString validation:")
    test_strings = ["abc", "aac", "abbbc", "cc", "bba", "abac"]

    for s in test_strings:
        print(f"{s} -> {fa.string_belong_to_language(s)}")
```

## Conclusions / Screenshots / Results

The grammar was successfully implemented and converted into a deterministic finite automaton.

The generated strings follow the pattern:

```python
(a|b)* c a (a|b)* c
```


The finite automaton correctly validates whether a string belongs to the language by checking if it ends in the final state.

All tested invalid strings were rejected, while generated valid strings were accepted.

Output of program execution:
```python
Generated strings:
1. acaac
2. bcaac
3. abcaaaac
4. abbaacac
5. acabbbac

String validation:
abc -> False
aac -> False
abbbc -> False
cc -> False
bba -> False
abac -> False
```
import random

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


class Grammar:
    def __init__(self):
        # VN, VT, S
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
                else:  # c
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
                else:  # c
                    result += "c"
                    current = "FINAL"

        return result

    def to_finite_automaton(self) -> FiniteAutomaton:
        states = {"S", "A", "B", "FINAL"}
        alphabet = {"a", "b", "c"}
        start_state = "S"
        final_states = {"FINAL"}

        transitions = {
            "S": {"a": "S", "b": "S", "c": "A"},
            "A": {"a": "B"},
            "B": {"a": "B", "b": "B", "c": "FINAL"}
        }

        return FiniteAutomaton(
            states,
            alphabet,
            transitions,
            start_state,
            final_states
        )


def main():
    grammar = Grammar()

    print("Generated strings:")
    for i in range(5):
        print(f"{i+1}. {grammar.generate_string()}")

    fa = grammar.to_finite_automaton()

    print("\nString validation:")
    test_strings = ["cac", "abcac", "bcabc", "cc", "bba", "cbc"]

    for s in test_strings:
        print(f"{s} -> {fa.string_belong_to_language(s)}")


if __name__ == "__main__":
    main()

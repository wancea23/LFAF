import random

MAX_REPEAT = 5


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


regexes = [
    "O(P|Q|R)+2(3|4)",
    "A*B(C|D|E)F(G|H|I)^2",
    "J+K(L|M|N)*O?(P|Q)^3",
]

for regex in regexes:
    print(f"\nRegex: {regex}")
    print("Samples:")
    for _ in range(5):
        result, _ = generate(regex)
        print(f"  {result}")
    _, steps = generate(regex)
    print("Processing steps:")
    for step in steps:
        print(step)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

states   = {"S", "A", "B", "FINAL"}
alphabet = {"a", "b", "c"}
start    = "S"
finals   = {"FINAL"}

transitions = {
    "S": {"a": ["S"], "b": ["S"], "c": ["A"]},
    "A": {"a": ["B"]},
    "B": {"a": ["B"], "b": ["B"], "c": ["FINAL"]},
}

def fa_to_grammar(transitions, finals):
    productions = {}
    for state, sym_map in transitions.items():
        productions[state] = []
        for symbol, targets in sym_map.items():
            for target in targets:
                if target in finals:
                    productions[state].append(symbol)       
                else:
                    productions[state].append(f"{symbol}{target}") 
    return productions

def is_deterministic(transitions):
    for state, sym_map in transitions.items():
        for symbol, targets in sym_map.items():
            if len(targets) > 1:
                return False
    return True

def ndfa_to_dfa(transitions, start, finals, alphabet):
    def name(fs):
        return "{" + ",".join(sorted(fs)) + "}"

    start_set = frozenset([start])
    unmarked  = [start_set]
    visited   = {start_set}
    dfa_trans = {}
    dfa_finals = set()

    while unmarked:
        current = unmarked.pop()
        dfa_trans[name(current)] = {}
        for symbol in alphabet:
            next_set = set()
            for state in current:
                if state in transitions and symbol in transitions[state]:
                    next_set.update(transitions[state][symbol])
            if not next_set:
                continue
            nf = frozenset(next_set)
            dfa_trans[name(current)][symbol] = [name(nf)]
            if nf not in visited:
                visited.add(nf)
                unmarked.append(nf)
        if current & finals:
            dfa_finals.add(name(current))

    return dfa_trans, name(start_set), dfa_finals

# Drawing
def draw_fa(transitions, start, finals, alphabet, filename="fa.png", title="Finite Automaton"):
    G = nx.MultiDiGraph()
    for state in transitions:
        G.add_node(state)

    edge_labels = {}
    for state, sym_map in transitions.items():
        for symbol, targets in sym_map.items():
            for target in targets:
                G.add_edge(state, target)
                key = (state, target)
                edge_labels[key] = edge_labels.get(key, "") + symbol + ","

    edge_labels = {k: v.rstrip(",") for k, v in edge_labels.items()}

    pos = nx.spring_layout(G, seed=42, k=2)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_title(title, fontsize=13)
    ax.axis("off")

    node_colors = []
    for node in G.nodes():
        if node in finals:
            node_colors.append("#90ee90")
        elif node == start:
            node_colors.append("#add8e6")
        else:
            node_colors.append("#ffffff")

    nx.draw_networkx_nodes(G, pos, node_size=1800, node_color=node_colors,
                           edgecolors="black", linewidths=1.5, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=11, ax=ax)
    nx.draw_networkx_edges(G, pos, ax=ax, arrows=True,
                           arrowstyle="-|>", arrowsize=20,
                           connectionstyle="arc3,rad=0.15",
                           edge_color="gray", width=1.5)

    for (u, v), label in edge_labels.items():
        x = (pos[u][0] + pos[v][0]) / 2
        y = (pos[u][1] + pos[v][1]) / 2 + 0.1
        ax.text(x, y, label, fontsize=9, ha="center",
                bbox=dict(boxstyle="round,pad=0.2", fc="lightyellow", ec="gray"))

    legend = [
        mpatches.Patch(color="#add8e6", label="Start state"),
        mpatches.Patch(color="#90ee90", label="Final state"),
        mpatches.Patch(color="white",   label="Normal state", linewidth=1),
    ]
    ax.legend(handles=legend, loc="upper left", fontsize=9)

    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    print(f"Graph saved to {filename}")

# helpers
def print_table(transitions, start, finals, alphabet, title):
    print(f"\n{title}")
    symbols = sorted(alphabet)
    print(f"{'State':<20}" + "".join(f"{s:<15}" for s in symbols))
    for state in sorted(transitions.keys()):
        prefix = ("*" if state in finals else "") + ("->" if state == start else "")
        row = f"{prefix + state:<20}"
        for sym in symbols:
            targets = transitions.get(state, {}).get(sym, [])
            row += f"{str(targets if targets else '-'):<15}"
        print(row)

print("\na) FA to Regular Grammar")
grammar = fa_to_grammar(transitions, finals)
for state, prods in grammar.items():
    if prods:
        print(f"  {state} -> {' | '.join(prods)}")

print("\nb) Determinism check")
print_table(transitions, start, finals, alphabet, "Original FA")
det = is_deterministic(transitions)
print(f"\n  Is deterministic: {det}")

print("\nc) NDFA -> DFA conversion")
ndfa_transitions = {
    "S": {"a": ["S", "A"], "b": ["S"], "c": ["A"]},
    "A": {"a": ["B"]},
    "B": {"a": ["B"], "b": ["B"], "c": ["FINAL"]},
}
ndfa_start  = "S"
ndfa_finals = {"FINAL"}

print_table(ndfa_transitions, ndfa_start, ndfa_finals, alphabet, "NDFA (modified)")
print(f"  Is deterministic: {is_deterministic(ndfa_transitions)}")

dfa_trans, dfa_start, dfa_finals = ndfa_to_dfa(ndfa_transitions, ndfa_start, ndfa_finals, alphabet)
print_table(dfa_trans, dfa_start, dfa_finals, alphabet, "DFA after subset construction")
print(f"  Is deterministic: {is_deterministic(dfa_trans)}")

print("\nd) Graphical representation")
draw_fa(transitions, start, finals, alphabet,
        filename="fa_original.png",
        title="Original FA")

draw_fa(dfa_trans, dfa_start, dfa_finals, alphabet,
        filename="fa_dfa.png",
        title="DFA after conversion")
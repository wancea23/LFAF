from itertools import combinations


class Grammar:
    def __init__(self, VN, VT, productions: dict, start: str):
        self.VN: set[str] = set(VN)
        self.VT: set[str] = set(VT)
        self.S = start
        self.P: dict[str, set[tuple]] = {}
        for nt, prods in productions.items():
            self.P[nt] = {tuple(p) for p in prods}

    def display(self, title: str = ""):
        if title:
            _hdr(title)
        print(f"  VN = {{ {', '.join(sorted(self.VN))} }}")
        print(f"  VT = {{ {', '.join(sorted(self.VT))} }}")
        print(f"  S  = {self.S}")
        print("  Productions:")
        for nt in sorted(self.P):
            for rhs in sorted(" ".join(p) if p else "ε" for p in self.P[nt]):
                print(f"    {nt} → {rhs}")

    def eliminate_epsilon(self) -> set:
        nullable: set[str] = {nt for nt, ps in self.P.items() if () in ps}

        changed = True
        while changed:
            changed = False
            for nt, prods in self.P.items():
                if nt not in nullable:
                    for prod in prods:
                        if prod and all(s in nullable for s in prod):
                            nullable.add(nt)
                            changed = True
                            break

        print(f"  Nullable variables : {nullable or 'none'}")

        new_P: dict[str, set[tuple]] = {}
        for nt, prods in self.P.items():
            new_prods: set[tuple] = set()
            for prod in prods:
                if prod == ():
                    continue
                null_pos = [i for i, s in enumerate(prod) if s in nullable]
                for r in range(len(null_pos) + 1):
                    for remove in combinations(null_pos, r):
                        new_prod = tuple(s for i, s in enumerate(prod) if i not in remove)
                        if new_prod or nt == self.S:
                            new_prods.add(new_prod)
            new_P[nt] = new_prods

        if self.S in nullable:
            new_P[self.S].add(())

        self.P = new_P
        return nullable

    def eliminate_unit_productions(self):
        unit_pairs: set[tuple[str, str]] = {(nt, nt) for nt in self.VN}
        changed = True
        while changed:
            changed = False
            for (A, B) in list(unit_pairs):
                for prod in self.P.get(B, set()):
                    if len(prod) == 1 and prod[0] in self.VN:
                        pair = (A, prod[0])
                        if pair not in unit_pairs:
                            unit_pairs.add(pair)
                            changed = True

        new_P: dict[str, set[tuple]] = {nt: set() for nt in self.VN}
        for (A, B) in unit_pairs:
            for prod in self.P.get(B, set()):
                if not (len(prod) == 1 and prod[0] in self.VN):
                    new_P[A].add(prod)

        self.P = new_P

    def eliminate_inaccessible(self) -> set:
        reachable: set[str] = {self.S}
        changed = True
        while changed:
            changed = False
            for nt in list(reachable):
                for prod in self.P.get(nt, set()):
                    for sym in prod:
                        if sym in self.VN and sym not in reachable:
                            reachable.add(sym)
                            changed = True

        inaccessible = self.VN - reachable
        print(f"  Inaccessible symbols removed : {inaccessible or 'none'}")
        self.VN = reachable
        self.P = {nt: ps for nt, ps in self.P.items() if nt in reachable}
        return inaccessible

    def eliminate_non_productive(self) -> set:
        productive: set[str] = set()
        changed = True
        while changed:
            changed = False
            for nt, prods in self.P.items():
                if nt not in productive:
                    for prod in prods:
                        if prod and all(s in self.VT or s in productive for s in prod):
                            productive.add(nt)
                            changed = True
                            break

        non_productive = self.VN - productive
        print(f"  Non-productive symbols removed : {non_productive or 'none'}")
        self.VN = productive
        self.P = {
            nt: {prod for prod in ps if all(s in self.VT or s in productive for s in prod)}
            for nt, ps in self.P.items() if nt in productive
        }
        return non_productive

    def to_cnf(self):
        terminal_var: dict[str, str] = {}
        pair_var: dict[tuple, str] = {}
        t_ctr = [0]
        p_ctr = [0]

        def _fresh(prefix: str) -> str:
            ctr = t_ctr if prefix == "T" else p_ctr
            while True:
                ctr[0] += 1
                name = f"{prefix}{ctr[0]}"
                if name not in self.VN:
                    return name

        def _term_var(t: str) -> str:
            if t not in terminal_var:
                name = _fresh("T")
                terminal_var[t] = name
                self.VN.add(name)
                self.P[name] = {(t,)}
            return terminal_var[t]

        def _pair_var(s1: str, s2: str) -> str:
            key = (s1, s2)
            if key not in pair_var:
                name = _fresh("X")
                pair_var[key] = name
                self.VN.add(name)
                self.P[name] = {key}
            return pair_var[key]

        changed = True
        while changed:
            changed = False
            new_P: dict[str, set[tuple]] = {}

            for nt in list(self.P):
                new_prods: set[tuple] = set()
                for prod in list(self.P.get(nt, set())):
                    if (len(prod) == 0
                            or (len(prod) == 1 and prod[0] in self.VT)
                            or (len(prod) == 2 and all(s in self.VN for s in prod))):
                        new_prods.add(prod)
                        continue

                    changed = True
                    syms = list(prod)

                    if len(syms) > 1:
                        syms = [_term_var(s) if s in self.VT else s for s in syms]

                    while len(syms) > 2:
                        v = _pair_var(syms[-2], syms[-1])
                        syms = syms[:-2] + [v]

                    new_prods.add(tuple(syms))

                new_P[nt] = new_prods

            for nt, ps in self.P.items():
                if nt not in new_P:
                    new_P[nt] = ps

            self.P = new_P

    def normalize(self) -> "Grammar":
        self.display("ORIGINAL GRAMMAR")

        _hdr("STEP 1 - Eliminate e-productions")
        self.eliminate_epsilon()
        self.display()

        _hdr("STEP 2 - Eliminate unit (renaming) productions")
        self.eliminate_unit_productions()
        self.display()

        _hdr("STEP 3 - Eliminate inaccessible symbols")
        self.eliminate_inaccessible()
        self.display()

        _hdr("STEP 4 - Eliminate non-productive symbols")
        self.eliminate_non_productive()
        self.display()

        _hdr("STEP 5 - Convert to Chomsky Normal Form")
        self.to_cnf()
        self.display()

        _hdr("NORMALISATION COMPLETE")
        return self


def _hdr(text: str, width: int = 58):
    print(f"\n{'='*width}")
    print(f"  {text}")
    print(f"{'='*width}")


def is_cnf(g: Grammar) -> bool:
    for nt, prods in g.P.items():
        for prod in prods:
            ok = (
                (len(prod) == 1 and prod[0] in g.VT) or
                (len(prod) == 2 and all(s in g.VN for s in prod)) or
                (len(prod) == 0 and nt == g.S)
            )
            if not ok:
                return False
    return True


def build_variant15() -> Grammar:
    return Grammar(
        VN=["S", "A", "B", "C", "D"],
        VT=["a", "b"],
        productions={
            "S": [["A", "C"], ["b", "A"], ["B"], ["a", "A"]],
            "A": [[], ["a", "S"], ["A", "B", "a", "b"]],
            "B": [["a"], ["b", "S"]],
            "C": [["a", "b", "C"]],
            "D": [["A", "B"]],
        },
        start="S",
    )


def run_tests():
    _hdr("UNIT TESTS")
    passed = failed = 0

    def check(label: str, condition: bool):
        nonlocal passed, failed
        mark = "PASS" if condition else "FAIL"
        print(f"  [{mark}]  {label}")
        passed += condition
        failed += not condition

    g1 = build_variant15()
    g1.normalize()
    check("Variant 15 result satisfies CNF rules", is_cnf(g1))
    check("Start symbol S present in final VN", "S" in g1.VN)
    check("No e-productions remain (except possibly S)",
          not any(() in ps and nt != g1.S for nt, ps in g1.P.items()))
    check("No unit productions remain",
          not any(any(len(p) == 1 and p[0] in g1.VN for p in ps)
                  for ps in g1.P.values()))

    g2 = Grammar(VN=["S"], VT=["a", "b"],
                 productions={"S": [["a"], ["b"]]}, start="S")
    g2.normalize()
    check("Trivial grammar (S->a | S->b) survives normalization", is_cnf(g2))

    g3 = Grammar(VN=["S", "A", "B"], VT=["a", "b"],
                 productions={"S": [["A", "B"], ["a"]], "A": [[], ["a"]], "B": [["b"]]},
                 start="S")
    g3.normalize()
    check("Grammar with nullable A normalises correctly", is_cnf(g3))

    print(f"\n  Results: {passed} passed, {failed} failed")
    print("=" * 58)
    return failed == 0


if __name__ == "__main__":
    print("=" * 58)
    print("  Chomsky Normal Form Normalizer  -  Variant 15")
    print("=" * 58)

    build_variant15().normalize()

    success = run_tests()
    exit(0 if success else 1)
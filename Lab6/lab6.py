import re
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional

#  TOKEN TYPES

class TokenType(Enum):
    NUMBER     = auto()
    STRING     = auto()
    IDENT      = auto()
    PLUS       = auto()
    MINUS      = auto()
    STAR       = auto()
    SLASH      = auto()
    ASSIGN     = auto()
    EQ         = auto()
    NEQ        = auto()
    LT         = auto()
    GT         = auto()
    LTE        = auto()
    GTE        = auto()
    LPAREN     = auto()
    RPAREN     = auto()
    LBRACE     = auto()
    RBRACE     = auto()
    SEMICOLON  = auto()
    IF         = auto()
    ELSE       = auto()
    WHILE      = auto()
    PRINT      = auto()
    EOF        = auto()


TOKEN_PATTERNS: list[tuple[TokenType, str]] = [
    (TokenType.NUMBER,    r'\d+(\.\d+)?'),
    (TokenType.STRING,    r'"[^"]*"'),
    (TokenType.EQ,        r'=='),
    (TokenType.NEQ,       r'!='),
    (TokenType.LTE,       r'<='),
    (TokenType.GTE,       r'>='),
    (TokenType.LT,        r'<'),
    (TokenType.GT,        r'>'),
    (TokenType.ASSIGN,    r'='),
    (TokenType.PLUS,      r'\+'),
    (TokenType.MINUS,     r'-'),
    (TokenType.STAR,      r'\*'),
    (TokenType.SLASH,     r'/'),
    (TokenType.LPAREN,    r'\('),
    (TokenType.RPAREN,    r'\)'),
    (TokenType.LBRACE,    r'\{'),
    (TokenType.RBRACE,    r'\}'),
    (TokenType.SEMICOLON, r';'),
    (TokenType.IDENT,     r'[a-zA-Z_]\w*'),
]

KEYWORDS = {
    'if':    TokenType.IF,
    'else':  TokenType.ELSE,
    'while': TokenType.WHILE,
    'print': TokenType.PRINT,
}
#  TOKEN

@dataclass
class Token:
    type:  TokenType
    value: str
    line:  int

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, line={self.line})"

#  LEXER

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos    = 0
        self.line   = 1
        self.tokens: list[Token] = []

    def tokenize(self) -> list[Token]:
        while self.pos < len(self.source):
            if self.source[self.pos] in ' \t\r':
                self.pos += 1
                continue
            if self.source[self.pos] == '\n':
                self.line += 1
                self.pos  += 1
                continue
            if self.source[self.pos:self.pos+2] == '//':
                while self.pos < len(self.source) and self.source[self.pos] != '\n':
                    self.pos += 1
                continue

            matched = False
            for ttype, pattern in TOKEN_PATTERNS:
                m = re.match(pattern, self.source[self.pos:])
                if m:
                    value = m.group(0)
                    if ttype == TokenType.IDENT and value in KEYWORDS:
                        ttype = KEYWORDS[value]
                    self.tokens.append(Token(ttype, value, self.line))
                    self.pos += len(value)
                    matched = True
                    break

            if not matched:
                raise SyntaxError(f"Unknown character {self.source[self.pos]!r} at line {self.line}")

        self.tokens.append(Token(TokenType.EOF, '', self.line))
        return self.tokens
    
@dataclass
class NumberNode:
    value: float

@dataclass
class StringNode:
    value: str

@dataclass
class IdentNode:
    name: str

@dataclass
class BinOpNode:
    op:    str
    left:  object
    right: object

@dataclass
class UnaryOpNode:
    op:      str
    operand: object

@dataclass
class AssignNode:
    name:  str
    value: object

@dataclass
class PrintNode:
    expr: object

@dataclass
class IfNode:
    condition:   object
    then_branch: list
    else_branch: list = field(default_factory=list)

@dataclass
class WhileNode:
    condition: object
    body:      list

@dataclass
class ProgramNode:
    statements: list

class Parser:
    """
    Recursive-descent parser.

    Grammar:
        program    → statement* EOF
        statement  → assign | print | if | while | expr SEMICOLON
        assign     → IDENT = expr SEMICOLON
        print      → print expr SEMICOLON
        if         → if expr { program } (else { program })?
        while      → while expr { program }
        expr       → comparison
        comparison → addition ((== | != | < | > | <= | >=) addition)*
        addition   → term ((+ | -) term)*
        term       → factor ((* | /) factor)*
        factor     → NUMBER | STRING | IDENT | ( expr ) | - factor
    """

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos    = 0

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def consume(self, expected: Optional[TokenType] = None) -> Token:
        tok = self.tokens[self.pos]
        if expected and tok.type != expected:
            raise SyntaxError(
                f"Expected {expected.name} but got {tok.type.name} "
                f"({tok.value!r}) at line {tok.line}"
            )
        self.pos += 1
        return tok

    def match(self, *types: TokenType) -> bool:
        return self.peek().type in types

    def parse(self) -> ProgramNode:
        node = self.parse_program()
        self.consume(TokenType.EOF)
        return node

    def parse_program(self) -> ProgramNode:
        stmts = []
        while not self.match(TokenType.EOF, TokenType.RBRACE):
            stmts.append(self.parse_statement())
        return ProgramNode(stmts)

    def parse_statement(self):
        tok = self.peek()

        if tok.type == TokenType.IDENT and self.pos + 1 < len(self.tokens) \
                and self.tokens[self.pos + 1].type == TokenType.ASSIGN:
            return self.parse_assign()

        if tok.type == TokenType.PRINT:
            return self.parse_print()

        if tok.type == TokenType.IF:
            return self.parse_if()

        if tok.type == TokenType.WHILE:
            return self.parse_while()

        expr = self.parse_expr()
        self.consume(TokenType.SEMICOLON)
        return expr

    def parse_assign(self) -> AssignNode:
        name = self.consume(TokenType.IDENT).value
        self.consume(TokenType.ASSIGN)
        value = self.parse_expr()
        self.consume(TokenType.SEMICOLON)
        return AssignNode(name, value)

    def parse_print(self) -> PrintNode:
        self.consume(TokenType.PRINT)
        expr = self.parse_expr()
        self.consume(TokenType.SEMICOLON)
        return PrintNode(expr)

    def parse_if(self) -> IfNode:
        self.consume(TokenType.IF)
        condition = self.parse_expr()
        self.consume(TokenType.LBRACE)
        then_branch = self.parse_program().statements
        self.consume(TokenType.RBRACE)
        else_branch = []
        if self.match(TokenType.ELSE):
            self.consume(TokenType.ELSE)
            self.consume(TokenType.LBRACE)
            else_branch = self.parse_program().statements
            self.consume(TokenType.RBRACE)
        return IfNode(condition, then_branch, else_branch)

    def parse_while(self) -> WhileNode:
        self.consume(TokenType.WHILE)
        condition = self.parse_expr()
        self.consume(TokenType.LBRACE)
        body = self.parse_program().statements
        self.consume(TokenType.RBRACE)
        return WhileNode(condition, body)

    def parse_expr(self):
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_addition()
        while self.match(TokenType.EQ, TokenType.NEQ,
                         TokenType.LT, TokenType.GT,
                         TokenType.LTE, TokenType.GTE):
            op   = self.consume().value
            right = self.parse_addition()
            left  = BinOpNode(op, left, right)
        return left

    def parse_addition(self):
        left = self.parse_term()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op    = self.consume().value
            right = self.parse_term()
            left  = BinOpNode(op, left, right)
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.match(TokenType.STAR, TokenType.SLASH):
            op    = self.consume().value
            right = self.parse_factor()
            left  = BinOpNode(op, left, right)
        return left

    def parse_factor(self):
        tok = self.peek()

        if tok.type == TokenType.MINUS:
            self.consume()
            return UnaryOpNode('-', self.parse_factor())

        if tok.type == TokenType.NUMBER:
            self.consume()
            return NumberNode(float(tok.value))

        if tok.type == TokenType.STRING:
            self.consume()
            return StringNode(tok.value[1:-1])

        if tok.type == TokenType.IDENT:
            self.consume()
            return IdentNode(tok.value)

        if tok.type == TokenType.LPAREN:
            self.consume()
            expr = self.parse_expr()
            self.consume(TokenType.RPAREN)
            return expr

        raise SyntaxError(
            f"Unexpected token {tok.type.name} ({tok.value!r}) at line {tok.line}"
        )

def print_ast(node, indent: int = 0):
    pad = "  " * indent
    match node:
        case ProgramNode(stmts):
            print(f"{pad}Program")
            for s in stmts:
                print_ast(s, indent + 1)
        case AssignNode(name, value):
            print(f"{pad}Assign: {name}")
            print_ast(value, indent + 1)
        case PrintNode(expr):
            print(f"{pad}Print")
            print_ast(expr, indent + 1)
        case IfNode(cond, then_b, else_b):
            print(f"{pad}If")
            print(f"{pad}  Condition:")
            print_ast(cond, indent + 2)
            print(f"{pad}  Then:")
            for s in then_b:
                print_ast(s, indent + 2)
            if else_b:
                print(f"{pad}  Else:")
                for s in else_b:
                    print_ast(s, indent + 2)
        case WhileNode(cond, body):
            print(f"{pad}While")
            print(f"{pad}  Condition:")
            print_ast(cond, indent + 2)
            print(f"{pad}  Body:")
            for s in body:
                print_ast(s, indent + 2)
        case BinOpNode(op, left, right):
            print(f"{pad}BinOp: {op!r}")
            print_ast(left,  indent + 1)
            print_ast(right, indent + 1)
        case UnaryOpNode(op, operand):
            print(f"{pad}UnaryOp: {op!r}")
            print_ast(operand, indent + 1)
        case NumberNode(v):
            print(f"{pad}Number: {v}")
        case StringNode(v):
            print(f"{pad}String: {v!r}")
        case IdentNode(name):
            print(f"{pad}Ident: {name}")
        case _:
            print(f"{pad}{node}")

class Interpreter:
    def __init__(self):
        self.env: dict = {}

    def run(self, node):
        match node:
            case ProgramNode(stmts):
                result = None
                for s in stmts:
                    result = self.run(s)
                return result
            case AssignNode(name, value):
                self.env[name] = self.run(value)
            case PrintNode(expr):
                print(f"  >> {self.run(expr)}")
            case IfNode(cond, then_b, else_b):
                branch = then_b if self.run(cond) else else_b
                for s in branch:
                    self.run(s)
            case WhileNode(cond, body):
                while self.run(cond):
                    for s in body:
                        self.run(s)
            case BinOpNode(op, left, right):
                l, r = self.run(left), self.run(right)
                return {'+': l+r, '-': l-r, '*': l*r, '/': l/r,
                        '==': l==r, '!=': l!=r,
                        '<':  l<r,  '>':  l>r,
                        '<=': l<=r, '>=': l>=r}[op]
            case UnaryOpNode('-', operand):
                return -self.run(operand)
            case NumberNode(v):
                return v
            case StringNode(v):
                return v
            case IdentNode(name):
                if name not in self.env:
                    raise NameError(f"Undefined variable: {name!r}")
                return self.env[name]

def run_tests():
    sep = "=" * 58
    passed = failed = 0

    def check(label, condition):
        nonlocal passed, failed
        mark = "PASS" if condition else "FAIL"
        print(f"  [{mark}]  {label}")
        passed += condition
        failed += not condition

    print(f"\n--- UNIT TESTS ---")

    def lex(src):
        return Lexer(src).tokenize()

    def parse(src):
        return Parser(lex(src)).parse()

    def interp(src):
        i = Interpreter()
        i.run(parse(src))
        return i.env

    # Test 1: number literal tokenises correctly
    tokens = lex("42;")
    check("Number token recognised", tokens[0].type == TokenType.NUMBER)

    # Test 2: keyword tokenises correctly
    tokens = lex("if while print")
    types = [t.type for t in tokens[:3]]
    check("Keywords recognised (if, while, print)",
          types == [TokenType.IF, TokenType.WHILE, TokenType.PRINT])

    # Test 3: arithmetic expression parses to BinOpNode
    ast = parse("x = 2 + 3;")
    check("Assignment node produced", isinstance(ast.statements[0], AssignNode))
    check("BinOp inside assignment", isinstance(ast.statements[0].value, BinOpNode))

    # Test 4: operator precedence (* before +)
    env = interp("x = 2 + 3 * 4;")
    check("Operator precedence: 2 + 3 * 4 == 14", env["x"] == 14.0)

    # Test 5: parentheses override precedence
    env = interp("x = (2 + 3) * 4;")
    check("Parentheses: (2 + 3) * 4 == 20", env["x"] == 20.0)

    # Test 6: variable assignment and use
    env = interp("a = 5; b = a + 1;")
    check("Variable use: a=5, b=a+1 => b==6", env["b"] == 6.0)

    # Test 7: if/else
    env = interp("x = 10; if x > 5 { x = 1; } else { x = 0; }")
    check("If/else: x=10 > 5 => x=1", env["x"] == 1.0)

    # Test 8: while loop
    env = interp("i = 0; while i < 3 { i = i + 1; }")
    check("While: counts i from 0 to 3", env["i"] == 3.0)

    # Test 9: unary minus
    env = interp("x = -7;")
    check("Unary minus: x = -7", env["x"] == -7.0)

    # Test 10: string literal
    env = interp('msg = "hello";')
    check('String literal: msg = "hello"', env["msg"] == "hello")

    print(f"\n  Results: {passed} passed, {failed} failed")
    print(sep)
    return failed == 0

SAMPLE = """
// Compute factorial of 5
n = 5;
result = 1;
i = 1;
while i <= n {
    result = result * i;
    i = i + 1;
}
print result;

// Simple if/else
x = 42;
if x == 42 {
    print "the answer";
} else {
    print "not the answer";
}
"""

if __name__ == "__main__":
    print("--- TOKENS ---")
    tokens = Lexer(SAMPLE).tokenize()
    for tok in tokens[:-1]:
        print(f"  {tok}")

    print("\n--- AST ---")
    ast = Parser(tokens).parse()
    print_ast(ast)

    print("\n--- OUTPUT ---")
    Interpreter().run(ast)

    run_tests()
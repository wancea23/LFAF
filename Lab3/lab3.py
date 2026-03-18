from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional

class TokenType(Enum):
    KEYWORD = auto()
    IDENTIFIER = auto()
    TICKER = auto()
    NUMBER = auto()
    STRING = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    COLON = auto()
    DOT = auto()
    ASSIGN = auto()
    OPERATOR = auto()
    PERIOD = auto()
    FORMAT = auto()
    FILTER = auto()
    WHERE = auto()
    WITH = auto()
    FOR = auto()
    USING = auto()
    AS = auto()
    EOF = auto()
    UNKNOWN = auto()

@dataclass
class Token:
    type: TokenType
    lexeme: str
    value: Optional[str]
    line: int
    column: int

class FinanceLexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        self.keywords = {
            'analyze': TokenType.KEYWORD,
            'calculate': TokenType.KEYWORD,
            'show': TokenType.KEYWORD,
            'define': TokenType.KEYWORD,
            'if': TokenType.KEYWORD,
            'else': TokenType.KEYWORD,
            'while': TokenType.KEYWORD,
            'for': TokenType.KEYWORD,
            'return': TokenType.KEYWORD,
            'stock': TokenType.KEYWORD,
            'option': TokenType.KEYWORD,
            'future': TokenType.KEYWORD,
            'bond': TokenType.KEYWORD,
            'dcf': TokenType.KEYWORD,
            'black_scholes': TokenType.KEYWORD,
            'sharpe_ratio': TokenType.KEYWORD,
            'var': TokenType.KEYWORD,
            'moving_average': TokenType.KEYWORD,
            'fetch': TokenType.KEYWORD,
            'when': TokenType.KEYWORD,
            'otherwise': TokenType.KEYWORD,
            'signal': TokenType.KEYWORD,
            'port': TokenType.KEYWORD,
        }
        self.periods = {
            '1d': TokenType.PERIOD,
            '1w': TokenType.PERIOD,
            '1m': TokenType.PERIOD,
            '3m': TokenType.PERIOD,
            '6m': TokenType.PERIOD,
            '1y': TokenType.PERIOD,
            'ytd': TokenType.PERIOD,
            '5y': TokenType.PERIOD,
        }
        self.formats = {
            'chart': TokenType.FORMAT,
            'table': TokenType.FORMAT,
            'json': TokenType.FORMAT,
            'csv': TokenType.FORMAT,
        }

    def current_char(self) -> Optional[str]:
        if self.pos < len(self.source):
            return self.source[self.pos]
        return None

    def peek_char(self, offset=1) -> Optional[str]:
        pos = self.pos + offset
        if pos < len(self.source):
            return self.source[pos]
        return None

    def advance(self):
        if self.pos < len(self.source):
            if self.source[self.pos] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.pos += 1

    def skip_whitespace(self):
        while self.current_char() and self.current_char().isspace():
            self.advance()

    def read_number(self) -> Token:
        start_line = self.line
        start_column = self.column
        num_str = ''

        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            num_str += self.current_char()
            self.advance()

        return Token(TokenType.NUMBER, num_str, num_str, start_line, start_column)

    def read_identifier(self) -> Token:
        start_line = self.line
        start_column = self.column
        ident_str = ''

        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            ident_str += self.current_char()
            self.advance()

        if ident_str in self.keywords:
            return Token(self.keywords[ident_str], ident_str, ident_str, start_line, start_column)
        elif ident_str in self.periods:
            return Token(TokenType.PERIOD, ident_str, ident_str, start_line, start_column)
        elif ident_str in self.formats:
            return Token(TokenType.FORMAT, ident_str, ident_str, start_line, start_column)
        elif ident_str == 'for':
            return Token(TokenType.FOR, ident_str, ident_str, start_line, start_column)
        elif ident_str == 'where':
            return Token(TokenType.WHERE, ident_str, ident_str, start_line, start_column)
        elif ident_str == 'with':
            return Token(TokenType.WITH, ident_str, ident_str, start_line, start_column)
        elif ident_str == 'using':
            return Token(TokenType.USING, ident_str, ident_str, start_line, start_column)
        elif ident_str == 'as':
            return Token(TokenType.AS, ident_str, ident_str, start_line, start_column)
        elif ident_str == 'filter':
            return Token(TokenType.FILTER, ident_str, ident_str, start_line, start_column)
        elif ident_str.isupper() and len(ident_str) <= 5:
            return Token(TokenType.TICKER, ident_str, ident_str, start_line, start_column)
        else:
            return Token(TokenType.IDENTIFIER, ident_str, ident_str, start_line, start_column)

    def read_string(self, quote_char) -> Token:
        start_line = self.line
        start_column = self.column
        string_str = ''
        self.advance()

        while self.current_char() and self.current_char() != quote_char:
            string_str += self.current_char()
            self.advance()

        if self.current_char() == quote_char:
            self.advance()

        return Token(TokenType.STRING, f'{quote_char}{string_str}{quote_char}', string_str, start_line, start_column)

    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            self.skip_whitespace()

            if self.current_char() is None:
                break

            char = self.current_char()
            line = self.line
            col = self.column

            if char.isdigit():
                self.tokens.append(self.read_number())
            elif char.isalpha() or char == '_':
                self.tokens.append(self.read_identifier())
            elif char == '"' or char == "'":
                self.tokens.append(self.read_string(char))
            elif char == '(':
                self.tokens.append(Token(TokenType.LPAREN, '(', '(', line, col))
                self.advance()
            elif char == ')':
                self.tokens.append(Token(TokenType.RPAREN, ')', ')', line, col))
                self.advance()
            elif char == '{':
                self.tokens.append(Token(TokenType.LBRACE, '{', '{', line, col))
                self.advance()
            elif char == '}':
                self.tokens.append(Token(TokenType.RBRACE, '}', '}', line, col))
                self.advance()
            elif char == '[':
                self.tokens.append(Token(TokenType.LBRACKET, '[', '[', line, col))
                self.advance()
            elif char == ']':
                self.tokens.append(Token(TokenType.RBRACKET, ']', ']', line, col))
                self.advance()
            elif char == ',':
                self.tokens.append(Token(TokenType.COMMA, ',', ',', line, col))
                self.advance()
            elif char == ':':
                self.tokens.append(Token(TokenType.COLON, ':', ':', line, col))
                self.advance()
            elif char == '.':
                self.tokens.append(Token(TokenType.DOT, '.', '.', line, col))
                self.advance()
            elif char == '=':
                self.tokens.append(Token(TokenType.ASSIGN, '=', '=', line, col))
                self.advance()
            elif char in '><!=':
                op_str = char
                self.advance()
                if self.current_char() in '=':
                    op_str += self.current_char()
                    self.advance()
                self.tokens.append(Token(TokenType.OPERATOR, op_str, op_str, line, col))
            elif char in '+-*/%':
                self.tokens.append(Token(TokenType.OPERATOR, char, char, line, col))
                self.advance()
            else:
                self.tokens.append(Token(TokenType.UNKNOWN, char, char, line, col))
                self.advance()

        self.tokens.append(Token(TokenType.EOF, '', None, self.line, self.column))
        return self.tokens

    def print_tokens(self):
        for token in self.tokens:
            print(f"Line {token.line}:{token.column} | Type: {token.type.name:15} | Lexeme: '{token.lexeme:20}' | Value: {token.value}")


class FinanceLexerAnalyzer:
    def __init__(self, lexer: FinanceLexer):
        self.lexer = lexer
        self.tokens = lexer.tokens

    def get_financial_terms(self):
        tickers = [t.lexeme for t in self.tokens if t.type == TokenType.TICKER]
        keywords = [t.lexeme for t in self.tokens if t.type == TokenType.KEYWORD]
        periods = [t.lexeme for t in self.tokens if t.type == TokenType.PERIOD]
        formats = [t.lexeme for t in self.tokens if t.type == TokenType.FORMAT]
        return {'tickers': tickers, 'keywords': keywords, 'periods': periods, 'formats': formats}

    def print_analysis(self):
        financial_terms = self.get_financial_terms()
        
        print("\nFINANCIAL TERMS EXTRACTED:")
        print(f"Tickers: {financial_terms['tickers']}")
        print(f"Keywords: {financial_terms['keywords']}")
        print(f"Time Periods: {financial_terms['periods']}")
        print(f"Output Formats: {financial_terms['formats']}")
        
        token_counts = {}
        for token in self.tokens:
            if token.type != TokenType.EOF:
                token_type = token.type.name
                token_counts[token_type] = token_counts.get(token_type, 0) + 1
        
        print("\nTOKEN DISTRIBUTION:")
        for token_type, count in sorted(token_counts.items()):
            print(f"{token_type:15}: {count}")


if __name__ == "__main__":
    test_cases = [
        "analyze stock AAPL for 6 months with moving_average filter price > 150.0",
        "calculate black_scholes for TSLA rate: 0.05 vol: 0.2 strike: 155.0",
        "show prices for AAPL where volume > 1000000 as chart",
        "define signal earnings_sentiment { source: fetch(nlp, ticker='MSFT') }",
        "when (signal > 0.2 && macro > 0.4) { signal: LONG }",
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\n{'-'*80}")
        print(f"TEST CASE {i}:")
        print(f"{'-'*80}")
        print(f"Input: {test}\n")
        print("TOKENS:")

        lexer = FinanceLexer(test)
        lexer.tokenize()
        lexer.print_tokens()

        analyzer = FinanceLexerAnalyzer(lexer)
        analyzer.print_analysis()
from enum import Enum
import sys

class  TokenType(Enum):
    EOF         = -1
    NEWLINE     = 0
    NUMBER      = 1
    IDENTIFIER  = 2
    STRING      = 3
    # Keywords.
    LABEL    = 101
    GOTO     = 102
    PRINT    = 103
    INPUT    = 104
    LET      = 105
    IF       = 106
    THEN     = 107
    ENDIF    = 108
    WHILE    = 109
    REPEAT   = 110
    ENDWHILE = 111
    # Operators.
    EQ       = 201  
    PLUS     = 202
    MINUS    = 203
    ASTERISK = 204
    SLASH    = 205
    EQEQ     = 206
    NOTEQ    = 207
    LT       = 208
    LTEQ     = 209
    GT       = 210
    GTEQ     = 211

# Token contains the original text and the type of token.
class Token:   
    def __init__(self, text: str, kind: TokenType):
        self.text = text
        self.kind = kind

class Lexer:
    def __init__(self, source: str):
        # Enforce newline as EOF character
        # Helps to know when the source code ends
        self.source = source + '\n'
        self.current_char = ''
        self.current_pos = -1
        self.nextChar()

    def nextChar(self, n = 1) -> str:
        self.current_pos += n
        if self.current_pos >= len(self.source):
            self.current_char = '\0'  # EOF
        else:
            self.current_char = self.source[self.current_pos]

        return self.current_char

    def peek(self):
        if self.current_pos + 1 >= len(self.source):
            return '\0'
        return self.source[self.current_pos + 1]

    def abort(self, message: str):
        sys.exit("Lexing error. " + message)

    def skipWhitespace(self):
        while self.current_char == ' ' or    \
                self.current_char == '\t' or \
                self.current_char == '\r':
            self.nextChar()

    def skipComment(self):
        if self.current_char == '#':
            self.nextChar()
            while self.current_char != '\n':
                self.nextChar()

    def getToken(self) -> Token | None:
        self.skipWhitespace()
        self.skipComment()

        token: Token | None = None
        
        if self.current_char in MAYBE_DOUBLE_OPS:
            maybe_double_op = self.current_char + self.peek()
            if maybe_double_op in DOUBLE_CHAR_OPS:
                token = self.create_double_op_token(maybe_double_op)
            elif self.current_char in SINGLE_CHAR_OPS:
                token = self.create_single_op_token(self.current_char)
        elif self.current_char in SINGLE_CHAR_OPS:
            token = self.create_single_op_token(self.current_char)
        elif self.current_char == '\"':
            token = self.create_string_token()
        elif self.current_char.isdigit():
            token = self.create_number_token()
        elif self.current_char.isalpha():
            token = self.create_identifier_or_keyword_token()

        if token is None:
            self.abort("Unknown token: " + self.current_char)

        return token
    
    def create_single_op_token(self, op: str) -> Token:
        self.nextChar()
        return Token(op, SINGLE_CHAR_OPS[op])
    
    def create_double_op_token(self, op: str) -> Token:
        self.nextChar(2)
        return Token(op, DOUBLE_CHAR_OPS[op])

    def create_string_token(self) -> Token:
        ILLEGAL_STRING_CHARS = ['\r', '\t', '\\', '\%']
        
        text = ''

        # Get the text between dquotes
        while self.nextChar() != '\"':
            # Don't allow special characters in the string. No escape characters, newlines, tabs, or %.
            # We will be using C's printf on this string.
            if self.current_char in ILLEGAL_STRING_CHARS:
                self.abort("Illegal character in string.")
            elif self.current_char == '\n':
                self.abort("Failed to close string.")
            else:
                text += self.current_char

        self.nextChar() # Chop the closing dquote

        return Token(text, TokenType.STRING)

    def create_number_token(self):
        number_as_str = self.current_char
        
        next_char = self.nextChar()

        while next_char.isdigit():
            number_as_str += next_char
            next_char = self.nextChar()
        
        # Floating point reached
        if self.current_char == '.':
            if not self.peek().isdigit():
                self.abort("Floating point number has no decimal values.")

            # Get decimal values
            while self.current_char.isdigit():
                number_as_str += self.nextChar()

        return Token(number_as_str, TokenType.NUMBER)
    
    def create_identifier_or_keyword_token(self) -> Token:
        text = self.current_char
        next_char = self.nextChar()

        while next_char.isalnum() or next_char == '_':
            text += next_char

            if text in KEYWORDS.keys() and self.peek() == ' ':
                self.nextChar()
                return Token(text, KEYWORDS[text])
            
            next_char = self.nextChar()
            
        return Token(text, TokenType.IDENTIFIER)

SINGLE_CHAR_OPS = { '+':  TokenType.PLUS,
                    '-':  TokenType.MINUS,
                    '*':  TokenType.ASTERISK,
                    '/':  TokenType.SLASH,
                    "=": TokenType.EQ,
                    ">": TokenType.GT,
                    "<": TokenType.LT,
                    '\n': TokenType.NEWLINE,
                    '\0': TokenType.EOF, }

MAYBE_DOUBLE_OPS = ['=', '>', '<', '!']
DOUBLE_CHAR_OPS = { "==": TokenType.EQEQ,
                    ">=": TokenType.GTEQ,
                    "<=": TokenType.LTEQ,
                    "!=": TokenType.NOTEQ, }

KEYWORDS = { "LABEL": TokenType.LABEL,
             "GOTO": TokenType.GOTO,
             "PRINT": TokenType.PRINT,
             "INPUT": TokenType.INPUT,
             "LET": TokenType.LET,
             "IF": TokenType.IF,
             "THEN": TokenType.THEN,
             "ENDIF": TokenType.ENDIF,
             "WHILE": TokenType.WHILE,
             "REPEAT": TokenType.REPEAT,
             "ENDWHILE": TokenType.ENDWHILE, }
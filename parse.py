import sys
from lex import *

# Parser object keeps track of current token and checks if the code matches the grammar
class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer

        self.current_token: Token | None = None
        self.peek_token: Token | None = None
        # Call this twice to initialize current and peek token
        self.nextToken()
        self.nextToken()

    def currentTokenIsKind(self, kind: TokenType):
        return self.current_token.kind == kind

    def nextTokenIsKind(self, kind: TokenType):
        return self.peek_token.kind == kind

    # Try to match current token. If not, error. Advances the current token.
    def match(self, kind: TokenType):  
        if not self.currentTokenIsKind(kind):
            self.abort("Expected " + kind.name + ", got " + self.current_token.kind.name)
        self.nextToken()

    def nextToken(self):
        self.current_token = self.peek_token
        self.peek_token = self.lexer.getToken()

    def abort(self, message):
        sys.exit("Error. " + message)
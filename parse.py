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

    # Production rules.

    # program ::= {statement}
    def program(self):
        print("PROGRAM")

        while self.currentTokenIsKind(TokenType.NEWLINE):
            self.nextToken()

        # Parse all the statements in the program.
        while not self.currentTokenIsKind(TokenType.EOF):
            self.statement()

        print("Parsing complete.")

    # One of the following statements...
    def statement(self):
        # Check the first token to see what kind of statement this is.

        if self.currentTokenIsKind(TokenType.PRINT):
            # statement ::= "PRINT" (expression | string) nl
            print("STATEMENT-PRINT")
            self.nextToken()

            if self.currentTokenIsKind(TokenType.STRING):
                # Simple string.
                self.nextToken()
            else:
                # Expect an expression.
                self.expression()
        elif self.currentTokenIsKind(TokenType.IF):
            # "IF" comparison "THEN" nl {statement} "ENDIF" nl
            print("STATEMENT-IF")
            self.nextToken()

            # Handle the comparison
            self.comparison()
            # Require THEN token afterwards
            self.matchCurrentTokenKind(TokenType.THEN)
            # Require NEWLINE token afterwards
            self.nl()
            self.processStatementsUntil(TokenType.ENDIF)
            # Require ENDIF token afterwards
            self.matchCurrentTokenKind(TokenType.ENDIF)
        elif self.currentTokenIsKind(TokenType.WHILE):
            # "WHILE" comparison "REPEAT" nl {statement nl} "ENDWHILE" nl
            print("STATEMENT-WHILE")
            self.nextToken()

            # Handle the comparison
            self.comparison()
            # Require REPEAT token afterwards
            self.matchCurrentTokenKind(TokenType.REPEAT)
            # Require NEWLINE token afterwards
            self.nl()
            self.processStatementsUntil(TokenType.ENDWHILE)
            # Require ENDWHILE token afterwards
            self.matchCurrentTokenKind(TokenType.ENDWHILE)
        elif self.currentTokenIsKind(TokenType.LABEL):
            # "LABEL" ident nl
            print("STATEMENT-LABEL")
            self.nextToken()

            # Require IDENTIFIER token afterwards
            self.matchCurrentTokenKind(TokenType.IDENTIFIER)
            # Handle the identifier
            self.identifier()
        elif self.currentTokenIsKind(TokenType.GOTO):
            # "GOTO" ident nl
            print("STATEMENT-GOTO")
            self.nextToken()

            # Require IDENTIFIER token afterwards
            self.matchCurrentTokenKind(TokenType.IDENTIFIER)
            # Handle the goto
            self.goto()
        elif self.currentTokenIsKind(TokenType.LET):
            # "LET" ident "=" expression nl
            print("STATEMENT-LET")
            self.nextToken()

            # Require IDENTIFIER token afterwards
            self.matchCurrentTokenKind(TokenType.IDENTIFIER)
            # Require EQ token afterwards
            self.matchCurrentTokenKind(TokenType.EQ)
            # Handle the expression
            self.expression()
        elif self.currentTokenIsKind(TokenType.INPUT):
            # "INPUT" ident nl
            print("STATEMENT-INPUT")
            self.nextToken()

            # Require INPUT token afterwards
            self.matchCurrentTokenKind(TokenType.INPUT)
            # Handle the input
            self.input()
        else:
            self.abort(f"Invalid statement at {self.current_token.text} ({self.current_token.kind.name})")

        # Require NEWLINE token after every statement
        self.nl()

    def expression(self):
        pass

    def comparison(self):
        pass

    def identifier(self):
        pass
    
    def input(self):
        pass

    def goto(self):
        pass

    # Zero or more statements in the body
    def processStatementsUntil(self, end_token: TokenType):
        while not self.currentTokenIsKind(end_token):
            if self.currentTokenIsKind(TokenType.EOF):
                self.abort("Opened If-statement without closing.")
            self.statement()

    def nl(self):
        print("NEWLINE")
        # Require at least one newline character
        self.matchCurrentTokenKind(TokenType.NEWLINE)

        # But allow as many as the user wants
        while self.currentTokenIsKind(TokenType.NEWLINE):
            self.nextToken()

    def currentTokenIsKind(self, kind: TokenType):
        return self.current_token.kind == kind

    def nextTokenIsKind(self, kind: TokenType):
        return self.peek_token.kind == kind

    # Try to match current token. If not, error. Advances the current token.
    def matchCurrentTokenKind(self, kind: TokenType):  
        if not self.currentTokenIsKind(kind):
            self.abort("Expected " + kind.name + ", got " + self.current_token.kind.name)
        self.nextToken()

    def nextToken(self):
        self.current_token = self.peek_token
        self.peek_token = self.lexer.getToken()

    def abort(self, message):
        sys.exit("Error. " + message)
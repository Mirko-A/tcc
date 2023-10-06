import sys
from lex import *

# Parser object keeps track of current token and checks if the code matches the grammar
class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer

        self.symbols = set()    # Variables declared so far.
        self.labels_declared = set() # Labels declared so far.
        self.labels_gotoed = set() # Labels goto'ed so far.

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

        for label in self.labels_gotoed:
            if label not in self.labels_declared:
                self.abort(f"Attempting to GOTO to an undeclared label: {label}")

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

            if self.current_token.text in self.labels_declared:
                self.abort(f"Label already exists: {self.current_token.text}")
            self.labels_declared.add(self.current_token.text)

            # Require IDENTIFIER token afterwards
            self.matchCurrentTokenKind(TokenType.IDENTIFIER)
            # Handle the identifier
            self.identifier()
        elif self.currentTokenIsKind(TokenType.GOTO):
            # "GOTO" ident nl
            print("STATEMENT-GOTO")
            self.nextToken()

            self.labels_gotoed.add(self.current_token.text)

            # Require IDENTIFIER token afterwards
            self.matchCurrentTokenKind(TokenType.IDENTIFIER)
            # Handle the goto
            self.goto()
        elif self.currentTokenIsKind(TokenType.LET):
            # "LET" ident "=" expression nl
            print("STATEMENT-LET")
            self.nextToken()

            # Check if identifier exists in symbol table.
            # If not, declare it.
            if self.current_token.text not in self.symbols:
                self.symbols.add(self.current_token.text)

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

            #If variable doesn't already exist, declare it.
            if self.current_token.text not in self.symbols:
                self.symbols.add(self.current_token.text)

            # Require IDENTIFIER token afterwards
            self.matchCurrentTokenKind(TokenType.IDENTIFIER)
            # Handle the input
            self.input()
        else:
            self.abort(f"Invalid statement at {self.current_token.text} ({self.current_token.kind.name})")

        # Require NEWLINE token after every statement
        self.nl()

    def comparison(self):
        # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
        print("COMPARISON")

        self.expression()
        # Must be at least one comparison operator and another expression.
        if self.isComparisonOperator():
            self.nextToken()
            self.expression()
        else:
            self.abort(f"Expected comparison operator at: {self.current_token.text}")

        # Can have 0 or more additional comparison operator and expressions.
        while self.isComparisonOperator():
            self.nextToken()
            self.expression()

    def isComparisonOperator(self) -> bool:
        if (self.currentTokenIsKind(TokenType.EQ)     or 
            self.currentTokenIsKind(TokenType.NOTEQ)  or 
            self.currentTokenIsKind(TokenType.GT)     or 
            self.currentTokenIsKind(TokenType.GTEQ)   or 
            self.currentTokenIsKind(TokenType.LT)     or 
            self.currentTokenIsKind(TokenType.LTEQ)):
            return True
        else:
            return False

    def expression(self):
        # expression ::= term {( "+" | "-" ) term}
        print("EXPRESSION")

        self.term()
        while self.currentTokenIsKind(TokenType.PLUS) or self.currentTokenIsKind(TokenType.MINUS):
            self.nextToken()
            self.term()

    def term(self):
        # term ::= unary {( "/" | "*" ) unary}
        print("TERM")

        self.unary()
        if self.currentTokenIsKind(TokenType.SLASH) or self.currentTokenIsKind(TokenType.ASTERISK):
            self.nextToken()
            self.unary()

    def unary(self):
        # unary ::= ["+" | "-"] primary
        print("UNARY")

        if self.currentTokenIsKind(TokenType.PLUS) or self.currentTokenIsKind(TokenType.MINUS):
            self.nextToken()
        self.primary()

    def primary(self):
        # primary ::= number | ident
        print(f"PRIMARY ({self.current_token.text})")

        if self.currentTokenIsKind(TokenType.NUMBER):
            self.nextToken()
        elif self.currentTokenIsKind(TokenType.IDENTIFIER):
            # Ensure the variable already exists.
            if self.current_token.text not in self.symbols:
                self.abort(f"Referencing variable before declaration: {self.current_token.text}")
            self.nextToken()
        else:
            self.abort(f"Expected NUMBER or IDENTIFIER token but got {self.current_token.kind.name}")

    def number(self):
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
from lex import *
from emit import *

from enum import Enum
import sys

class ExitCode(Enum):
    # OK
    OK = 0
    # Usage errors
    USAGE_ERROR_NOT_ENOUGH_ARGS = 1
    USAGE_TOO_MANY_ARGS = 2
    # Compile errors

    # Runtime errors
    RUNTIME_ERROR_INVALID_INPUT = 20

# Parser object keeps track of current token and checks if the code matches the grammar
class Parser:
    def __init__(self, lexer: Lexer, emitter: Emitter):
        self.lexer = lexer
        self.emitter = emitter

        self.code = "" # Output of the parser is kept here

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
        self.emitter.header_add_line("#include <stdio.h>")
        self.emitter.header_add_line("int main(void)")
        self.emitter.header_add_line("{")

        # Allow spaces at the start of the program
        while self.currentTokenIsKind(TokenType.NEWLINE):
            self.nextToken()

        # Parse all the statements in the program.
        while not self.currentTokenIsKind(TokenType.EOF):
            self.statement()

        for label in self.labels_gotoed:
            if label not in self.labels_declared:
                self.abort(f"Attempting to GOTO to an undeclared label: {label}")

        self.emitter.code_add_line(f"return {ExitCode.OK.value};")
        self.emitter.code_add_line("}")

    # One of the following statements...
    def statement(self):
        # Check the first token to see what kind of statement this is.

        if self.currentTokenIsKind(TokenType.PRINT):
            # statement ::= "PRINT" (expression | string) nl
            self.nextToken()

            if self.currentTokenIsKind(TokenType.STRING):
                # Simple string.
                self.emitter.code_add_line(f"printf(\"{self.current_token.text}\\n\");")
                self.nextToken()
            else:
                # Expect an expression.
                self.emitter.code_add(f"printf(\"%.2f\\n\", (float)(")
                self.expression()
                self.emitter.code_add_line("));")
        elif self.currentTokenIsKind(TokenType.IF):
            # "IF" comparison "THEN" nl {statement} "ENDIF" nl
            self.emitter.code_add("if(")
            self.nextToken()

            # Handle the comparison
            self.comparison()
            self.emitter.code_add_line(")")
            # Require THEN token afterwards
            self.matchCurrentTokenKind(TokenType.THEN)
            # Require NEWLINE token afterwards
            self.nl()
            self.emitter.code_add_line("{")
            self.processStatementsUntil(TokenType.ENDIF)
            # Require ENDIF token afterwards
            self.matchCurrentTokenKind(TokenType.ENDIF)
            self.emitter.code_add_line("}")
        elif self.currentTokenIsKind(TokenType.WHILE):
            # "WHILE" comparison "REPEAT" nl {statement nl} "ENDWHILE" nl
            self.emitter.code_add("while(")
            self.nextToken()

            # Handle the comparison
            self.comparison()
            self.emitter.code_add_line(")")
            # Require REPEAT token afterwards
            self.matchCurrentTokenKind(TokenType.REPEAT)
            # Require NEWLINE token afterwards
            self.nl()
            self.emitter.code_add_line("{")
            self.processStatementsUntil(TokenType.ENDWHILE)
            # Require ENDWHILE token afterwards
            self.matchCurrentTokenKind(TokenType.ENDWHILE)
            self.emitter.code_add_line("}")
        elif self.currentTokenIsKind(TokenType.LABEL):
            # "LABEL" ident nl
            self.nextToken()

            if self.current_token.text in self.labels_declared:
                self.abort(f"Label already exists: {self.current_token.text}")
            self.labels_declared.add(self.current_token.text)

            self.emitter.code_add_line(f"{self.current_token.text}:")

            # Require IDENTIFIER token afterwards
            self.matchCurrentTokenKind(TokenType.IDENTIFIER)
            # Handle the identifier
            self.identifier()
        elif self.currentTokenIsKind(TokenType.GOTO):
            # "GOTO" ident nl
            print("STATEMENT-GOTO")
            self.nextToken()

            self.labels_gotoed.add(self.current_token.text)

            self.emitter.code_add_line(f"goto {self.current_token.text};")

            # Require IDENTIFIER token afterwards
            self.matchCurrentTokenKind(TokenType.IDENTIFIER)
        elif self.currentTokenIsKind(TokenType.LET):
            # "LET" ident "=" expression nl
            self.nextToken()

            # Check if identifier exists in symbol table.
            # If not, declare it.
            if self.current_token.text not in self.symbols:
                self.emitter.header_add_line(f"float {self.current_token.text};")
                self.symbols.add(self.current_token.text)

            self.emitter.code_add(f"{self.current_token.text}")

            # Require IDENTIFIER token afterwards
            self.matchCurrentTokenKind(TokenType.IDENTIFIER)
            # Require EQ token afterwards
            self.emitter.code_add(" = ")
            self.matchCurrentTokenKind(TokenType.EQ)
            # Handle the expression
            self.expression()
            self.emitter.code_add_line(";")

        elif self.currentTokenIsKind(TokenType.INPUT):
            # "INPUT" ident nl
            self.nextToken()

            #If variable doesn't already exist, declare it.
            if self.current_token.text not in self.symbols:
                self.emitter.header_add_line(f"float {self.current_token.text};")
                self.symbols.add(self.current_token.text)

            self.emitter.code_add_line(f"if(scanf(\"%f\", &{self.current_token.text}) == 0)")
            self.emitter.code_add_line("{")
            self.emitter.code_add_line("printf(\"Runtime error. Only floating point numbers are accepted as input.\\n\");")
            self.emitter.code_add_line(f"return {ExitCode.RUNTIME_ERROR_INVALID_INPUT.value};")
            self.emitter.code_add_line("}")

            # Require IDENTIFIER token afterwards
            self.matchCurrentTokenKind(TokenType.IDENTIFIER)
        else:
            self.abort(f"Invalid statement at {self.current_token.text} ({self.current_token.kind.name})")

        # Require NEWLINE token after every statement
        self.nl()

    # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    def comparison(self):
        self.expression()
        # Must be at least one comparison operator and another expression.
        if self.isComparisonOperator():
            self.emitter.code_add(f" {self.current_token.text} ")
            self.nextToken()
            self.expression()
        else:
            self.abort(f"Expected comparison operator at: {self.current_token.text}")

        # Can have 0 or more additional comparison operator and expressions.
        while self.isComparisonOperator():
            self.emitter.code_add(f" {self.current_token.text} ")
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

    # expression ::= term {( "+" | "-" ) term}
    def expression(self):
        self.term()
        while self.currentTokenIsKind(TokenType.PLUS) or self.currentTokenIsKind(TokenType.MINUS):
            self.emitter.code_add(self.current_token.text)
            self.nextToken()
            self.term()

    # term ::= unary {( "/" | "*" ) unary}
    def term(self):
        self.unary()
        if self.currentTokenIsKind(TokenType.SLASH) or self.currentTokenIsKind(TokenType.ASTERISK):
            self.emitter.code_add(self.current_token.text)
            self.nextToken()
            self.unary()

    # unary ::= ["+" | "-"] primary
    def unary(self):
        if self.currentTokenIsKind(TokenType.PLUS) or self.currentTokenIsKind(TokenType.MINUS):
            self.emitter.code_add(self.current_token.text)
            self.nextToken()
        self.primary()

    # primary ::= number | ident
    def primary(self):
        if self.currentTokenIsKind(TokenType.NUMBER):
            self.emitter.code_add(self.current_token.text)
            self.nextToken()
        elif self.currentTokenIsKind(TokenType.IDENTIFIER):
            # Ensure the variable already exists.
            if self.current_token.text not in self.symbols:
                self.abort(f"Referencing variable before declaration: {self.current_token.text}")
            
            self.emitter.code_add(self.current_token.text)
            self.nextToken()
        else:
            self.abort(f"Expected NUMBER or IDENTIFIER token but got {self.current_token.kind.name}")

    # Zero or more statements in the body
    def processStatementsUntil(self, end_token: TokenType):
        while not self.currentTokenIsKind(end_token):
            if self.currentTokenIsKind(TokenType.EOF):
                self.abort("Opened If-statement without closing.")
            self.statement()

    def nl(self):
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
            self.abort(f"Expected {kind.name}, got {self.current_token.kind.name}")
        self.nextToken()

    def nextToken(self):
        self.current_token = self.peek_token
        self.peek_token = self.lexer.getToken()

    def abort(self, message: str):
        print("Error. " + message)
        sys.exit()
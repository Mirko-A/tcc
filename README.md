# Description
A compiler for a BASIC-like language written in Python

# Grammar
program ::= {statement}\n
statement ::= "PRINT" (expression | string) nl\n
    | "IF" comparison "THEN" nl {statement} "ENDIF" nl\n
    | "WHILE" comparison "REPEAT" nl {statement} "ENDWHILE" nl\n
    | "LABEL" ident nl\n
    | "GOTO" ident nl\n
    | "LET" ident "=" expression nl\n
    | "INPUT" ident nl\n
comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+\n
expression ::= term {( "-" | "+" ) term}\n
term ::= unary {( "/" | "*" ) unary}\n
unary ::= ["+" | "-"] primary\n
primary ::= number | ident\n
nl ::= '\n'+\n
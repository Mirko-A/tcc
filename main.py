from lex import *
from parse import *

def main():
    with open("test.tcc") as fd:
        source = fd.read()

    lexer = Lexer(source)
    parser = Parser(lexer)
    parser.program()

if __name__ == "__main__":
    main()


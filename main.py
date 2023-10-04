from lexer import *

def main():
    with open("test.tcc") as fd:
        source = fd.read()

    lexer = Lexer(source)
    token = lexer.getToken()
    while token.kind is not TokenType.EOF:
        print(f"{token.kind} : {token.text}")
        token = lexer.getToken()

if __name__ == "__main__":
    main()


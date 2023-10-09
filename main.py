from lex import *
from parse import *
from emit import *

import sys

def print_usage():
    print("""Usage: ./tcc input_file_path [output_file_path]""")

def main():
    arg_count = len(sys.argv)
    if arg_count < 2:
        print("Error: not enough arguments.")
        print_usage()
        exit(1)
    elif arg_count > 3:
        print("Error: too many arguments.")
        print_usage()
        exit(2)
    else:
        # arg_count is 2 or 3
        with open(sys.argv[1]) as in_file:
            source = in_file.read()
    
            lexer = Lexer(source)
            emitter = Emitter() if arg_count == 2 else Emitter(sys.argv[2])
            parser = Parser(lexer, emitter)

            parser.program()
            emitter.emit()

if __name__ == "__main__":
    main()


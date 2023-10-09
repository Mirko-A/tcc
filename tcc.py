from lex import *
from parse import *
from emit import *

import sys
import os
import subprocess
import time

def print_usage():
    print("""Usage: ./tcc input_file_path [output_file_path]""")

def compile(source: str, out_file_path: str):
    lexer = Lexer(source)
    emitter = Emitter(f"{out_file_path}.c")
    parser = Parser(lexer, emitter)

    parser.program()
    emitter.emit()

def main():
    arg_count = len(sys.argv)
    if arg_count < 2:
        print("Error: not enough arguments.")
        print_usage()
        sys.exit(ExitCode.USAGE_ERROR_NOT_ENOUGH_ARGS.value)
    elif arg_count > 3:
        print("Error: too many arguments.")
        print_usage()
        sys.exit(ExitCode.USAGE_TOO_MANY_ARGS.value)
    else:
        # arg_count is 2 or 3
        start = time.perf_counter()

        with open(sys.argv[1]) as in_file:
            source = in_file.read()
            out_file_path = sys.argv[2] if arg_count == 3 else "out"
    
            compile(source, out_file_path)
            os.makedirs("./bin")
            subprocess.run(["gcc", f"{out_file_path}.c", "-o", f"./bin/{out_file_path}"])
            os.remove(f"{out_file_path}.c")
            
            stop = time.perf_counter()
            print(f"Compilation done. Time needed: {stop - start:0.4f} ")

if __name__ == "__main__":
    main()


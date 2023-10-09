class Emitter:
    def __init__(self, out_file_path: str = "out.c"):
        self.out_file_path = out_file_path
        self.header = ""
        self.code = ""

    def code_add(self, code: str):
        code += code
        
    def code_add_line(self, code: str):
        self.code += code + '\n'

    def header_add_line(self, code):
        self.header += code + '\n'

    def emit(self):
        with open(self.out_file_path, 'w') as out_file:
            out_file.write(self.header + self.code)
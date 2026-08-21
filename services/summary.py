import ast
import os

PATH = "/home/hassan/Code/Hobby/DEPMAP/test"

class CodeSummary(ast.NodeVisitor):
    def __init__(self):
        self.imports = []
        self.classes = []
        self.functions = []
        self.calls = []
        
    def visit_Import(self, node):
        for  alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)
        
    def visit_ClassDef(self, node):
        self.classes.append(node.name)
        self.generic_visit(node)
        
    def visit_FunctionDef(self, node):
        self.functions.append(node.name)
        self.generic_visit(node)
        
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.calls.append(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.calls.append(node.func.attr)
        self.generic_visit(node)
        
def summarize(PATH):
    os.chdir(PATH)
    files = os.listdir(PATH)
    for file in files:
        with open(file, "r") as f:
            code = f.read()
            
        tree = ast.parse(code)
        s = CodeSummary()
        s.visit(tree)
        
        print("#"*10, f"File Name:{file}", "#"*10)
        print("-"*10, "Code Summary", "-"*10)
        print(f"IMPORTS: {s.imports}, TOTAL IMPORTS = {len(s.imports)}")
        print(f"CLASSES: {s.classes}, TOTAL CLASSES = {len(s.classes)}")
        print(f"FUNCTIONS: {s.functions}, TOTAL FUNCTIONS = {len(s.functions)}")
        print(f"CALLS: {s.calls}, TOTAL CALLS = {len(s.calls)}")
        print("-"*10, "Code Summary", "-"*10)
        print("")
        print("")
            
    

summarize(PATH=PATH)
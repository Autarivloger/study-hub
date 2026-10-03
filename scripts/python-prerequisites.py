"""Read-only AST analysis of lesson snippets. Used by the course migration checks."""
import ast
import json
import re
import sys


def analyze(code):
    features = set()
    calls = set()
    modules = set()
    try:
        tree = ast.parse(code)
    except SyntaxError:
        # Deliberately broken examples still need their syntax prerequisites.
        for pattern, feature in [(r"\bdef\s", "def"), (r"\bfor\s", "for"),
                                 (r"\bwhile\s", "while"), (r"\btry:", "try"),
                                 (r"\blambda\b", "lambda"), (r"\bclass\s", "class")]:
            if re.search(pattern, code):
                features.add(feature)
        return {"features": sorted(features), "calls": [], "modules": []}

    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node

    def ancestor(node, kind):
        node = parents.get(node)
        while node is not None:
            if isinstance(node, kind):
                return node
            node = parents.get(node)
        return None

    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            features.add("def")
            if n.args.args or n.args.posonlyargs or n.args.kwonlyargs:
                features.add("parameters")
            if n.args.defaults or n.args.kw_defaults:
                if n.args.defaults or any(n.args.kw_defaults):
                    features.add("defaults")
            if n.args.vararg or n.args.kwarg or n.args.kwonlyargs:
                features.add("args")
            if ast.get_docstring(n):
                features.add("docstring")
            if n.decorator_list:
                features.add("decorator")
        elif isinstance(n, ast.Return):
            features.add("return")
        elif isinstance(n, ast.Lambda):
            features.add("lambda")
        elif isinstance(n, (ast.Global, ast.Nonlocal)):
            features.add("scope")
        elif isinstance(n, ast.If):
            features.add("if")
            if n.orelse:
                features.add("else")
            parent_if = ancestor(n, ast.If)
            if parent_if and n not in parent_if.orelse:
                features.add("nested_if")
        elif isinstance(n, ast.IfExp):
            features.add("conditional_expression")
        elif isinstance(n, (ast.For, ast.AsyncFor)):
            features.add("for")
            if ancestor(n, (ast.For, ast.While)):
                features.add("nested_loop")
            if n.orelse:
                features.add("loop_else")
        elif isinstance(n, ast.While):
            features.add("while")
            if ancestor(n, (ast.For, ast.While)):
                features.add("nested_loop")
        elif isinstance(n, (ast.Break, ast.Continue)):
            features.add("break_continue")
        elif isinstance(n, ast.Match):
            features.add("match")
        elif isinstance(n, ast.NamedExpr):
            features.add("walrus")
        elif isinstance(n, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            features.add("generator" if isinstance(n, ast.GeneratorExp) else "comprehension")
            if len(n.generators) > 1 or ancestor(n, (ast.ListComp, ast.SetComp, ast.DictComp)):
                features.add("nested_comprehension")
        elif isinstance(n, ast.List):
            features.add("list_literal")
            if any(isinstance(x, ast.List) for x in n.elts):
                features.add("nested_list")
        elif isinstance(n, ast.Tuple):
            if isinstance(n.ctx, ast.Load):
                features.add("tuple")
        elif isinstance(n, (ast.Dict, ast.DictComp)):
            features.add("dict")
            if isinstance(n, ast.Dict) and any(isinstance(x, ast.Dict) for x in n.values):
                features.add("nested_dict")
        elif isinstance(n, (ast.Set, ast.SetComp)):
            features.add("set")
        elif isinstance(n, ast.Try):
            features.add("try")
        elif isinstance(n, ast.Raise):
            features.add("raise")
        elif isinstance(n, (ast.With, ast.AsyncWith)):
            features.add("with")
        elif isinstance(n, ast.Assert):
            features.add("assert")
        elif isinstance(n, ast.ClassDef):
            features.add("class")
            if n.bases:
                features.add("inheritance")
        elif isinstance(n, (ast.Yield, ast.YieldFrom)):
            features.add("generator")
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            if isinstance(n, ast.Import):
                modules.update(a.name.split('.')[0] for a in n.names)
            elif n.module:
                modules.add(n.module.split('.')[0])
            features.add("import")
        elif isinstance(n, ast.Call):
            name = ast.unparse(n.func)
            calls.add(name)
            if isinstance(n.func, ast.Name):
                f = ancestor(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                if f and f.name == n.func.id:
                    features.add("recursion")
            if any(k.arg == 'key' for k in n.keywords):
                features.add("key_function")
        elif isinstance(n, ast.Subscript):
            features.add("index")
    return {"features": sorted(features), "calls": sorted(calls), "modules": sorted(modules)}


if __name__ == '__main__':
    json.dump([analyze(c) for c in json.load(sys.stdin)], sys.stdout, ensure_ascii=False)

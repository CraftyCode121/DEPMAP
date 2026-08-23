import networkx as nx
import ast
import os

def parse_file(filepath):
    """Extract imports, classes (with methods), and top-level functions from one file."""
    with open(filepath, encoding="utf-8", errors="ignore") as f:
        source = f.read()
    tree = ast.parse(source, filename=filepath)

    imports = []
    functions = {}   
    classes = {}      

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append({"module": alias.name, "level": 0})
        elif isinstance(node, ast.ImportFrom):
            imports.append({
                "module": node.module,
                "level": node.level,
                "names": [a.name for a in node.names]
            })

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            functions[node.name] = _extract_calls(node)
        elif isinstance(node, ast.ClassDef):
            methods = {}
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    methods[item.name] = _extract_calls(item)
            bases = [b.id for b in node.bases if isinstance(b, ast.Name)]  # only simple names, not module.Class
            classes[node.name] = {"methods": methods, "bases": bases}

    return {"imports": imports, "functions": functions, "classes": classes}

def build_class_registry(parsed):
    """Map class_name -> {file, methods, bases}. Assumes unique class names across repo."""
    registry = {}
    for filepath, data in parsed.items():
        for cls_name, cls_info in data["classes"].items():
            registry[cls_name] = {"file": filepath, **cls_info}
    return registry

def resolve_self_call(called, cls_name, registry, visited=None):
    """Walk up the inheritance chain to find which class actually defines `called`."""
    if visited is None:
        visited = set()
    if cls_name in visited or cls_name not in registry:
        return None
    visited.add(cls_name)

    cls_info = registry[cls_name]
    if called in cls_info["methods"]:
        return f"{cls_info['file']}::{cls_name}.{called}"

    for base in cls_info["bases"]:
        result = resolve_self_call(called, base, registry, visited)
        if result:
            return result
    return None


def _extract_calls(func_node):
    plain_calls = []
    self_calls = []
    instance_calls = []   # (var_name, method_name)
    var_classes = {}       # var_name -> class_name, from "var = ClassName(...)"

    for n in ast.walk(func_node):
        if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name):
            if len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
                var_classes[n.targets[0].id] = n.value.func.id

        if isinstance(n, ast.Call):
            if isinstance(n.func, ast.Name):
                plain_calls.append(n.func.id)
            elif isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name):
                if n.func.value.id == "self":
                    self_calls.append(n.func.attr)
                else:
                    instance_calls.append((n.func.value.id, n.func.attr))

    return {"plain": plain_calls, "self": self_calls, "instance": instance_calls, "var_classes": var_classes}

def resolve_import(imp, importing_file, all_files, root):
    level = imp["level"]
    module = imp["module"]

    if level == 0:
        if not module:
            return None
        candidate = os.path.join(root, module.replace(".", os.sep))  # now absolute, like relative case
    else:
        base_dir = os.path.dirname(importing_file)
        for _ in range(level - 1):
            base_dir = os.path.dirname(base_dir)

        if module:
            candidate = os.path.join(base_dir, module.replace(".", os.sep))
        else:
            for name in imp.get("names", []):
                match = _match_candidate(os.path.join(base_dir, name), all_files, root)
                if match:
                    return match
            return None

    return _match_candidate(candidate, all_files, root)


def _match_candidate(candidate, all_files, root):
    candidate_rel = os.path.relpath(candidate, root)
    package_form = os.path.join(candidate_rel, "__init__")  
    for filepath in all_files:
        rel_path = os.path.relpath(filepath, root)
        rel_no_ext = os.path.splitext(rel_path)[0]
        if rel_no_ext == candidate_rel or rel_no_ext == package_form:
            return filepath
    return None

def get_import_bindings(data, filepath, all_files, root):
    """Map each imported name -> the file it actually comes from."""
    bindings = {}
    for imp in data["imports"]:
        resolved = resolve_import(imp, filepath, all_files, root)
        if resolved:
            for name in imp.get("names", []):
                bindings[name] = resolved
    return bindings

def resolve_call(called_name, filepath, data, bindings):
    """Return the fid of the function this call refers to, or None if external."""
    if called_name in data["functions"]:
        return f"{filepath}::{called_name}"
    if called_name in bindings:
        return f"{bindings[called_name]}::{called_name}"
    return None  # builtin, external lib, or unresolved (e.g. method call)

def walk_repo(root):
    """Run parse_file on every .py file, return {filepath: parsed_data}."""
    results = {}
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            if fname.endswith(".py"):
                path = os.path.join(dirpath, fname)
                try:
                    results[path] = parse_file(path)
                except Exception as e:
                    print(f"FAILED: {path} -> {type(e).__name__}: {e}")
                    continue
    return results
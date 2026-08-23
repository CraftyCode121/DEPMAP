from parser.python_parser import resolve_import, walk_repo, resolve_call, get_import_bindings, resolve_self_call, build_class_registry
import networkx as nx

def build_graphs(parsed, root):
    file_graph = nx.DiGraph()
    func_graph = nx.DiGraph()
    external_deps = {}
    all_files = list(parsed.keys())

    for filepath, data in parsed.items():
        file_graph.add_node(filepath)
        for imp in data["imports"]:
            resolved = resolve_import(imp, filepath, all_files, root)
            if resolved:
                file_graph.add_edge(filepath, resolved)
            elif imp["module"]:
                top_level = imp["module"].split(".")[0]
                external_deps.setdefault(top_level, set()).add(filepath)

        bindings = get_import_bindings(data, filepath, all_files, root)

        for fname, calls in data["functions"].items():
            fid = f"{filepath}::{fname}"
            func_graph.add_node(fid, file=filepath)
            for called in calls["plain"]:
                target = resolve_call(called, filepath, data, bindings)
                if target:
                    func_graph.add_edge(fid, target)

        # class methods
        registry = build_class_registry(parsed)  

        for cls_name, cls_info in data["classes"].items():
            for mname, calls in cls_info["methods"].items():
                fid = f"{filepath}::{cls_name}.{mname}"
                func_graph.add_node(fid, file=filepath, cls=cls_name)

                for called in calls["plain"]:
                    target = resolve_call(called, filepath, data, bindings)
                    if target:
                        func_graph.add_edge(fid, target)

                for called in calls["self"]:
                    target = resolve_self_call(called, cls_name, registry)
                    if target:
                        func_graph.add_edge(fid, target)
                        
                for var_name, method in calls["instance"]:
                    cls_guess = calls["var_classes"].get(var_name)
                    if cls_guess and cls_guess in registry:
                        target = resolve_self_call(method, cls_guess, registry)
                        if target:
                            func_graph.add_edge(fid, target)

    return file_graph, func_graph, external_deps

root = "/home/hassan/Code/Hobby/DEPMAP/testing_repoes/easyprep"
parsed = walk_repo(root)
file_graph, func_graph, external_deps = build_graphs(parsed, root)

print(file_graph.number_of_edges(), "internal file dependencies")
print(len(external_deps), "external packages")
for pkg, files in external_deps.items():
    print(f"  {pkg}: used in {len(files)} file(s)")

print(func_graph.number_of_nodes(), "functions")
print(func_graph.number_of_edges(), "resolved calls")
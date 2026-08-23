import networkx as nx

def impacted_files(file_graph, changed_file):
    """Everything that depends on changed_file, directly or transitively."""
    if changed_file not in file_graph:
        return set()
    return nx.ancestors(file_graph, changed_file)

def impacted_functions(func_graph, changed_fid):
    """Everything that calls changed_fid, directly or transitively."""
    if changed_fid not in func_graph:
        return set()
    return nx.ancestors(func_graph, changed_fid)

def impact_report(func_graph, changed_fid):
    if changed_fid not in func_graph:
        return {"direct": set(), "transitive": set()}

    direct = set(func_graph.predecessors(changed_fid))
    all_impacted = nx.ancestors(func_graph, changed_fid)
    transitive = all_impacted - direct

    return {"direct": direct, "transitive": transitive}

from summarizer.file_summary import summarize_repo
from parser.python_parser import walk_repo

root = "/home/hassan/Code/Hobby/DEPMAP/testing_repoes/easyprep/"
parsed = walk_repo(root)
summaries = summarize_repo(parsed)

print(summaries["/home/hassan/Code/Hobby/DEPMAP/testing_repoes/easyprep/easyprep/core.py"])
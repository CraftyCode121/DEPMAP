from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import networkx as nx

from graph.builder import walk_repo, build_graphs
from graph.queries import impact_report
from summarizer.file_summary import summarize_file

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for local dev, tighten later
    allow_methods=["*"],
    allow_headers=["*"],
)

# in-memory cache: one repo analyzed at a time for now
state = {
    "file_graph": None,
    "func_graph": None,
    "external_deps": None,
    "parsed": None,
}


@app.post("/analyze")
def analyze(repo_path: str):
    parsed = walk_repo(repo_path)
    file_graph, func_graph, external_deps = build_graphs(parsed, repo_path)

    state["file_graph"] = file_graph
    state["func_graph"] = func_graph
    state["external_deps"] = external_deps
    state["parsed"] = parsed

    return {
        "files": file_graph.number_of_nodes(),
        "file_edges": file_graph.number_of_edges(),
        "functions": func_graph.number_of_nodes(),
        "function_edges": func_graph.number_of_edges(),
    }


@app.get("/graph/files")
def get_file_graph():
    if state["file_graph"] is None:
        raise HTTPException(400, "No repo analyzed yet — call /analyze first")
    return nx.node_link_data(state["file_graph"])


@app.get("/graph/functions")
def get_func_graph():
    if state["func_graph"] is None:
        raise HTTPException(400, "No repo analyzed yet — call /analyze first")
    return nx.node_link_data(state["func_graph"])


@app.get("/external-deps")
def get_external_deps():
    if state["external_deps"] is None:
        raise HTTPException(400, "No repo analyzed yet — call /analyze first")
    return {pkg: list(files) for pkg, files in state["external_deps"].items()}


@app.get("/impact/{graph_type}")
def get_impact(graph_type: str, node_id: str):
    graph = state["file_graph"] if graph_type == "files" else state["func_graph"]
    if graph is None:
        raise HTTPException(400, "No repo analyzed yet — call /analyze first")
    if node_id not in graph:
        raise HTTPException(404, f"Node not found: {node_id}")

    report = impact_report(graph, node_id)
    return {
        "direct": list(report["direct"]),
        "transitive": list(report["transitive"]),
    }


@app.get("/summary/{file_path:path}")
def get_summary(file_path: str):
    if state["parsed"] is None:
        raise HTTPException(400, "No repo analyzed yet")

    full_path = "/" + file_path  # path param strips the leading slash, add it back
    if full_path not in state["parsed"]:
        raise HTTPException(404, "File not found")

    return {"summary": summarize_file(full_path, state["parsed"][full_path])}
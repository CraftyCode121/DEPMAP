<p align="center">
  <img src="logo.png" width="180">
</p>

<p align="center">
  Analyze Python repositories and visualize their dependency structure.
</p>

<p align="center">

  <img src="https://img.shields.io/badge/Python-3.10%2B-blue">

  <img src="https://img.shields.io/github/license/CraftyCode121/DEPMAP">

  <img src="https://img.shields.io/github/stars/CraftyCode121/DEPMAP">

  <img src="https://img.shields.io/github/issues/CraftyCode121/DEPMAP">

  <img src="https://img.shields.io/github/last-commit/CraftyCode121/DEPMAP">

</p>

---

DEPMAP analyzes a Python repository and builds a dependency graph out of it — which files import which, which functions call which — so you can see the structure of a codebase and answer "what breaks if I change this file?" before you find out the hard way.

It parses your repo with Python's `ast` module, builds file-level and function-level dependency graphs with `networkx`, and serves them through a small FastAPI backend to an interactive graph you explore in the browser.

## Features

- **File dependency graph** — resolves absolute imports, relative imports (`from . import x`), and package imports (`from . import mypackage`)
- **Function-level call graph** — resolves plain function calls, `self.method()` calls (including through inheritance), and simple same-function instance calls (`var.method()` where `var` was constructed locally)
- **Impact analysis** — click any file to see everything that directly or transitively depends on it
- **External dependency tracking** — see every third-party package the repo uses and how many files import it
- **File summaries** — imports (tagged as external / relative / internal), classes with their methods, and top-level functions

## Requirements

- Python 3.10+
- A modern browser

## Quick start

- **Linux/macOS:** `./run.sh`
- **Windows:** double-click `run.bat` (or run it from cmd)

Either one creates the virtual environment if it doesn't exist yet, installs dependencies, starts the API, and opens the frontend in your browser automatically. Type a repo path into the input field and click **Analyze**.

## Manual setup

If you'd rather run things yourself instead of using the scripts above:

```bash
git clone https://github.com/CraftyCode121/DEPMAP
cd DEPMAP
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running it

Covered by the Quick Start scripts above. If you're doing it manually instead:

**1. Start the API:**

```bash
uvicorn api.main:app --reload
```

This runs on `http://localhost:8000`.

**2. Open the frontend:**

Open `frontend/index.html` directly in your browser (double-click it, or use its `file://` path). No build step needed.

**3. Analyze a repo:**

Type the full local path to any Python repository into the input field at the top and click **Analyze**. The graph will render, and clicking any node shows its impact and summary.

> The frontend talks to the API at `http://localhost:8000` by default. If you run the API on a different host or port, update the `API` constant near the top of the `<script>` block in `frontend/index.html`.

## Project structure

```
DEPMAP/
├── parser/
│   └── python_parser.py     # AST-based extraction: imports, classes, functions, calls
├── graph/
│   ├── builder.py            # Builds file graph + function graph, resolves imports/calls
│   └── queries.py            # Impact analysis (direct/transitive dependents)
├── summarizer/
│   └── file_summary.py       # Human-readable per-file summaries
├── api/
│   └── main.py                # FastAPI endpoints
├── frontend/
│   └── index.html             # Graph UI (Cytoscape.js, no build step)
└── requirements.txt
```

## Known limitations

- Python only — no support for other languages yet
- Cross-file method resolution assumes unique class names across the repo
- Instance-call resolution (`var.method()`) only catches variables constructed directly in the same function — not ones passed in as parameters or reassigned conditionally
- One repo is analyzed at a time (in-memory cache, resets on server restart)

## License

MIT

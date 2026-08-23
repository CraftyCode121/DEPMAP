import ast

def summarize_function(name, node_data):
    calls = node_data.get("plain", []) + node_data.get("self", [])
    call_note = f", calls {len(set(calls))} other function(s)" if calls else ""
    return f"`{name}`{call_note}"


def summarize_class(cls_name, cls_info):
    methods = list(cls_info["methods"].keys())
    bases = cls_info["bases"]
    base_note = f" (inherits from {', '.join(bases)})" if bases else ""
    return f"Class `{cls_name}`{base_note} with {len(methods)} method(s): {', '.join(methods)}"


def _format_import(imp):
    """Render one import as a display string, preserving relative-import dots
    so the frontend can tell relative apart from absolute/external at a glance."""
    level = imp.get("level", 0)
    module = imp.get("module")

    if level > 0:
        dots = "." * level
        if module:
            return f"{dots}{module}"
        # "from . import x, y" — module is None, list each imported name
        names = imp.get("names", [])
        return ", ".join(f"{dots}{n}" for n in names) if names else dots

    return module  # absolute import; None only if malformed, filtered by caller


def summarize_file(filepath, data):
    lines = [f"File: {filepath}"]

    import_display = []
    for imp in data["imports"]:
        formatted = _format_import(imp)
        if formatted:
            import_display.append(formatted)

    if import_display:
        lines.append(f"  Imports: {', '.join(import_display)}")

    if data["classes"]:
        lines.append(f"  Defines {len(data['classes'])} class(es):")
        for cls_name, cls_info in data["classes"].items():
            lines.append(f"    - {summarize_class(cls_name, cls_info)}")

    if data["functions"]:
        lines.append(f"  Defines {len(data['functions'])} top-level function(s):")
        for fname, fcalls in data["functions"].items():
            lines.append(f"    - {summarize_function(fname, fcalls)}")

    return "\n".join(lines)


def summarize_repo(parsed):
    return {filepath: summarize_file(filepath, data) for filepath, data in parsed.items()}
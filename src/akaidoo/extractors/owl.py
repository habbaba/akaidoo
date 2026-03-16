"""OWL widget and component extractor."""
import re
from pathlib import Path
from typing import Dict, Any

FIELD_WIDGET_RE = re.compile(
    r'registry\s*\.\s*category\s*\(\s*["\']fields["\']\s*\)\s*\.\s*add\s*\(\s*["\'](\w+)["\']',
)
VIEW_WIDGET_RE = re.compile(
    r'registry\s*\.\s*category\s*\(\s*["\']view_widgets["\']\s*\)\s*\.\s*add\s*\(\s*["\'](\w+)["\']',
)
SERVICE_RE = re.compile(
    r'registry\s*\.\s*category\s*\(\s*["\']services["\']\s*\)\s*\.\s*add\s*\(\s*["\'](\w+)["\']',
)

def extract_owl_registry(module_path: Path) -> Dict[str, Any]:
    """Extract OWL field widgets, view widgets, and services."""
    widgets = {}
    view_widgets = {}
    services = {}

    static_src = module_path / "static" / "src"
    if not static_src.is_dir():
        return {"field_widgets": {}, "view_widgets": {}, "services": {}}

    for js_file in static_src.rglob("*.js"):
        try:
            content = js_file.read_text(errors='ignore')
        except Exception:
            continue

        rel_path = str(js_file.relative_to(module_path))

        for match in FIELD_WIDGET_RE.finditer(content):
            name = match.group(1)
            if name not in widgets:
                widgets[name] = {"file": rel_path}

        for match in VIEW_WIDGET_RE.finditer(content):
            name = match.group(1)
            if name not in view_widgets:
                view_widgets[name] = {"file": rel_path}

        for match in SERVICE_RE.finditer(content):
            name = match.group(1)
            if name not in services:
                services[name] = {"file": rel_path}

    return {
        "field_widgets": widgets,
        "view_widgets": view_widgets,
        "services": services,
    }

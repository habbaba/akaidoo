"""HTTP Routes extractor."""
import re
from pathlib import Path
from typing import List, Dict, Any

ROUTE_DECORATOR_RE = re.compile(
    r'@(?:http\.)?route\s*\((.*?)\)',
    re.DOTALL,
)
METHOD_DEF_RE = re.compile(
    r'def\s+(\w+)\s*\(self(?:,\s*(.*?))?\)\s*:',
)
CONTROLLER_CLASS_RE = re.compile(
    r'class\s+(\w+)\s*\(\s*(?:http\.)?Controller\s*\)',
)
ROUTE_PATH_RE = re.compile(r'["\'](/[^"\']+)["\']')
AUTH_RE = re.compile(r'auth\s*=\s*["\'](\w+)["\']')
TYPE_RE = re.compile(r'type\s*=\s*["\'](\w+)["\']')
METHODS_RE = re.compile(r'methods\s*=\s*\[(.*?)\]')

def extract_http_routes(module_path: Path) -> Dict[str, Any]:
    """Extract all HTTP routes from controller files."""
    routes = []
    controllers = {}

    controllers_dir = module_path / "controllers"
    if not controllers_dir.is_dir():
        return {"routes": [], "controllers": {}}

    for py_file in controllers_dir.rglob("*.py"):
        try:
            content = py_file.read_text(errors='ignore')
        except Exception:
            continue

        if '@route' not in content and '@http.route' not in content:
            continue

        rel_path = str(py_file.relative_to(module_path))

        for match in CONTROLLER_CLASS_RE.finditer(content):
            ctrl_name = match.group(1)
            controllers[ctrl_name] = {"file": rel_path}

        lines = content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            route_match = ROUTE_DECORATOR_RE.search(line)
            
            if not route_match:
                if '@route' in line or '@http.route' in line:
                    full_line = line
                    j = i + 1
                    while j < len(lines) and ')' not in full_line:
                        full_line += ' ' + lines[j].strip()
                        j += 1
                    route_match = ROUTE_DECORATOR_RE.search(full_line)
                    if route_match:
                        for k in range(i + 1, min(j + 3, len(lines))):
                            method_match = METHOD_DEF_RE.search(lines[k])
                            if method_match:
                                r = _parse_route(route_match.group(1), method_match.group(1), rel_path)
                                if r: routes.append(r)
                                break
                i += 1
                continue

            for k in range(i + 1, min(i + 5, len(lines))):
                method_match = METHOD_DEF_RE.search(lines[k])
                if method_match:
                    r = _parse_route(route_match.group(1), method_match.group(1), rel_path)
                    if r: routes.append(r)
                    break
            i += 1

    return {"routes": routes, "controllers": controllers}

def _parse_route(decorator_args: str, method_name: str, file_path: str) -> Dict[str, Any]:
    route = {"method": method_name, "file": file_path}
    paths = ROUTE_PATH_RE.findall(decorator_args)
    if paths:
        route["path"] = paths[0]
        if len(paths) > 1:
            route["paths"] = paths

    auth = AUTH_RE.search(decorator_args)
    route["auth"] = auth.group(1) if auth else "user"

    rtype = TYPE_RE.search(decorator_args)
    route["type"] = rtype.group(1) if rtype else "http"

    methods = METHODS_RE.search(decorator_args)
    if methods:
        route["methods"] = re.findall(r'["\'](\w+)["\']', methods.group(1))

    return route if "path" in route else {}

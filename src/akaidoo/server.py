"""
Akaidoo MCP Server

Provides MCP (Model Context Protocol) tools for AI agents to query Odoo codebases.
Uses AkaidooService for all operations.
"""

from typing import List, Optional
from pathlib import Path
from mcp.server.fastmcp import FastMCP

from .service import get_service
from .config import TOKEN_FACTOR

# Create an MCP server
mcp = FastMCP("Akaidoo")

# Get the service instance
_service = get_service()


@mcp.tool()
def read_module_source(
    addon: str,
    shrink_mode: str = "soft",
    expand_models: Optional[List[str]] = None,
    add_expand_models: Optional[List[str]] = None,
    context_budget_tokens: Optional[int] = None,
) -> str:
    """
    Retrieves Odoo addon source code with intelligent context optimization.

    QUICK START: Just provide the `addon` name - akaidoo handles the rest with smart defaults.

    OPTIONS:
    - `shrink_mode`: Controls code compression (default: "soft")
      - "none": Full code, no shrinking
      - "soft": Shrink dependencies only (recommended for most tasks)
      - "medium": More aggressive shrinking
      - "hard": Very aggressive shrinking
      - "max": Maximum compression, structure only

    - `expand_models`: EXPLICIT mode - ONLY expand these models (disables auto-expand)
      Use for debugging specific models, e.g., ["account.move"] for a traceback

    - `add_expand_models`: ADDITIVE mode - Add models to the auto-expand set
      Use when you need more detail on related models, e.g., ["stock.picking"]

    - `context_budget_tokens`: Target context size (e.g., 100000)
      Akaidoo auto-escalates shrink modes to fit within budget

    STRATEGY GUIDE:
    1. **General exploration**: Just provide addon name with defaults
    2. **Debugging traceback**: Use expand_models=["the.failing.model"]
    3. **Need more context on a model**: Use add_expand_models=["related.model"]
    4. **Context too large**: Use context_budget_tokens or increase shrink_mode
    """
    # Convert token budget to character budget
    budget_chars = None
    if context_budget_tokens is not None:
        budget_chars = int(context_budget_tokens / TOKEN_FACTOR)

    import os
    cfg_path = Path(os.environ.get("ODOO_RC")) if "ODOO_RC" in os.environ else None
    context = _service.resolve_context(
        addon,
        shrink_mode=shrink_mode,
        expand_models_str=",".join(expand_models) if expand_models else None,
        add_expand_str=",".join(add_expand_models) if add_expand_models else None,
        context_budget=budget_chars,
        odoo_cfg=cfg_path,
    )
    introduction = f"MCP Dump for {addon}"
    return _service.get_context_dump(context, introduction)


import os

@mcp.tool()
def get_context_map(addon: str) -> str:
    # ... docstring omitted ...
    cfg_path = Path(os.environ.get("ODOO_RC")) if "ODOO_RC" in os.environ else None
    context = _service.resolve_context(addon, odoo_cfg=cfg_path)
    return _service.get_tree_string(context, use_ansi=False)

@mcp.tool()
def get_context_summary(addon: str) -> dict:
    # ... docstring omitted ...
    cfg_path = Path(os.environ.get("ODOO_RC")) if "ODOO_RC" in os.environ else None
    context = _service.resolve_context(addon, odoo_cfg=cfg_path)
    return _service.get_context_summary(context)

@mcp.tool()
def ping() -> str:
    """Check if the Akaidoo MCP server is running."""
    return "pong"

import json

from .extractors.owl import extract_owl_registry
from .extractors.routes import extract_http_routes
from .extractors.relations import extract_model_relations
from .extractors.reports import extract_reports

@mcp.tool()
def get_owl_registry(addon: str) -> str:
    # ... docstring omitted ...
    cfg_path = Path(os.environ.get("ODOO_RC")) if "ODOO_RC" in os.environ else None
    context = _service.resolve_context(addon, odoo_cfg=cfg_path)
    if not context.selected_addon_names:
        return json.dumps({"error": f"Addon {addon} not found"})
    addon_name = list(context.selected_addon_names)[0]
    addon_files = context.addon_files_map.get(addon_name, [])
    if not addon_files:
        return json.dumps({"error": f"No files found for {addon_name}"})
    addon_path = Path(addon_files[0]).parent.parent if addon_files[0].suffix == ".py" else Path(addon_files[0]).parent
    while addon_path.name != addon_name and len(addon_path.parts) > 1:
        addon_path = addon_path.parent
    result = extract_owl_registry(addon_path)
    return json.dumps(result, indent=2)

@mcp.tool()
def get_http_routes(addon: str) -> str:
    # ... docstring omitted ...
    cfg_path = Path(os.environ.get("ODOO_RC")) if "ODOO_RC" in os.environ else None
    context = _service.resolve_context(addon, odoo_cfg=cfg_path)
    if not context.selected_addon_names:
        return json.dumps({"error": f"Addon {addon} not found"})
    addon_name = list(context.selected_addon_names)[0]
    addon_files = context.addon_files_map.get(addon_name, [])
    if not addon_files:
        return json.dumps({"error": f"No files found for {addon_name}"})
    addon_path = Path(addon_files[0]).parent.parent if addon_files[0].suffix == ".py" else Path(addon_files[0]).parent
    while addon_path.name != addon_name and len(addon_path.parts) > 1:
        addon_path = addon_path.parent
    result = extract_http_routes(addon_path)
    return json.dumps(result, indent=2)

@mcp.tool()
def get_model_relations(addon: str) -> str:
    # ... docstring omitted ...
    cfg_path = Path(os.environ.get("ODOO_RC")) if "ODOO_RC" in os.environ else None
    context = _service.resolve_context(addon, odoo_cfg=cfg_path)
    if not context.selected_addon_names:
        return json.dumps({"error": f"Addon {addon} not found"})
    addon_name = list(context.selected_addon_names)[0]
    addon_files = context.addon_files_map.get(addon_name, [])
    if not addon_files:
        return json.dumps({"error": f"No files found for {addon_name}"})
    addon_path = Path(addon_files[0]).parent.parent if addon_files[0].suffix == ".py" else Path(addon_files[0]).parent
    while addon_path.name != addon_name and len(addon_path.parts) > 1:
        addon_path = addon_path.parent
    result = extract_model_relations(addon_path)
    return json.dumps(result, indent=2)

@mcp.tool()
def get_reports(addon: str) -> str:
    # ... docstring omitted ...
    cfg_path = Path(os.environ.get("ODOO_RC")) if "ODOO_RC" in os.environ else None
    context = _service.resolve_context(addon, odoo_cfg=cfg_path)
    if not context.selected_addon_names:
        return json.dumps({"error": f"Addon {addon} not found"})
    addon_name = list(context.selected_addon_names)[0]
    addon_files = context.addon_files_map.get(addon_name, [])
    if not addon_files:
        return json.dumps({"error": f"No files found for {addon_name}"})
    addon_path = Path(addon_files[0]).parent.parent if addon_files[0].suffix == ".py" else Path(addon_files[0]).parent
    while addon_path.name != addon_name and len(addon_path.parts) > 1:
        addon_path = addon_path.parent
    result = extract_reports(addon_path)
    return json.dumps(result, indent=2)


@mcp.resource("akaidoo://context/summary")
def get_summary() -> str:
    """
    Get the current Akaidoo session summary.

    Reads `.akaidoo/context/session.md` which is created by running:
    `akaidoo <addon> --session`

    This provides a mission briefing for the current development session.
    """
    summary_path = Path(".akaidoo/context/session.md")
    if summary_path.exists():
        return summary_path.read_text()
    else:
        return "# Akaidoo Session\n\nNo active session. Run `akaidoo <addon> --session` to start one."

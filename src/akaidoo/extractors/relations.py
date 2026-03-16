"""Model relations extractor using tree-sitter."""
from pathlib import Path
from typing import Dict, Any, List
from ..utils import parser

def extract_model_relations(module_path: Path) -> Dict[str, Any]:
    """Extract model relations from Python files."""
    relations = {}

    models_dir = module_path / "models"
    if not models_dir.is_dir():
        # Models can also be in the root directory
        files = list(module_path.glob("*.py"))
    else:
        files = list(models_dir.rglob("*.py"))

    for py_file in files:
        if py_file.name == "__init__.py" or py_file.name == "__manifest__.py":
            continue

        try:
            content = py_file.read_text(encoding="utf-8")
        except Exception:
            continue

        code_bytes = bytes(content, "utf8")
        try:
            tree = parser.parse(code_bytes)
        except Exception:
            continue

        root_node = tree.root_node
        for node in root_node.children:
            if node.type == "class_definition":
                body_node = node.child_by_field_name("body")
                if not body_node:
                    continue

                # Find model name
                model_names = []
                for child in body_node.children:
                    if child.type == "expression_statement":
                        expr = child.child(0)
                        if expr and expr.type == "assignment":
                            left = expr.child_by_field_name("left")
                            if left and left.type == "identifier":
                                attr_name = code_bytes[left.start_byte : left.end_byte].decode("utf-8")
                                if attr_name in ("_name", "_inherit"):
                                    right = expr.child_by_field_name("right")
                                    if right:
                                        if right.type == "string":
                                            mname = code_bytes[right.start_byte : right.end_byte].decode("utf-8").strip("'\"")
                                            model_names.append(mname)
                                        elif right.type in ("list", "tuple"):
                                            for rchild in right.children:
                                                if rchild.type == "string":
                                                    mname = code_bytes[rchild.start_byte : rchild.end_byte].decode("utf-8").strip("'\"")
                                                    model_names.append(mname)
                
                if not model_names:
                    continue

                for m in model_names:
                    if m not in relations:
                        relations[m] = {"type": "model" if "_name" in content else "inherit", "relations": {}}

                # Extract relations
                for child in body_node.children:
                    if child.type == "expression_statement":
                        expr = child.child(0)
                        if expr and expr.type == "assignment":
                            left = expr.child_by_field_name("left")
                            right = expr.child_by_field_name("right")
                            
                            if not left or left.type != "identifier" or not right or right.type != "call":
                                continue
                            
                            fn = right.child_by_field_name("function")
                            if not fn or fn.type != "attribute":
                                continue
                            
                            attr = fn.child_by_field_name("attribute")
                            if not attr or attr.type != "identifier":
                                continue
                            
                            field_type = code_bytes[attr.start_byte : attr.end_byte].decode("utf-8")
                            
                            if field_type in ("Many2one", "One2many", "Many2many"):
                                field_name = code_bytes[left.start_byte : left.end_byte].decode("utf-8")
                                args = right.child_by_field_name("arguments")
                                
                                comodel = None
                                if args:
                                    for arg in args.children:
                                        if arg.type == "string":
                                            comodel = code_bytes[arg.start_byte : arg.end_byte].decode("utf-8").strip("'\"")
                                            break
                                        elif arg.type == "keyword_argument":
                                            kname = arg.child_by_field_name("name")
                                            kval = arg.child_by_field_name("value")
                                            if kname and kval and kval.type == "string":
                                                k = code_bytes[kname.start_byte : kname.end_byte].decode("utf-8")
                                                if k == "comodel_name":
                                                    comodel = code_bytes[kval.start_byte : kval.end_byte].decode("utf-8").strip("'\"")
                                                    break
                                
                                if comodel:
                                    for m in model_names:
                                        relations[m]["relations"][field_name] = {"type": field_type, "comodel": comodel}

    return relations

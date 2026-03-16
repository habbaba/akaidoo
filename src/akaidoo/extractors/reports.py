"""XML Reports extractor."""
import re
from pathlib import Path
from typing import Dict, Any, List

REPORT_ACTION_RE = re.compile(r'<record[^>]*model=["\']ir\.actions\.report["\'][^>]*>(.*?)</record>', re.DOTALL)
REPORT_FIELD_RE = re.compile(r'<field\s+name=["\'](.*?)["\'][^>]*>(.*?)</field>', re.DOTALL)

def extract_reports(module_path: Path) -> List[Dict[str, str]]:
    """Extract QWeb report definitions from XML files."""
    reports = []

    # Look in the standard places: `report` or `views` dirs
    search_dirs = [module_path / "report", module_path / "reports", module_path / "views"]
    
    xml_files = []
    for d in search_dirs:
        if d.is_dir():
            xml_files.extend(list(d.rglob("*.xml")))

    for xml_file in xml_files:
        try:
            content = xml_file.read_text(errors='ignore')
        except Exception:
            continue
            
        rel_path = str(xml_file.relative_to(module_path))

        for match in REPORT_ACTION_RE.finditer(content):
            record_block = match.group(1)
            report_data = {"file": rel_path}
            
            for field_match in REPORT_FIELD_RE.finditer(record_block):
                field_name = field_match.group(1)
                field_val = field_match.group(2).strip()
                
                # if the tag is empty but uses `eval` or `ref`
                if not field_val:
                    eval_match = re.search(r'eval=["\'](.*?)["\']', field_match.group(0))
                    ref_match = re.search(r'ref=["\'](.*?)["\']', field_match.group(0))
                    if eval_match:
                        field_val = eval_match.group(1)
                    elif ref_match:
                        field_val = ref_match.group(1)
                
                if field_name in ("name", "model", "report_type", "report_name", "print_report_name"):
                    report_data[field_name] = field_val
            
            if "name" in report_data or "report_name" in report_data:
                reports.append(report_data)

    return reports

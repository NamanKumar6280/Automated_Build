#!/usr/bin/env python3
"""
Parse Unity log file for compiler errors/warnings.
If log file doesn't exist, output empty JSON.
"""

import sys
import re
import json
import os

def parse_log(log_path):
    if not os.path.isfile(log_path):
        return {"errors": [], "warnings": []}

    errors = []
    warnings = []
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    error_pattern = re.compile(r'(.+)\((\d+),(\d+)\): error ([A-Z0-9]+): (.+)')
    warning_pattern = re.compile(r'(.+)\((\d+),(\d+)\): warning ([A-Z0-9]+): (.+)')
    for line in lines:
        m = error_pattern.search(line)
        if m:
            errors.append({
                "file": m.group(1).strip(),
                "line": int(m.group(2)),
                "column": int(m.group(3)),
                "code": m.group(4),
                "message": m.group(5).strip()
            })
            continue
        m = warning_pattern.search(line)
        if m:
            warnings.append({
                "file": m.group(1).strip(),
                "line": int(m.group(2)),
                "column": int(m.group(3)),
                "code": m.group(4),
                "message": m.group(5).strip()
            })

    return {"errors": errors, "warnings": warnings}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: parse_unity_log.py <logfile> <output.json>")
        sys.exit(1)
    log_file = sys.argv[1]
    out_file = sys.argv[2]
    data = parse_log(log_file)
    with open(out_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Parsed {len(data['errors'])} errors and {len(data['warnings'])} warnings.")

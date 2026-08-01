#!/usr/bin/env python3
"""
Generate AI report in Markdown and JSON.
"""

import sys
import json
import argparse
import datetime
import os

def generate_from_compile_errors(errors_file, output_md, output_json):
    with open(errors_file, 'r') as f:
        compile_data = json.load(f)

    errors = compile_data.get("errors", [])
    warnings = compile_data.get("warnings", [])

    missing_classes = []
    missing_namespaces = []
    suggestions = []
    for e in errors:
        msg = e.get("message", "")
        code = e.get("code", "")
        if "CS0246" in code and "type or namespace" in msg:
            parts = msg.split("'")
            if len(parts) >= 2:
                missing_classes.append(parts[1])
        if "CS0234" in code:
            parts = msg.split("'")
            if len(parts) >= 2:
                missing_namespaces.append(parts[1])
        if "InputValue" in msg:
            suggestions.append("Install com.unity.inputsystem package and add using UnityEngine.InputSystem;")
        if "TextMeshPro" in msg:
            suggestions.append("Ensure com.unity.textmeshpro is installed and import TMP Essentials.")
        if "NavMesh" in msg:
            suggestions.append("Install com.unity.ai.navigation package.")

    report = {
        "compilation": "FAILED" if errors else "SUCCESS",
        "total_errors": len(errors),
        "total_warnings": len(warnings),
        "missing_classes": list(set(missing_classes)),
        "missing_namespaces": list(set(missing_namespaces)),
        "suggested_fixes": list(set(suggestions)),
        "raw_errors": errors[:10]
    }

    with open(output_json, 'w') as f:
        json.dump(report, f, indent=2)

    md = f"""# AI Build Report (Compile Failure)

**Status**: {report['compilation']}
**Errors**: {report['total_errors']}
**Warnings**: {report['total_warnings']}

## Missing Classes
{chr(10).join(['- ' + c for c in report['missing_classes']]) if report['missing_classes'] else 'None'}

## Missing Namespaces
{chr(10).join(['- ' + n for n in report['missing_namespaces']]) if report['missing_namespaces'] else 'None'}

## Suggested Fixes
{chr(10).join(['- ' + s for s in report['suggested_fixes']]) if report['suggested_fixes'] else 'No suggestions.'}

## Sample Errors (first 10)
{chr(10).join(['- ' + e['message'] for e in report['raw_errors']])}
"""
    with open(output_md, 'w') as f:
        f.write(md)

def generate_success_report(apk_size, build_time, output_md):
    # If apk_size is not a number, default to 0
    try:
        apk_size = int(apk_size)
    except:
        apk_size = 0

    # build_time might be empty
    if not build_time:
        build_time = "unknown"

    md = f"""# AI Build Report (Success)

**Build Status**: SUCCESS
**APK Size**: {apk_size} bytes
**Build Time**: {build_time} seconds
**Generated At**: {datetime.datetime.utcnow().isoformat()}

All steps completed successfully. The APK is ready for download.
"""
    with open(output_md, 'w') as f:
        f.write(md)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--compile-errors", help="JSON file from parse_unity_log")
    parser.add_argument("--success", action="store_true", help="Indicate success build")
    parser.add_argument("--apk-size", help="APK size in bytes")
    parser.add_argument("--build-time", help="Build time in seconds")
    parser.add_argument("--output", required=True, help="Output Markdown file")
    parser.add_argument("--json", action="store_true", help="Also output JSON")

    args = parser.parse_args()

    if args.compile_errors:
        json_out = args.output.replace(".md", ".json") if args.json else None
        generate_from_compile_errors(args.compile_errors, args.output, json_out)
    elif args.success:
        generate_success_report(args.apk_size or "0", args.build_time or "unknown", args.output)
    else:
        print("No valid mode specified.")
        sys.exit(1)

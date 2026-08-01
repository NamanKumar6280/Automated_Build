#!/usr/bin/env python3
"""
Validate a Unity project structure before Unity runs.
Checks for critical folders, packages, scripts, and configuration.
"""

import os
import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(os.getcwd())

# Required relative paths (relative to project root)
REQUIRED = {
    "folders": [
        "Assets",
        "Assets/_Project/Scripts",
        "Assets/_Project/Scripts/Data",
        "Assets/_Project/Scripts/Systems",
        "Assets/_Project/Scripts/Gameplay",
        "Assets/_Project/Scripts/UI",
        "Assets/_Project/Scripts/Tests",
        "Assets/Editor",
        "Assets/Editor/ProjectSetup",
        "Packages",
        "ProjectSettings",
    ],
    "files": [
        "ProjectSettings/ProjectVersion.txt",
        "Packages/manifest.json",
        "Assets/_Project/Scripts/_Project.asmdef",
        "Assets/Editor/ProjectSetup/SetupRunner.cs",
        "Assets/Editor/BuildScript.cs",
    ],
    "packages": [
        "com.unity.render-pipelines.universal",
        "com.unity.inputsystem",
        "com.unity.textmeshpro",
        "com.unity.ai.navigation",
        "com.unity.ugui",
    ]
}

def check():
    errors = []
    warnings = []

    # Check folders
    for folder in REQUIRED["folders"]:
        p = PROJECT_ROOT / folder
        if not p.is_dir():
            errors.append(f"Missing folder: {folder}")

    # Check files
    for file in REQUIRED["files"]:
        p = PROJECT_ROOT / file
        if not p.is_file():
            errors.append(f"Missing file: {file}")

    # Check packages in manifest.json
    manifest_path = PROJECT_ROOT / "Packages" / "manifest.json"
    if manifest_path.is_file():
        import json
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        deps = manifest.get("dependencies", {})
        for pkg in REQUIRED["packages"]:
            if pkg not in deps:
                warnings.append(f"Package not in manifest: {pkg}")
    else:
        errors.append("manifest.json missing")

    # Prepare report
    report = {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
        "passed_checks": len([f for f in REQUIRED["files"] if (PROJECT_ROOT / f).is_file()]) + len([f for f in REQUIRED["folders"] if (PROJECT_ROOT / f).is_dir()])
    }

    # Write to file for later use
    with open("validation_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("=== Validation Report ===")
    print(f"Status: {report['status']}")
    if errors:
        for e in errors:
            print(f"❌ {e}")
    if warnings:
        for w in warnings:
            print(f"⚠️ {w}")
    if not errors and not warnings:
        print("✅ All checks passed.")

    return len(errors) == 0

if __name__ == "__main__":
    sys.exit(0 if check() else 1)

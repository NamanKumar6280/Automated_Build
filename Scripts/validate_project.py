#!/usr/bin/env python3
"""
Validate Unity project structure. Supports --generated flag to check generated assets.
"""

import os
import sys
import json
import argparse
from pathlib import Path

PROJECT_ROOT = Path(os.getcwd())

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

def check_generated_assets():
    """Check that generation produced the expected assets."""
    errors = []
    warnings = []

    # Count scenes
    scenes = list((PROJECT_ROOT / "Assets" / "_Project" / "Scenes").glob("*.unity")) if (PROJECT_ROOT / "Assets" / "_Project" / "Scenes").exists() else []
    if len(scenes) < 2:
        errors.append("Expected at least 2 scenes (MainMenu and Shop). Found: {}".format(len(scenes)))

    # Check prefabs
    prefabs = list((PROJECT_ROOT / "Assets" / "_Project" / "Prefabs").glob("*.prefab")) if (PROJECT_ROOT / "Assets" / "_Project" / "Prefabs").exists() else []
    expected_prefabs = {"Player", "Shelf_Packaged", "ProductBox", "CheckoutCounter", "Customer", "DeliveryPallet"}
    found_prefabs = {p.stem for p in prefabs}
    missing = expected_prefabs - found_prefabs
    if missing:
        errors.append(f"Missing prefabs: {missing}")

    # Check ScriptableObjects
    so_path = PROJECT_ROOT / "Assets" / "_Project" / "Data" / "Products"
    if not so_path.exists() or not list(so_path.glob("*.asset")):
        warnings.append("No ProductData assets found. They may be created at runtime.")

    report = {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
        "scene_count": len(scenes),
        "prefab_count": len(prefabs),
    }
    with open("generated_assets_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print
    print("=== Generated Assets Validation ===")
    print(f"Status: {report['status']}")
    print(f"Scenes: {report['scene_count']}")
    print(f"Prefabs: {report['prefab_count']}")
    if errors:
        for e in errors:
            print(f"❌ {e}")
    if warnings:
        for w in warnings:
            print(f"⚠️ {w}")

    return len(errors) == 0

def check_initial():
    errors = []
    warnings = []

    for folder in REQUIRED["folders"]:
        p = PROJECT_ROOT / folder
        if not p.is_dir():
            errors.append(f"Missing folder: {folder}")

    for file in REQUIRED["files"]:
        p = PROJECT_ROOT / file
        if not p.is_file():
            errors.append(f"Missing file: {file}")

    manifest_path = PROJECT_ROOT / "Packages" / "manifest.json"
    if manifest_path.is_file():
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        deps = manifest.get("dependencies", {})
        for pkg in REQUIRED["packages"]:
            if pkg not in deps:
                warnings.append(f"Package not in manifest: {pkg}")
    else:
        errors.append("manifest.json missing")

    report = {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
        "passed_checks": len([f for f in REQUIRED["files"] if (PROJECT_ROOT / f).is_file()]) + len([f for f in REQUIRED["folders"] if (PROJECT_ROOT / f).is_dir()])
    }

    with open("validation_report.json", "w") as f:
        json.dump(report, f, indent=2)

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", action="store_true", help="Check generated assets")
    args = parser.parse_args()

    if args.generated:
        success = check_generated_assets()
    else:
        success = check_initial()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

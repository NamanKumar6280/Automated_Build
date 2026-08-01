#!/usr/bin/env python3
"""
Validate Unity project – auto‑detects project root.
"""

import os
import sys
import json
import argparse
from pathlib import Path

def find_unity_project_root(start_path=None):
    """Search for a folder containing both 'Assets' and 'Packages'."""
    if start_path is None:
        start_path = Path.cwd()
    for root, dirs, files in os.walk(start_path):
        if "Assets" in dirs and "Packages" in dirs:
            return Path(root)
    # Fallback: current directory
    return Path.cwd()

def check_initial(project_root):
    errors = []
    warnings = []

    required_folders = [
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
    ]
    required_files = [
        "ProjectSettings/ProjectVersion.txt",
        "Packages/manifest.json",
        "Assets/_Project/Scripts/_Project.asmdef",
        "Assets/Editor/ProjectSetup/SetupRunner.cs",
        "Assets/Editor/BuildScript.cs",
    ]
    required_packages = [
        "com.unity.render-pipelines.universal",
        "com.unity.inputsystem",
        "com.unity.textmeshpro",
        "com.unity.ai.navigation",
        "com.unity.ugui",
    ]

    for folder in required_folders:
        p = project_root / folder
        if not p.is_dir():
            errors.append(f"Missing folder: {folder}")

    for file in required_files:
        p = project_root / file
        if not p.is_file():
            errors.append(f"Missing file: {file}")

    manifest_path = project_root / "Packages" / "manifest.json"
    if manifest_path.is_file():
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        deps = manifest.get("dependencies", {})
        for pkg in required_packages:
            if pkg not in deps:
                warnings.append(f"Package not in manifest: {pkg}")
    else:
        errors.append("manifest.json missing")

    report = {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
        "project_root": str(project_root),
    }

    with open("validation_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Also write project root to a file for other steps
    with open("project_root.txt", "w") as f:
        f.write(str(project_root))

    print("=== Validation Report ===")
    print(f"Project root: {project_root}")
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

def check_generated_assets(project_root):
    errors = []
    warnings = []

    scenes = list((project_root / "Assets" / "_Project" / "Scenes").glob("*.unity")) if (project_root / "Assets" / "_Project" / "Scenes").exists() else []
    if len(scenes) < 2:
        errors.append(f"Expected at least 2 scenes (MainMenu, Shop). Found: {len(scenes)}")

    prefabs = list((project_root / "Assets" / "_Project" / "Prefabs").glob("*.prefab")) if (project_root / "Assets" / "_Project" / "Prefabs").exists() else []
    expected = {"Player", "Shelf_Packaged", "ProductBox", "CheckoutCounter", "Customer", "DeliveryPallet"}
    found = {p.stem for p in prefabs}
    missing = expected - found
    if missing:
        errors.append(f"Missing prefabs: {missing}")

    so_path = project_root / "Assets" / "_Project" / "Data" / "Products"
    if not so_path.exists() or not list(so_path.glob("*.asset")):
        warnings.append("No ProductData assets found.")

    report = {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
        "scene_count": len(scenes),
        "prefab_count": len(prefabs),
        "project_root": str(project_root),
    }
    with open("generated_assets_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("=== Generated Assets Validation ===")
    print(f"Project root: {project_root}")
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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", action="store_true", help="Check generated assets")
    args = parser.parse_args()

    # Auto‑detect project root
    project_root = find_unity_project_root()
    print(f"Detected Unity project root: {project_root}")

    if args.generated:
        success = check_generated_assets(project_root)
    else:
        success = check_initial(project_root)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

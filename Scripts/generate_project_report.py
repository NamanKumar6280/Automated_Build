#!/usr/bin/env python3
"""
Generate a report of generated assets: scenes, prefabs, ScriptableObjects, etc.
"""

import os
from pathlib import Path
import json
import datetime

PROJECT_ROOT = Path(os.getcwd())

def count_files(ext, folder="Assets"):
    """Count files with a given extension recursively under folder."""
    p = PROJECT_ROOT / folder
    if not p.is_dir():
        return 0
    return len(list(p.rglob(f"*{ext}")))

def main():
    report = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "generated_assets": {
            "unity_scenes": count_files(".unity"),
            "prefabs": count_files(".prefab"),
            "scriptable_objects": count_files(".asset", "Assets/_Project/Data"),
            "materials": count_files(".mat"),
            "animations": count_files(".anim"),
            "input_actions": count_files(".inputactions", "Assets/_Project/Input"),
            "navmesh_surfaces": count_files(".asset", "Assets/_Project/") # approximate
        },
        "missing_references": []  # Placeholder for future reference checks
    }

    # Write JSON report
    with open("project_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Create Markdown
    md = f"""# Project Generation Report
Generated on: {report['timestamp']}

## Generated Assets
- **Scenes**: {report['generated_assets']['unity_scenes']}
- **Prefabs**: {report['generated_assets']['prefabs']}
- **ScriptableObjects**: {report['generated_assets']['scriptable_objects']}
- **Materials**: {report['generated_assets']['materials']}
- **Animations**: {report['generated_assets']['animations']}
- **Input Actions**: {report['generated_assets']['input_actions']}
- **NavMesh Surfaces**: {report['generated_assets']['navmesh_surfaces']}

## Missing References
None detected (placeholder).
"""
    with open("project_report.md", "w") as f:
        f.write(md)

if __name__ == "__main__":
    main()

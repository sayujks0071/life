"""Compatibility wrapper. Canonical generator is spine_daily_update.py."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spine_daily_update import generate_report, parse_roadmap

if __name__ == "__main__":
    roadmap_path = "docs/spine_submission_roadmap.md"
    data, error = parse_roadmap(roadmap_path)

    if error:
        print(error)
        sys.exit(1)

    print(generate_report(data))

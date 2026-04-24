import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from planner.data.recruiters import RECRUITER_SEED

TARGET_DIR = ROOT / "src" / "data"
TARGET_DIR.mkdir(parents=True, exist_ok=True)
BACKEND_TARGET = ROOT / "backend" / "planner" / "data" / "benchmark_hires.json"
SOURCE = ROOT / "backend" / "planner" / "data" / "benchmark_hires.json"


def export_hires():
    hires = json.loads(SOURCE.read_text(encoding="utf-8"))

    target = TARGET_DIR / "benchmarkHires.json"
    target.write_text(json.dumps(hires, indent=2), encoding="utf-8")
    return len(hires)


def export_recruiters():
    target = TARGET_DIR / "recruiters.json"
    target.write_text(json.dumps(RECRUITER_SEED, indent=2), encoding="utf-8")
    return len(RECRUITER_SEED)


def main():
    hires_count = export_hires()
    recruiters_count = export_recruiters()
    print(f"Exported {hires_count} hires and {recruiters_count} recruiters.")


if __name__ == "__main__":
    main()

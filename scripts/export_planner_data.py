import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from planner.data.recruiters import RECRUITER_SEED
from planner.services.normalize import (
    infer_function,
    infer_seniority,
    normalize_location,
    normalize_role_title,
    normalize_stage,
    parse_cost_to_usd,
    stage_rank,
)


SOURCE = ROOT / "dover_cost_per_hire.csv"
TARGET_DIR = ROOT / "src" / "data"
TARGET_DIR.mkdir(parents=True, exist_ok=True)


def export_hires():
    hires = []
    with SOURCE.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for index, row in enumerate(reader, start=1):
            location = normalize_location(row["Company Location"])
            stage = normalize_stage(row["Company Stage"])
            hires.append(
                {
                    "sourceRowIndex": index,
                    "roleTitle": row["Position"],
                    "normalizedRoleTitle": normalize_role_title(row["Position"]),
                    "function": infer_function(row["Position"]),
                    "seniority": infer_seniority(row["Position"]),
                    "costPerHireUsd": parse_cost_to_usd(row["Cost Per Hire"]),
                    "costPerHireDisplay": row["Cost Per Hire"],
                    "companyStage": stage,
                    "stageRank": stage_rank(stage),
                    "companyLocation": row["Company Location"],
                    "normalizedCity": location["city"],
                    "normalizedRegion": location["region"],
                    "geoCluster": location["cluster"],
                    "notableInvestors": row["Notable Investor(s)"],
                    "recruiterName": row["Recruiter Name"],
                }
            )

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

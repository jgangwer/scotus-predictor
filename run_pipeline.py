#!/usr/bin/env python3
"""
run_pipeline.py — Pipeline Orchestrator

Runs the full SCOTUS prediction pipeline for one or all cases.
Includes cost estimation, skip logic, and status tracking.

Usage:
    python3 run_pipeline.py                           # process all pipeline_ready cases
    python3 run_pipeline.py data/cases/25-332         # process one case by path
    python3 run_pipeline.py 25-332                    # process one case by docket number
    python3 run_pipeline.py --estimate                # show cost estimate without running
    python3 run_pipeline.py --force                   # re-run even if already complete
    python3 run_pipeline.py --force data/cases/25-332 # force re-run one case
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
CASES_DIR = os.path.join(DATA_DIR, "cases")
STATUS_FILE = os.path.join(DATA_DIR, "docket_status.json")
PYTHON = os.path.join(SCRIPT_DIR, "venv", "bin", "python3")

# Pipeline steps in order.
# (script_name, description, output_file_to_check, takes_case_dir_arg)
# If output_file_to_check is None, the step always runs.
PIPELINE_STEPS = [
    ("fetch_opinions.py",        "Fetch cited opinions",    "_citation_index.json",           True),
    ("summarize_opinions.py",    "Summarize opinions",      None,                             False),
    ("issue_analysis.py",        "Issue analysis",          "issue_analysis_output.txt",      True),
    ("vote_prediction.py",       "Vote prediction",         "vote_predictions_combined.txt",  True),
    ("scenario_construction.py", "Scenario construction",   "scenario_output.txt",            True),
    ("export_to_website.py",     "Export to website",       None,                             True),
]

# Rough cost estimates per step (Claude API costs)
STEP_COSTS = {
    "fetch_opinions.py":        0.00,   # CourtListener API, free
    "summarize_opinions.py":    0.50,   # ~$0.02/opinion, depends on new opinions
    "issue_analysis.py":        0.70,
    "vote_prediction.py":       4.10,   # 9 justice calls (reduced with caching)
    "scenario_construction.py": 0.70,
    "export_to_website.py":     0.80,
}


def load_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            return json.load(f)
    return {"term": None, "cases": {}}


def save_status(status):
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f, indent=2)


def step_already_done(case_dir, output_file):
    """Check if a pipeline step's output already exists."""
    if output_file is None:
        return False
    return os.path.exists(os.path.join(case_dir, output_file))


def preflight_check(case_dir):
    """Verify the case has the required inputs to run the pipeline."""
    issues = []
    if not os.path.exists(os.path.join(case_dir, "case_info.txt")):
        issues.append("Missing case_info.txt")

    briefs_dir = os.path.join(case_dir, "briefs")
    if not os.path.isdir(briefs_dir):
        issues.append("Missing briefs/ directory")
    elif not list(Path(briefs_dir).glob("*.pdf")):
        issues.append("No PDF files in briefs/")

    transcript_dir = os.path.join(case_dir, "transcript")
    if not os.path.isdir(transcript_dir):
        issues.append("Missing transcript/ directory")
    elif not list(Path(transcript_dir).glob("*.pdf")):
        issues.append("No PDF files in transcript/")

    return issues


def run_step(script_name, case_dir, step_desc):
    """Run a single pipeline step. Returns True on success."""
    script_path = os.path.join(SCRIPT_DIR, script_name)
    if not os.path.exists(script_path):
        print(f"    ERROR: Script not found: {script_path}")
        return False

    # summarize_opinions.py doesn't take a case dir argument
    if script_name == "summarize_opinions.py":
        cmd = [PYTHON, script_path]
    else:
        cmd = [PYTHON, script_path, case_dir]

    print(f"    Running: {step_desc}...")
    start = time.time()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=1800,  # 30 minute timeout per step
            cwd=SCRIPT_DIR,
        )
        elapsed = time.time() - start

        if result.returncode != 0:
            print(f"    FAILED ({elapsed:.0f}s)")
            # Show the last few lines of stderr for debugging
            stderr_lines = result.stderr.strip().split("\n")
            for line in stderr_lines[-5:]:
                if line.strip():
                    print(f"      {line.strip()}")
            return False

        print(f"    Done ({elapsed:.0f}s)")
        # Show last few lines of stdout for visibility
        stdout_lines = result.stdout.strip().split("\n")
        for line in stdout_lines[-3:]:
            if line.strip():
                print(f"      {line.strip()}")
        return True

    except subprocess.TimeoutExpired:
        print(f"    TIMEOUT (30 min limit)")
        return False
    except Exception as e:
        print(f"    ERROR: {e}")
        return False


def estimate_costs(cases_to_process):
    """Estimate pipeline cost for the given cases."""
    total_cost = 0
    case_details = []

    for case_dir, docket in cases_to_process:
        steps_needed = []
        case_cost = 0
        for script, desc, output_file, _ in PIPELINE_STEPS:
            if not step_already_done(case_dir, output_file):
                steps_needed.append(desc)
                case_cost += STEP_COSTS.get(script, 0)
        if steps_needed:
            total_cost += case_cost
            case_details.append({
                "docket": docket,
                "steps": steps_needed,
                "cost": case_cost,
            })

    return total_cost, case_details


def process_case(case_dir, docket, force=False):
    """Run the full pipeline on one case."""
    print(f"\n{'='*60}")
    print(f"PIPELINE: {docket}")
    print(f"Directory: {case_dir}")
    print(f"{'='*60}")

    issues = preflight_check(case_dir)
    if issues:
        print(f"  Pre-flight FAILED:")
        for issue in issues:
            print(f"    - {issue}")
        return False
    print(f"  Pre-flight OK")

    all_success = True
    for script, desc, output_file, takes_case_dir in PIPELINE_STEPS:
        if not force and step_already_done(case_dir, output_file):
            print(f"    Skipping: {desc} (already complete)")
            continue

        success = run_step(script, case_dir, desc)
        if not success:
            print(f"  Pipeline stopped at: {desc}")
            all_success = False
            break

    if all_success:
        print(f"\n  Pipeline COMPLETE for {docket}")
    return all_success


def resolve_case(arg):
    """Resolve a docket number or path to (case_dir, docket)."""
    arg = arg.rstrip("/")
    if os.path.isdir(arg):
        return os.path.abspath(arg), os.path.basename(arg)
    # Try as docket number
    case_dir = os.path.join(CASES_DIR, arg)
    if os.path.isdir(case_dir):
        return case_dir, arg
    print(f"Error: Case directory not found: {case_dir}")
    sys.exit(1)


def get_ready_cases(force=False):
    """Get cases that are ready for pipeline processing."""
    status = load_status()
    cases = []
    for docket, info in status.get("cases", {}).items():
        directory = info.get("directory", docket)
        case_dir = os.path.join(CASES_DIR, directory)
        if not os.path.isdir(case_dir):
            continue
        if force:
            if info.get("pipeline_ready") or info.get("briefs_downloaded"):
                cases.append((case_dir, docket))
        else:
            if info.get("pipeline_ready") and not info.get("pipeline_complete"):
                cases.append((case_dir, docket))
    return cases


def main():
    args = sys.argv[1:]
    force = "--force" in args
    estimate_only = "--estimate" in args
    args = [a for a in args if not a.startswith("--")]

    if args:
        # Single case mode
        case_dir, docket = resolve_case(args[0])

        if estimate_only:
            total_cost, details = estimate_costs([(case_dir, docket)])
            print(f"\nCost estimate for {docket}: ~${total_cost:.2f}")
            if details:
                for d in details:
                    print(f"  Steps needed: {', '.join(d['steps'])}")
            sys.exit(0)

        success = process_case(case_dir, docket, force=force)

        # Update status
        status = load_status()
        if docket in status.get("cases", {}):
            if success:
                status["cases"][docket]["pipeline_complete"] = True
                status["cases"][docket]["state"] = "pipeline_complete"
            save_status(status)

        sys.exit(0 if success else 1)
    else:
        # Batch mode — all ready cases
        cases = get_ready_cases(force=force)

        if not cases:
            print("No cases ready for pipeline processing.")
            print("\nTo prepare cases:")
            print("  1. python3 fetch_docket.py        # discover cases")
            print("  2. python3 fetch_sources.py --all  # download sources")
            print("  3. python3 run_pipeline.py         # run pipeline")
            sys.exit(0)

        if estimate_only:
            total_cost, details = estimate_costs(cases)
            print(f"\n{'='*60}")
            print(f"COST ESTIMATE")
            print(f"{'='*60}")
            print(f"  Cases to process: {len(details)}")
            print(f"  Estimated total:  ~${total_cost:.2f}")
            print()
            for d in details:
                print(f"  {d['docket']}: ~${d['cost']:.2f}")
                print(f"    Steps: {', '.join(d['steps'])}")
            print(f"\nTo proceed, run without --estimate")
            sys.exit(0)

        print(f"Processing {len(cases)} cases...")
        success_count = 0
        fail_count = 0
        status = load_status()

        for case_dir, docket in sorted(cases, key=lambda x: x[1]):
            success = process_case(case_dir, docket, force=force)
            if success:
                success_count += 1
                if docket in status.get("cases", {}):
                    status["cases"][docket]["pipeline_complete"] = True
                    status["cases"][docket]["state"] = "pipeline_complete"
            else:
                fail_count += 1
            save_status(status)

        print(f"\n{'='*60}")
        print(f"PIPELINE SUMMARY")
        print(f"{'='*60}")
        print(f"  Succeeded: {success_count}")
        print(f"  Failed:    {fail_count}")
        print(f"  Total:     {success_count + fail_count}")


if __name__ == "__main__":
    main()

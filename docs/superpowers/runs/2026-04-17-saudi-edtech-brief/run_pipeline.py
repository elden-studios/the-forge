"""Reproduce the 2026-04-17 Saudi EdTech Wave 3 simulation run.

This is the thin reproducer. It invokes the shipped Cabinet Framing
simulation driver with the --brief edtech canned inputs and relies on
the driver to:
  1. Write cabinet_framing + pre_mortem blocks onto forge-tasks.json
  2. Generate + persist a sample Cabinet Verdict decision (dec-xxxxxxxx)
     onto forge-decisions.json via append_decision_persist
  3. Run validator.validate_project to confirm Standing Rule 11 is
     satisfied (cabinet_framing present AND >=1 decision for current_project)

Run from repo root:
    python3 docs/superpowers/runs/2026-04-17-saudi-edtech-brief/run_pipeline.py

Source fixtures used:
    scripts/sample_inputs/cabinet_lenses_edtech.json
    scripts/sample_inputs/pre_mortem_edtech.json

For the original Saudi PropTech variant, pass --brief proptech (or omit
the flag — proptech is the default for backward compatibility).
"""
import os
import subprocess
import sys

REPO = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
)


def main():
    driver = os.path.join(REPO, "scripts", "cabinet_framing_simulate.py")
    subprocess.check_call([sys.executable, driver, "--brief", "edtech"])


if __name__ == "__main__":
    main()

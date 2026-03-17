#!/usr/bin/env python3
"""
simulate_github_ci_event.py — Demo script for GitHub Actions integration.

What this does:
  1. Bootstraps all tools (including GitHubTool).
  2. Fetches the latest GitHub Actions workflow logs for your repo.
  3. Sends the logs through EventIngestionLayer → WorkflowGraph.
  4. Prints structured output: failed tests, analysis, plan, and ticket.

Usage:
    # With live GitHub data:
    export GITHUB_TOKEN=ghp_yourtoken
    export GITHUB_REPO=owner/repo
    python scripts/simulate_github_ci_event.py

    # Target a specific workflow:
    python scripts/simulate_github_ci_event.py --workflow ci.yml

    # Use bundled sample logs (no token needed):
    python scripts/simulate_github_ci_event.py --sample
"""
from __future__ import annotations

import argparse
import json
import os
import sys

# Allow running from any directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

load_dotenv()

from observability import init_telemetry

init_telemetry("multiagent-orchestrator")

from tools.tool_registry import ToolRegistry
from events import EventIngestionLayer, EventRouter
from utils.logger import get_logger

logger = get_logger("GitHubCIDemo")

# ── Sample fallback logs ───────────────────────────────────────────────────
SAMPLE_LOGS = """\
=== 1_Checkout.txt ===
[INFO] Checked out repo @ main (abc1234)

=== 2_Setup Python.txt ===
[INFO] Python 3.11.8 installed

=== 3_Run tests.txt ===
[INFO] pytest -v --tb=short
FAILED tests/test_auth.py::test_login_timeout
    TimeoutError: login service did not respond within 30s
FAILED tests/test_payments.py::test_checkout_flaky
    AssertionError: Expected 'SUCCESS', got 'PENDING' (race condition)
ERROR tests/test_notifications.py::test_smtp_send
    ConnectionError: SMTP server unreachable

=== 4_Post job.txt ===
[ERROR] 3 tests failed. Build FAILED.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simulate a GitHub Actions CI failure event through QAOps pipeline"
    )
    parser.add_argument(
        "--repo",
        default=os.getenv("GITHUB_REPO", ""),
        help="GitHub repo (owner/repo). Defaults to GITHUB_REPO env var.",
    )
    parser.add_argument(
        "--workflow",
        default="",
        help="Workflow file name, e.g. 'ci.yml'. Omit for latest run.",
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Use bundled sample logs instead of fetching from GitHub.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Run ExecutionAgent in dry-run mode (default: True).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # ── Bootstrap tools ───────────────────────────────────────────────────
    ToolRegistry.bootstrap()

    # ── Wire pipeline ─────────────────────────────────────────────────────
    router  = EventRouter(dry_run=args.dry_run)
    ingress = EventIngestionLayer()
    ingress.register_handler(router)

    # ── Determine log source ──────────────────────────────────────────────
    if args.sample:
        logger.info("[Demo] Using bundled sample logs (--sample flag set)")
        event = ingress.ingest_logs(
            ci_logs=SAMPLE_LOGS,
            source="github_actions",
        )
    elif args.repo or os.getenv("GITHUB_REPO"):
        repo     = args.repo or os.getenv("GITHUB_REPO", "")
        workflow = args.workflow

        logger.info(f"[Demo] Fetching GitHub Actions logs: repo={repo!r} workflow={workflow!r}")
        event = ingress.ingest_github_event(repo=repo, workflow=workflow)
    else:
        print(
            "\n⚠️  No GitHub repo configured.\n"
            "   Set GITHUB_REPO env var or pass --repo owner/repo\n"
            "   Or use --sample to run with bundled demo logs.\n"
        )
        sys.exit(1)

    # ── Retrieve result from router ───────────────────────────────────────
    # EventRouter stores the last result; re-call with same event for output.
    result = router(event)

    # ── Pretty-print output ───────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  QAOps Pipeline — GitHub Actions Demo Result")
    print("=" * 60)
    print(json.dumps(result, indent=2, default=str))
    print("=" * 60)

    ticket = result.get("ticket_url") or result.get("ticket", "")
    source = result.get("ticket_source", "none")

    if ticket:
        label = "JIRA" if source == "jira" else "GitHub Issue"
        print(f"\n✅  {label} created: {ticket}")
    else:
        print("\n⚠️   No ticket created (configure JIRA_* or GITHUB_TOKEN + GITHUB_REPO)")

    failed = result.get("failed_tests", [])
    print(f"🔍  Failed tests detected: {len(failed)}")
    for t in failed:
        print(f"     • {t}")

    print()


if __name__ == "__main__":
    main()
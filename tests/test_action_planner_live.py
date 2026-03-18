"""
Live verification test for ActionPlannerAgent.
Tests both confidence threshold gating and real Jira ticket creation.

Run:  python tests/test_action_planner_live.py
"""
import os
import sys
import logging

from dotenv import load_dotenv

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from adk import Message
from agents.action_planner_agent import ActionPlannerAgent

agent = ActionPlannerAgent()

PASS = "\033[92m PASS\033[0m"
FAIL = "\033[91m FAIL\033[0m"

results = []

# ─────────────────────────────────────────────────────────────────────────────
# TEST 1 — confidence >= 0.8 → plan generated + Jira ticket created
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*70)
print("TEST 1: confidence=0.85  →  expect plan + real Jira ticket (SCRUM)")
print("="*70)

msg_high = Message(
    sender="RootCauseAnalyzerAgent",
    receiver="ActionPlannerAgent",
    content={
        "root_causes": [
            "AssertionError in testUserAuthentication",
            "ConnectException in testCreateUser",
        ],
        "confidence": 0.85,
        "error_categories": ["assertion", "connection_error"],
        "analysis": (
            "Two tests failed in Build #123 of WebApp-Main. "
            "testUserAuthentication failed with AssertionError (expected true, got false), "
            "indicating broken authentication logic or stale test credentials. "
            "testCreateUser failed with ConnectException (Connection refused), "
            "indicating the backend API service was not running or port was blocked "
            "when tests executed."
        ),
    },
)

result_high = agent._run(msg_high)
c = result_high.content

print(f"  priority       : {c['priority']}")
print(f"  confidence     : {c['confidence']}")
print(f"  plan steps     : {len(c['plan'])}")
for step in c["plan"]:
    print(f"    - {step}")
print(f"  error_categories: {c['error_categories']}")
print(f"  ticket_url     : {c['ticket_url'] or '(empty — ticket creation failed)'}")

t1_plan_ok   = len(c["plan"]) >= 2
t1_ticket_ok = "cicdagent.atlassian.net/browse/SCRUM" in (c["ticket_url"] or "")
t1_priority  = c["priority"] == "HIGH"

print(f"\n  [plan generated]   {PASS if t1_plan_ok else FAIL}")
print(f"  [priority=HIGH]    {PASS if t1_priority else FAIL}")
print(f"  [Jira ticket SCRUM] {PASS if t1_ticket_ok else FAIL + ' — got: ' + (c['ticket_url'] or 'EMPTY')}")

results.append(("TEST 1 (confidence=0.85)", t1_plan_ok and t1_ticket_ok and t1_priority))


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2 — confidence < 0.8 → plan skipped, NO Jira ticket
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*70)
print("TEST 2: confidence=0.65  →  expect no plan, no ticket")
print("="*70)

msg_low = Message(
    sender="RootCauseAnalyzerAgent",
    receiver="ActionPlannerAgent",
    content={
        "root_causes": ["Possible flaky test"],
        "confidence": 0.65,
        "error_categories": ["unknown"],
        "analysis": "Inconclusive failure pattern — insufficient data.",
    },
)

result_low = agent._run(msg_low)
c2 = result_low.content

print(f"  priority      : {c2['priority']}")
print(f"  confidence    : {c2['confidence']}")
print(f"  plan          : {c2['plan']}")
print(f"  ticket_url    : {c2['ticket_url'] or '(empty — expected)'}")

t2_no_ticket = c2["ticket_url"] == ""
t2_priority  = c2["priority"] == "MEDIUM"
t2_skipped   = "manual review required" in c2["plan"][0].lower() if c2["plan"] else False

print(f"\n  [no ticket created]      {PASS if t2_no_ticket else FAIL}")
print(f"  [priority=MEDIUM]        {PASS if t2_priority else FAIL}")
print(f"  [skip message in plan]   {PASS if t2_skipped else FAIL}")

results.append(("TEST 2 (confidence=0.65)", t2_no_ticket and t2_priority and t2_skipped))


# ─────────────────────────────────────────────────────────────────────────────
# TEST 3 — confidence exactly at boundary (0.8) → plan + ticket
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*70)
print("TEST 3: confidence=0.80 (boundary) →  expect plan + ticket")
print("="*70)

msg_boundary = Message(
    sender="RootCauseAnalyzerAgent",
    receiver="ActionPlannerAgent",
    content={
        "root_causes": ["NullPointerException in testPayment"],
        "confidence": 0.80,
        "error_categories": ["null_pointer"],
        "analysis": "Payment test failed with NPE suggesting uninitialised payment provider.",
    },
)

result_boundary = agent._run(msg_boundary)
c3 = result_boundary.content

print(f"  priority      : {c3['priority']}")
print(f"  plan          : {c3['plan']}")
print(f"  ticket_url    : {c3['ticket_url'] or '(empty — ticket creation failed)'}")

t3_plan_ok   = len(c3["plan"]) >= 1 and "manual review" not in c3["plan"][0].lower()
t3_ticket_ok = "cicdagent.atlassian.net/browse/SCRUM" in (c3["ticket_url"] or "")

print(f"\n  [plan generated]    {PASS if t3_plan_ok else FAIL}")
print(f"  [Jira ticket SCRUM] {PASS if t3_ticket_ok else FAIL + ' — got: ' + (c3['ticket_url'] or 'EMPTY')}")

results.append(("TEST 3 (confidence=0.80 boundary)", t3_plan_ok and t3_ticket_ok))


# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
all_passed = True
for name, passed in results:
    status = PASS if passed else FAIL
    print(f"  {status}  {name}")
    all_passed = all_passed and passed

print()
if all_passed:
    print("\033[92mAll tests passed!\033[0m")
    sys.exit(0)
else:
    print("\033[91mSome tests failed — check logs above.\033[0m")
    sys.exit(1)

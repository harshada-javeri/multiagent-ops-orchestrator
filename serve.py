#!/usr/bin/env python3
"""
Flask web service for QAOps Multi-Agent System.
Adds /events endpoint for structured CIFailureEvent ingestion.
"""
import os

from dotenv import load_dotenv

load_dotenv()

from observability import init_telemetry

init_telemetry("multiagent-orchestrator")

from flask import Flask, jsonify, request

from main_orchestrator import run_qaops_pipeline, _ingress
from tools.tool_registry import ToolRegistry
from utils.logger import get_logger

app = Flask(__name__)
logger = get_logger("QAOpsAPI")


@app.route("/health", methods=["GET"])
def health():
    """Health check — also reports registered tools."""
    return jsonify(
        {
            "status": "healthy",
            "service": "QAOps Multi-Agent Orchestrator",
            "version": "2.0",
            "tools": ToolRegistry.list_tools(),
        }
    ), 200


@app.route("/predict", methods=["POST"])
def predict():
    """
    Backward-compatible prediction endpoint.
    Body: {"ci_logs": "<raw log string>"}
    """
    body = request.get_json(force=True) or {}
    ci_logs: str = body.get("ci_logs", "")
    if not ci_logs.strip():
        return jsonify({"error": "'ci_logs' field is required and must be non-empty"}), 400

    result = run_qaops_pipeline(ci_logs)
    if result.get("status") == "error":
        return jsonify(result), 500
    return jsonify(result), 200


@app.route("/events", methods=["POST"])
def ingest_event():
    """
    Structured event ingestion endpoint.

    Accepts a full CIFailureEvent payload:
    {
        "ci_logs":   "<string>",
        "source":    "jenkins" | "github_actions" | "manual" | ...,
        "severity":  "critical" | "high" | "medium" | "low",
        "branch":    "<optional>",
        "build_url": "<optional>"
    }
    """
    body = request.get_json(force=True) or {}
    try:
        event = _ingress.ingest(body)
        return jsonify({"event_id": event.event_id, "status": "accepted"}), 202
    except Exception as exc:
        logger.error(f"[API] Event ingestion error: {exc}", exc_info=True)
        return jsonify({"error": str(exc)}), 422


@app.route("/", methods=["GET"])
def root():
    return jsonify(
        {
            "service": "QAOps Multi-Agent Orchestrator",
            "version": "2.0",
            "endpoints": {
                "GET  /health":  "Health check + tool registry status",
                "POST /predict": "Analyse CI logs (raw string body)",
                "POST /events":  "Ingest structured CIFailureEvent",
                "GET  /":        "API documentation",
            },
        }
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 9696))
    logger.info(f"Starting QAOps API on port {port}")
    app.run(host="0.0.0.0", port=port, debug=os.getenv("DEBUG", "false").lower() == "true")
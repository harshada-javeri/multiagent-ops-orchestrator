#!/usr/bin/env python3
"""
Flask web service for QAOps Multi-Agent System
Provides REST API endpoints for CI/CD failure analysis
"""

from dotenv import load_dotenv
load_dotenv()

from monocle_apptrace import setup_monocle_telemetry
setup_monocle_telemetry(workflow_name="serve")

from flask import Flask, request, jsonify
import os
from predict import QAOpsPredictor
from utils.logger import get_logger

app = Flask(__name__)
logger = get_logger("QAOpsAPI")

# Initialize predictor
try:
    predictor = QAOpsPredictor()
    logger.info("QAOps predictor initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize predictor: {e}")
    predictor = None

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "QAOps Multi-Agent Orchestrator",
        "version": "1.0"
    }), 200

@app.route('/predict', methods=['POST'])
def predict():
    """
    Prediction endpoint
    Expects JSON: {"ci_logs": "log content here"}
    Returns: {"failed_tests": [...], "analysis": "...", "remediation_plan": "..."}
    """
    try:
        if not predictor:
            return jsonify({"error": "Predictor not initialized"}), 500
        
        data = request.get_json()
        if not data or 'ci_logs' not in data:
            return jsonify({
                "error": "Missing 'ci_logs' field in request body"
            }), 400
        
        ci_logs = data['ci_logs']
        if not isinstance(ci_logs, str) or not ci_logs.strip():
            return jsonify({
                "error": "ci_logs must be a non-empty string"
            }), 400
        
        # Run prediction
        result = predictor.predict(ci_logs)
        
        if result.get("status") == "error":
            return jsonify(result), 500
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Prediction endpoint error: {e}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API documentation"""
    return jsonify({
        "service": "QAOps Multi-Agent Orchestrator",
        "version": "1.0",
        "endpoints": {
            "GET /health": "Health check",
            "POST /predict": "Analyze CI/CD logs and generate remediation plan",
            "GET /": "This documentation"
        },
        "example_request": {
            "url": "/predict",
            "method": "POST",
            "body": {
                "ci_logs": "[ERROR] test_login FAILED due to timeout\\n[INFO] Build finished"
            }
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 9696))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting QAOps API server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
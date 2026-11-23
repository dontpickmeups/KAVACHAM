
from flask import Flask, render_template, jsonify, request
from pathlib import Path
import json
import sys

app = Flask(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = PROJECT_ROOT / "scan_report.json"

# Make the existing scanner importable
SCANNER_DIR = Path(__file__).resolve().parent / "scanner"
sys.path.insert(0, str(SCANNER_DIR))

from repository_manager import process_repository


@app.route("/")
def dashboard():
    return render_template("index.html")


@app.route("/api/report")
def get_report():
    if not REPORT_PATH.exists():
        return jsonify({"error": "No scan report found"}), 404

    try:
        with open(REPORT_PATH, "r", encoding="utf-8") as file:
            return jsonify(json.load(file))
    except (json.JSONDecodeError, OSError) as error:
        return jsonify({"error": str(error)}), 500


@app.route("/api/scan", methods=["POST"])
def scan_repository():
    data = request.get_json(silent=True) or {}
    repo_url = data.get("repo_url", "").strip()

    if not repo_url:
        return jsonify({"error": "Please enter a GitHub repository URL"}), 400

    try:
        report = process_repository(repo_url)

        if not report:
            return jsonify({
                "error": "Scan failed or no supported dependency files were found."
            }), 400

        return jsonify(report)

    except Exception as error:
        return jsonify({"error": str(error)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)

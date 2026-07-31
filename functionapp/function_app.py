"""Azure Functions v2 (Python) — medical record analysis pipeline.

Functions:
    * analyze: HTTP POST /api/analyze
      Request body is raw PDF bytes. Returns ACU extraction JSON.
    * healthcheck: HTTP GET /api/health
      Reports account + analyzer readiness.
"""
from __future__ import annotations

import base64
import json
import logging
import os
import time

import azure.functions as func
import httpx
from azure.identity import DefaultAzureCredential

app = func.FunctionApp()

ACU_ENDPOINT = os.environ.get("ACU_ENDPOINT", "").rstrip("/")
API_VERSION = os.environ.get("ACU_API_VERSION", "2025-11-01")
OUTPUT_CONTAINER = os.environ.get("OUTPUT_CONTAINER", "output")
DEFAULT_ANALYZER = os.environ.get("DEFAULT_ANALYZER", "healthcareDischargeSummaryV1")

_credential = DefaultAzureCredential()


def _acu_token() -> str:
    return _credential.get_token("https://cognitiveservices.azure.com/.default").token


def _analyze_pdf(pdf_bytes: bytes, analyzer_id: str) -> dict:
    token = _acu_token()
    payload = {"inputs": [{"data": base64.b64encode(pdf_bytes).decode("ascii")}]}
    with httpx.Client(timeout=120.0, headers={"Authorization": f"Bearer {token}"}) as client:
        submit = client.post(
            f"{ACU_ENDPOINT}/contentunderstanding/analyzers/{analyzer_id}:analyze?api-version={API_VERSION}",
            headers={"Content-Type": "application/json"},
            json=payload,
        )
        try:
            submit.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"ACU analyze request failed ({exc.response.status_code}): {exc.response.text}"
            ) from exc
        op_url = submit.headers.get("operation-location") or submit.headers.get("Operation-Location")
        if not op_url:
            return submit.json()

        # Poll until done (max 5 min).
        deadline = time.time() + 300
        while time.time() < deadline:
            r = client.get(op_url)
            r.raise_for_status()
            body = r.json()
            status = (body.get("status") or "").lower()
            if status in {"succeeded", "failed", "completed"}:
                return body
            time.sleep(3)
        raise TimeoutError(f"Analyzer {analyzer_id} did not finish in time")


@app.route(route="analyze", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
def analyze(req: func.HttpRequest) -> func.HttpResponse:
    analyzer_id = req.params.get("analyzerId", DEFAULT_ANALYZER)
    pdf_bytes = req.get_body()
    if not pdf_bytes:
        return func.HttpResponse(
            json.dumps({"error": "Request body is empty. Send raw PDF bytes."}),
            status_code=400,
            mimetype="application/json",
        )

    try:
        result = _analyze_pdf(pdf_bytes, analyzer_id)
        payload = {
            "analyzer": analyzer_id,
            "status": result.get("status"),
            "result": result.get("result") or result,
        }
        return func.HttpResponse(json.dumps(payload, indent=2), mimetype="application/json")
    except Exception as exc:  # noqa: BLE001
        logging.exception("Analyzer failed")
        return func.HttpResponse(
            json.dumps({"analyzer": analyzer_id, "error": str(exc)}),
            status_code=500,
            mimetype="application/json",
        )


@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def healthcheck(req: func.HttpRequest) -> func.HttpResponse:
    payload = {
        "status": "ok",
        "acuEndpoint": ACU_ENDPOINT,
        "defaultAnalyzer": DEFAULT_ANALYZER,
        "outputContainer": OUTPUT_CONTAINER,
    }
    try:
        token = _acu_token()
        with httpx.Client(timeout=30.0, headers={"Authorization": f"Bearer {token}"}) as client:
            r = client.get(f"{ACU_ENDPOINT}/contentunderstanding/analyzers?api-version={API_VERSION}")
            payload["analyzersRegistered"] = len(r.json().get("value", []))
    except Exception as exc:  # noqa: BLE001
        payload["acuProbeError"] = str(exc)
    return func.HttpResponse(json.dumps(payload, indent=2), mimetype="application/json")

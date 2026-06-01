"""Lightweight local HTTP API for chart and agent integrations."""

from __future__ import annotations

import json
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from .agent import DEFAULT_AGENT_QUESTION, MingLiAgent
from .chart_api import build_bazi_chart
from .models.base import ModelClient
from .web_ui import render_index_html


MAX_REQUEST_BYTES = 1024 * 1024


@dataclass(frozen=True)
class ApiConfig:
    """Configuration shared by all requests handled by the local API."""

    fortune_data_path: Optional[str] = None
    model_name: Optional[str] = None
    provider: Optional[str] = None
    env_file: Optional[str] = None


def chart_response(
    payload: Dict[str, Any],
    *,
    fortune_data_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a chart API response from a ChartInput-like payload."""

    if not isinstance(payload, dict):
        raise ValueError("chart request body must be a JSON object")
    return build_bazi_chart(payload, fortune_data_path=fortune_data_path).as_dict()


def agent_response(
    payload: Dict[str, Any],
    *,
    model_client: Optional[ModelClient] = None,
    fortune_data_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Build an agent API response from a direct or wrapped chart payload."""

    if not isinstance(payload, dict):
        raise ValueError("agent request body must be a JSON object")

    chart_input = payload.get("chart_input", payload)
    if not isinstance(chart_input, dict):
        raise ValueError("chart_input must be a JSON object")

    question = str(payload.get("question") or DEFAULT_AGENT_QUESTION)
    return MingLiAgent(model_client).run(
        chart_input,
        question=question,
        fortune_data_path=fortune_data_path,
    ).as_dict()


def create_model_client(
    model_name: str,
    *,
    provider: Optional[str] = None,
    env_file: Optional[str] = None,
) -> ModelClient:
    """Create a model client for API server use."""

    from .models.factory import ModelFactory
    from .utils.config import load_config

    config = load_config(env_file)
    return ModelFactory.create(model_name, provider=provider, config=config)


class MingLiApiHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the local MingLi API."""

    server_version = "MingLiBenchHTTP/0.1"

    def do_OPTIONS(self) -> None:
        self._send_json(204, None)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in {"/", "/app"}:
            self._send_html(200, render_index_html(self._model_name()))
            return
        if path == "/health":
            self._send_json(
                200,
                {
                    "status": "ok",
                    "service": "mingli-bench",
                    "endpoints": ["/", "/health", "/chart", "/agent"],
                    "model": self._model_name(),
                },
            )
            return
        self._send_json(404, {"error": {"message": f"unknown endpoint: {path}"}})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            payload = self._read_json_body()
            if path == "/chart":
                self._send_json(
                    200,
                    chart_response(
                        payload,
                        fortune_data_path=self._config().fortune_data_path,
                    ),
                )
                return
            if path == "/agent":
                self._send_json(
                    200,
                    agent_response(
                        payload,
                        model_client=self._model_client(),
                        fortune_data_path=self._config().fortune_data_path,
                    ),
                )
                return
            self._send_json(404, {"error": {"message": f"unknown endpoint: {path}"}})
        except Exception as error:
            self._send_json(
                400,
                {
                    "error": {
                        "type": error.__class__.__name__,
                        "message": str(error),
                    }
                },
            )

    def log_message(self, format: str, *args: Any) -> None:
        """Keep test and CLI output focused unless callers add their own logging."""

    def _config(self) -> ApiConfig:
        return getattr(self.server, "api_config", ApiConfig())

    def _model_client(self) -> Optional[ModelClient]:
        return getattr(self.server, "model_client", None)

    def _model_name(self) -> Optional[str]:
        model_client = self._model_client()
        return model_client.model_name if model_client else None

    def _read_json_body(self) -> Dict[str, Any]:
        raw_length = self.headers.get("Content-Length", "0")
        try:
            content_length = int(raw_length)
        except ValueError as error:
            raise ValueError("invalid Content-Length header") from error
        if content_length > MAX_REQUEST_BYTES:
            raise ValueError("request body is too large")
        raw = self.rfile.read(content_length)
        if not raw:
            return {}
        try:
            parsed = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError("request body must be valid JSON") from error
        if not isinstance(parsed, dict):
            raise ValueError("request body must be a JSON object")
        return parsed

    def _send_json(self, status: int, payload: Optional[Dict[str, Any]]) -> None:
        encoded = b"" if payload is None else json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        ).encode("utf-8")
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        if encoded:
            self.wfile.write(encoded)

    def _send_html(self, status: int, html: str) -> None:
        encoded = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def create_server(
    host: str = "127.0.0.1",
    port: int = 8765,
    *,
    config: Optional[ApiConfig] = None,
    model_client: Optional[ModelClient] = None,
) -> ThreadingHTTPServer:
    """Create a configured HTTP server without starting it."""

    server = ThreadingHTTPServer((host, port), MingLiApiHandler)
    server.api_config = config or ApiConfig()
    server.model_client = model_client
    return server


def run_server(
    host: str = "127.0.0.1",
    port: int = 8765,
    *,
    fortune_data_path: Optional[str] = None,
    model_name: Optional[str] = None,
    provider: Optional[str] = None,
    env_file: Optional[str] = None,
) -> None:
    """Start the local HTTP API server and block until interrupted."""

    model_client = (
        create_model_client(model_name, provider=provider, env_file=env_file)
        if model_name
        else None
    )
    server = create_server(
        host,
        port,
        config=ApiConfig(
            fortune_data_path=fortune_data_path,
            model_name=model_name,
            provider=provider,
            env_file=env_file,
        ),
        model_client=model_client,
    )
    actual_host, actual_port = server.server_address
    print(f"MingLi API server running at http://{actual_host}:{actual_port}", flush=True)
    print("Open the web UI or use: GET /health, POST /chart, POST /agent", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nMingLi API server stopped.", flush=True)
    finally:
        server.server_close()


__all__ = [
    "ApiConfig",
    "MingLiApiHandler",
    "agent_response",
    "chart_response",
    "create_model_client",
    "create_server",
    "run_server",
]

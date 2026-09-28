from __future__ import annotations

import json
import ssl
import time
import uuid
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlencode, urlparse, urlunparse

import requests
import websocket


@dataclass
class ProbeResult:
    reachable: bool = False
    kernel_started: bool = False
    workload_completed: bool = False
    kernel_start_seconds: float | None = None
    execution_seconds: float | None = None
    total_seconds: float | None = None
    outputs: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def _ws_url(http_url: str) -> str:
    parsed = urlparse(http_url)
    scheme = "wss" if parsed.scheme == "https" else "ws"
    return urlunparse(parsed._replace(scheme=scheme))


def run_probe(
    base_url: str,
    token: str,
    kernel_name: str,
    code: str,
    request_timeout: float,
    kernel_timeout: float,
    execution_timeout: float,
    verify_tls: bool,
) -> ProbeResult:
    result = ProbeResult()
    started = time.monotonic()
    session = requests.Session()
    session.headers.update({"Authorization": f"token {token}"})
    kernel_id: str | None = None

    try:
        api_started = time.monotonic()
        response = session.get(
            f"{base_url}/api",
            timeout=request_timeout,
            verify=verify_tls,
        )
        response.raise_for_status()
        result.reachable = True

        response = session.post(
            f"{base_url}/api/kernels",
            json={"name": kernel_name},
            timeout=kernel_timeout,
            verify=verify_tls,
        )
        response.raise_for_status()
        kernel_id = response.json()["id"]
        result.kernel_started = True
        result.kernel_start_seconds = time.monotonic() - api_started

        session_id = uuid.uuid4().hex
        query = urlencode({"session_id": session_id, "token": token})
        channel_url = _ws_url(
            f"{base_url}/api/kernels/{kernel_id}/channels?{query}"
        )
        sslopt = {} if verify_tls else {"cert_reqs": ssl.CERT_NONE}
        ws = websocket.create_connection(
            channel_url,
            timeout=execution_timeout,
            sslopt=sslopt,
            cookie="; ".join(
                f"{key}={value}" for key, value in session.cookies.items()
            ),
        )
        msg_id = uuid.uuid4().hex
        execute_request = {
            "header": {
                "msg_id": msg_id,
                "username": "event-wifi",
                "session": session_id,
                "date": "",
                "msg_type": "execute_request",
                "version": "5.3",
            },
            "parent_header": {},
            "metadata": {},
            "content": {
                "code": code,
                "silent": False,
                "store_history": False,
                "user_expressions": {},
                "allow_stdin": False,
                "stop_on_error": True,
            },
            "channel": "shell",
            "buffers": [],
        }
        execution_started = time.monotonic()
        ws.send(json.dumps(execute_request))
        deadline = execution_started + execution_timeout

        while time.monotonic() < deadline:
            message = json.loads(ws.recv())
            if message.get("parent_header", {}).get("msg_id") != msg_id:
                continue
            msg_type = message.get("msg_type") or message.get("header", {}).get(
                "msg_type"
            )
            content = message.get("content", {})
            if msg_type == "stream":
                result.outputs.append(content.get("text", ""))
            elif msg_type == "error":
                result.errors.append(
                    f"{content.get('ename', 'Error')}: {content.get('evalue', '')}"
                )
            elif msg_type == "status" and content.get("execution_state") == "idle":
                result.workload_completed = not result.errors
                break
        else:
            result.errors.append("Execution timed out before kernel became idle")
        ws.close()
        result.execution_seconds = time.monotonic() - execution_started
    except Exception as exc:  # boundary: preserve error in test result
        result.errors.append(f"{type(exc).__name__}: {exc}")
    finally:
        if kernel_id:
            try:
                session.delete(
                    f"{base_url}/api/kernels/{kernel_id}",
                    timeout=request_timeout,
                    verify=verify_tls,
                )
            except requests.RequestException as exc:
                result.errors.append(f"Kernel cleanup failed: {exc}")
        result.total_seconds = time.monotonic() - started
        session.close()
    return result


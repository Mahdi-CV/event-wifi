from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Adapter:
    client_id: str
    interface: str
    namespace: str
    mac: str = ""


def load_toml(path: str | Path) -> dict[str, Any]:
    with Path(path).open("rb") as handle:
        return tomllib.load(handle)


def load_adapters(path: str | Path) -> list[Adapter]:
    raw = load_toml(path)
    adapters = [Adapter(**item) for item in raw.get("adapter", [])]
    if not adapters:
        raise ValueError(f"No [[adapter]] entries found in {path}")
    client_ids = [item.client_id for item in adapters]
    if len(client_ids) != len(set(client_ids)):
        raise ValueError("Adapter client_id values must be unique")
    return adapters


def jupyter_url(config: dict[str, Any]) -> str:
    section = config["jupyter"]
    base = section["base_url"].rstrip("/")
    prefix = section.get("api_path_prefix", "").strip("/")
    return f"{base}/{prefix}".rstrip("/") if prefix else base


def required_token(config: dict[str, Any]) -> str:
    env_name = config["jupyter"].get("token_env", "JUPYTER_TOKEN")
    token = os.environ.get(env_name, "")
    if not token:
        raise ValueError(f"Required environment variable {env_name} is not set")
    return token


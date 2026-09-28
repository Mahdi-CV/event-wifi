from pathlib import Path

import pytest

from event_wifi.config import load_adapters


def test_load_adapters(tmp_path: Path):
    path = tmp_path / "adapters.toml"
    path.write_text(
        '[[adapter]]\nclient_id="AUTO-001"\ninterface="wlan1"\nnamespace="ew-1"\n'
    )
    adapters = load_adapters(path)
    assert adapters[0].client_id == "AUTO-001"


def test_duplicate_ids_rejected(tmp_path: Path):
    path = tmp_path / "adapters.toml"
    path.write_text(
        '[[adapter]]\nclient_id="A"\ninterface="w1"\nnamespace="n1"\n'
        '[[adapter]]\nclient_id="A"\ninterface="w2"\nnamespace="n2"\n'
    )
    with pytest.raises(ValueError, match="unique"):
        load_adapters(path)


from __future__ import annotations

import importlib.util
import json
import plistlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "install_local_overlay.py"


def _load_installer_module():
    spec = importlib.util.spec_from_file_location("install_local_overlay", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_installer_materializes_payload_and_launchd_plist_in_clean_home(tmp_path):
    installer = _load_installer_module()
    hermes_home = tmp_path / "home" / ".hermes"
    user_home = tmp_path / "home"

    result = installer.install(
        hermes_home=hermes_home,
        user_home=user_home,
        source_dir=ROOT,
        bootstrap=False,
        run_maintain=False,
    )

    active_policy = hermes_home / "localization" / "support-policy.json"
    active_manager = hermes_home / "scripts" / "hermes_zh_overlay_manager.py"
    plist_path = user_home / "Library" / "LaunchAgents" / "com.muzhen.hermes-zh-overlay-maintain.plist"

    assert Path(result["release_dir"]).exists()
    assert active_policy.exists()
    assert active_manager.exists()
    assert json.loads(active_policy.read_text(encoding="utf-8"))["supported_commit"]
    assert active_manager.read_text(encoding="utf-8") == (
        Path(result["release_dir"]) / "payload" / "scripts" / "hermes_zh_overlay_manager.py"
    ).read_text(encoding="utf-8")

    plist = plistlib.loads(plist_path.read_bytes())
    assert plist["Label"] == "com.muzhen.hermes-zh-overlay-maintain"
    assert plist["ProgramArguments"][1] == str(active_manager)
    assert plist["ProgramArguments"][2:] == ["maintain", "--scheduled"]
    assert plist["WorkingDirectory"] == str(hermes_home)
    assert plist["StartInterval"] == 21600

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_public_docs_exist_and_are_linked():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    install = (ROOT / "docs" / "install.md").read_text(encoding="utf-8")
    release = (ROOT / "docs" / "release.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")

    assert "Hermes 中文化无人值守发布" in readme
    assert "适用对象" in readme
    assert "用户体验视角" in readme
    assert "默认中文的 Hermes" in readme
    assert "正常运行 `hermes update`" in readme
    assert "curl -fsSL https://raw.githubusercontent.com/Muzhen2000/hermes-zh-overlay-release/main/scripts/install_local_overlay.py | python3 -" in readme
    assert "docs/install.md" in readme
    assert "docs/release.md" in readme
    assert "CHANGELOG.md" in readme
    assert "CONTRIBUTING.md" in readme
    assert "LICENSE" in readme
    assert "自动晋升" in readme
    assert "一行安装" in install
    assert "curl -fsSL https://raw.githubusercontent.com/Muzhen2000/hermes-zh-overlay-release/main/scripts/install_local_overlay.py | python3 -" in install
    assert "--no-bootstrap --no-maintain" in install
    assert "~/Desktop/Hermes-ZH-Failures/latest" in install
    assert "release_version" in release
    assert "0.1.0" in release
    assert "验证通过后自动晋升" in release
    assert "初始化 Hermes 中文化无人值守发布仓库" in changelog
    assert "This repository publishes and maintains the Hermes Chinese overlay release system." in contributing
    assert "Apache License" in license_text

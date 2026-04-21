#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml


class VerifyError(RuntimeError):
    """Raised when release verification fails."""


def _read_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise VerifyError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise VerifyError(f"invalid json: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise VerifyError(f"expected object json: {path}")
    return data


def _run(cmd: list[str], *, cwd: Path | None = None) -> str:
    result = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        details = (result.stderr or result.stdout or f"exit {result.returncode}").strip()
        raise VerifyError(f"{' '.join(cmd)} failed: {details}")
    return (result.stdout or "").strip()


def _changed_files(source_dir: Path) -> list[str]:
    names: set[str] = set()
    for cmd in [
        ["git", "diff", "--name-only"],
        ["git", "diff", "--cached", "--name-only"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ]:
        names.update(filter(None, _run(cmd, cwd=source_dir).splitlines()))
    return sorted(names)


def _load_metadata(repo_root: Path, release_id: str | None = None) -> tuple[str, dict, dict]:
    release_index = _read_json(repo_root / "release.json")
    resolved_release = release_id or str(release_index.get("latest_release") or "").strip()
    if not resolved_release:
        raise VerifyError("release.json does not define latest_release")
    manifest = _read_json(repo_root / "releases" / resolved_release / "manifest.json")
    return resolved_release, release_index, manifest


def _patch_files(patch_path: Path) -> list[str]:
    files: list[str] = []
    for line in patch_path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("diff --git a/"):
            continue
        parts = line.split()
        if len(parts) < 4 or not parts[3].startswith("b/"):
            raise VerifyError(f"unexpected patch header: {line}")
        files.append(parts[3][2:])
    return files


def _ui_keys_from_patch(patch_path: Path) -> set[str]:
    helper_prefixes: dict[str, tuple[tuple[str, str], ...]] = {
        "cli.py": (("_cli_ui", "cli."),),
        "gateway/run.py": (("_gateway_ui", "gateway.runtime."),),
        "gateway/platforms/telegram.py": (("_tg_ui", "gateway.telegram."),),
        "gateway/platforms/feishu.py": (("_feishu_ui", "gateway.feishu."),),
        "hermes_cli/gateway.py": (("_ui", "gateway."),),
        "hermes_cli/auth.py": (("_ui", "auth."),),
        "hermes_cli/debug.py": (("_ui", "debug."),),
        "hermes_cli/main.py": (("_ui", "main."),),
        "hermes_cli/status.py": (("_ui", "status."),),
        "hermes_cli/banner.py": (("_ui", "banner."),),
    }
    keys = set()
    current_file = ""
    for line in patch_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("diff --git a/"):
            parts = line.split()
            current_file = parts[3][2:] if len(parts) >= 4 and parts[3].startswith("b/") else ""
            continue
        if not line.startswith("+") or line.startswith("+++"):
            continue
        added_line = line[1:]
        for helper, prefix in helper_prefixes.get(current_file, ()):
            pattern = rf"{re.escape(helper)}\(\s*[\"']([^\"']+)[\"']"
            for match in re.findall(pattern, added_line):
                keys.add(f"{prefix}{match}")
    return keys


def _ui_messages(ui_path: Path) -> set[str]:
    try:
        data = yaml.safe_load(ui_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise VerifyError(f"missing ui catalog: {ui_path}") from exc
    if not isinstance(data, dict):
        raise VerifyError(f"expected object yaml: {ui_path}")
    messages = data.get("messages")
    if not isinstance(messages, dict):
        raise VerifyError(f"expected messages object in: {ui_path}")
    return set(messages)


def _normalize_skill_slug(name: str) -> str:
    text = str(name or "").strip().lower().replace(" ", "-").replace("_", "-")
    text = re.sub(r"[^a-z0-9-]", "", text)
    text = re.sub(r"-{2,}", "-", text)
    return text.strip("-")


def _skills_catalog_keys(skills_path: Path) -> set[str]:
    try:
        data = yaml.safe_load(skills_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise VerifyError(f"missing skills catalog: {skills_path}") from exc
    if not isinstance(data, dict):
        raise VerifyError(f"expected object yaml: {skills_path}")
    skills = data.get("skills")
    if not isinstance(skills, dict):
        raise VerifyError(f"expected skills object in: {skills_path}")
    return {str(key).strip() for key in skills if str(key).strip()}


def _skill_name_from_frontmatter(skill_md: Path) -> str:
    content = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---(?:\s*\n|$)", content, re.DOTALL)
    if not match:
        return skill_md.parent.name
    frontmatter = yaml.safe_load(match.group(1)) or {}
    if not isinstance(frontmatter, dict):
        return skill_md.parent.name
    name = str(frontmatter.get("name") or "").strip()
    return name or skill_md.parent.name


def _installed_skill_entries(skills_dir: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for skill_md in sorted(skills_dir.rglob("SKILL.md")):
        if any(part in {".git", ".github", ".hub"} for part in skill_md.parts):
            continue
        name = _skill_name_from_frontmatter(skill_md)
        entries.append(
            {
                "name": name,
                "directory_name": skill_md.parent.name,
                "slug": _normalize_skill_slug(name),
            }
        )
    return entries


def _validate_installed_skill_localizations(*, repo_root: Path, skills_path: Path) -> None:
    skills_dir = repo_root.parent / "skills"
    if not skills_dir.exists():
        return
    catalog_keys = _skills_catalog_keys(skills_path)
    missing: list[str] = []
    for entry in _installed_skill_entries(skills_dir):
        candidates = {
            entry["slug"],
            entry["directory_name"],
            entry["directory_name"].lower(),
            _normalize_skill_slug(entry["name"]),
            entry["name"].strip(),
            entry["name"].strip().lower(),
        }
        if not any(candidate for candidate in candidates if candidate in catalog_keys):
            missing.append(entry["name"] or entry["directory_name"])
    if missing:
        raise VerifyError(
            "skills.zh-CN.yaml is missing installed skill descriptions: "
            + ", ".join(sorted(dict.fromkeys(missing)))
        )


def validate_release(repo_root: Path, release_id: str | None = None) -> dict:
    resolved_release, release_index, manifest = _load_metadata(repo_root, release_id)
    release_dir = repo_root / "releases" / resolved_release
    patch_path = release_dir / str(manifest.get("patch") or "")
    if not patch_path.exists():
        raise VerifyError(f"missing patch file: {patch_path}")

    localization_dir = release_dir / "localization"
    localization_files = []
    for name in manifest.get("localization_files", []):
        if str(name).endswith(".py"):
            raise VerifyError(f"localization_files must be read-only data, not python runtime: {name}")
        path = localization_dir / name
        if not path.exists():
            raise VerifyError(f"missing localization file: {path}")
        localization_files.append(str(path.relative_to(repo_root)))

    skins_dir = release_dir / "skins"
    skin_files = []
    for name in manifest.get("skin_files", []):
        path = skins_dir / name
        if not path.exists():
            raise VerifyError(f"missing skin file: {path}")
        skin_files.append(str(path.relative_to(repo_root)))

    patch_files = _patch_files(patch_path)
    allowed = list(manifest.get("allowed_source_files", []))
    if sorted(patch_files) != sorted(allowed):
        raise VerifyError(
            "patch file set does not match manifest allowed_source_files: "
            f"{sorted(patch_files)} != {sorted(allowed)}"
        )

    ui_path = localization_dir / "ui.zh-CN.yaml"
    missing_ui_keys = sorted(_ui_keys_from_patch(patch_path) - _ui_messages(ui_path))
    if missing_ui_keys:
        raise VerifyError(f"ui.zh-CN.yaml is missing runtime keys: {missing_ui_keys}")
    if "skills.zh-CN.yaml" in manifest.get("localization_files", []):
        _validate_installed_skill_localizations(
            repo_root=repo_root,
            skills_path=localization_dir / "skills.zh-CN.yaml",
        )

    return {
        "release": resolved_release,
        "official_repo": release_index.get("official_repo"),
        "official_commit": manifest.get("official_commit"),
        "patch_path": str(patch_path.relative_to(repo_root)),
        "patch_files": patch_files,
        "localization_files": localization_files,
        "skin_files": skin_files,
    }


def validate_local_source(*, repo_root: Path, source_dir: Path, release_id: str | None = None) -> dict:
    resolved_release, _, manifest = _load_metadata(repo_root, release_id)
    release_dir = repo_root / "releases" / resolved_release
    patch_path = release_dir / str(manifest.get("patch") or "")
    official_commit = str(manifest.get("official_commit") or "")
    if not official_commit:
        raise VerifyError("manifest does not define official_commit")

    head = _run(["git", "rev-parse", "HEAD"], cwd=source_dir)
    dirty = _changed_files(source_dir)
    allowed = sorted(manifest.get("allowed_source_files", []))

    if head != official_commit:
        raise VerifyError(f"source HEAD {head} does not match official_commit {official_commit}")
    if dirty != allowed:
        raise VerifyError(f"local dirty files {dirty} do not match allowed_source_files {allowed}")
    _run(["git", "apply", "--reverse", "--check", str(patch_path)], cwd=source_dir)

    return {
        "source_dir": str(source_dir),
        "head": head,
        "dirty_files": dirty,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a versioned Hermes Chinese release.")
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--release", default="")
    parser.add_argument("--source-dir", default="")
    args = parser.parse_args()

    try:
        result = {"release": validate_release(Path(args.repo_root), args.release or None)}
        if args.source_dir:
            result["local_source"] = validate_local_source(
                repo_root=Path(args.repo_root),
                source_dir=Path(args.source_dir).expanduser(),
                release_id=args.release or None,
            )
    except VerifyError as exc:
        print(f"[hermes-zh-release] {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

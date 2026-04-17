from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

import yaml

from hermes_constants import get_hermes_home

_DEFAULT_LOCALE = "zh-CN"
_SLUG_INVALID_CHARS = re.compile(r"[^a-z0-9-]")
_SLUG_MULTI_HYPHEN = re.compile(r"-{2,}")
_LOCALIZATION_CACHE: Dict[Path, tuple[int, Dict[str, Any]]] = {}


def _localization_dir() -> Path:
    return get_hermes_home() / "localization"


def _load_localization_yaml(path: Path) -> Dict[str, Any]:
    try:
        stat = path.stat()
    except OSError:
        return {}

    cached = _LOCALIZATION_CACHE.get(path)
    if cached and cached[0] == stat.st_mtime_ns:
        return cached[1]

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        raw = {}

    if not isinstance(raw, dict):
        raw = {}

    _LOCALIZATION_CACHE[path] = (stat.st_mtime_ns, raw)
    return raw


def _load_overlay(kind: str) -> Dict[str, Any]:
    return _load_localization_yaml(_localization_dir() / f"{kind}.{_DEFAULT_LOCALE}.yaml")


def _lookup_localized(mapping: Any, *keys: str | None) -> str:
    if not isinstance(mapping, dict):
        return ""
    for key in keys:
        if key is None:
            continue
        text = str(key).strip()
        if not text:
            continue
        if text in mapping:
            value = mapping[text]
            if isinstance(value, str) and value.strip():
                return value.strip()
        lowered = text.lower()
        if lowered in mapping:
            value = mapping[lowered]
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


def _lookup_localized_list(mapping: Any, *keys: str | None) -> List[str]:
    if not isinstance(mapping, dict):
        return []
    for key in keys:
        if key is None:
            continue
        text = str(key).strip()
        if not text:
            continue
        for candidate in (text, text.lower()):
            if candidate not in mapping:
                continue
            value = mapping[candidate]
            if isinstance(value, list):
                cleaned = [str(item).strip() for item in value if str(item).strip()]
                if cleaned:
                    return cleaned
    return []


def normalize_skill_slug(name: str) -> str:
    slug = str(name or "").strip().lower().replace(" ", "-").replace("_", "-")
    slug = _SLUG_INVALID_CHARS.sub("", slug)
    slug = _SLUG_MULTI_HYPHEN.sub("-", slug).strip("-")
    return slug


def get_command_description(command_name: str, default: str) -> str:
    commands = _load_overlay("commands").get("commands", {})
    return _lookup_localized(commands, command_name) or default


def get_command_meta(key: str, default: str) -> str:
    meta = _load_overlay("commands").get("meta", {})
    return _lookup_localized(meta, key) or default


def get_skill_description(
    *,
    name: str | None = None,
    slug: str | None = None,
    default: str = "",
) -> str:
    skills = _load_overlay("skills").get("skills", {})
    normalized = normalize_skill_slug(name or "") if name else ""
    return _lookup_localized(skills, slug, name, normalized) or default


def get_skill_meta(key: str, default: str) -> str:
    meta = _load_overlay("skills").get("meta", {})
    return _lookup_localized(meta, key) or default


def get_category_description(category: str, default: str = "") -> str:
    categories = _load_overlay("skills").get("categories", {})
    return _lookup_localized(categories, category) or default


def format_localized_text(template: str, **format_args: Any) -> str:
    if not format_args:
        return template
    try:
        return template.format(**format_args)
    except Exception:
        return template


def get_ui_text(key: str, default: str = "", **format_args: Any) -> str:
    messages = _load_overlay("ui").get("messages", {})
    template = _lookup_localized(messages, key) or default
    return format_localized_text(template, **format_args)


def get_skin_branding_text(skin_name: str, key: str, default: str = "") -> str:
    messages = _load_overlay("skins").get("skins", {})
    normalized_skin = str(skin_name or "").strip().lower()
    template = _lookup_localized(
        (messages.get(normalized_skin, {}) if isinstance(messages.get(normalized_skin), dict) else {}).get("branding", {}),
        key,
    ) or _lookup_localized(
        (messages.get("default", {}) if isinstance(messages.get("default"), dict) else {}).get("branding", {}),
        key,
    )
    return template or default


def get_skin_spinner_text(skin_name: str, key: str, default: List[str] | None = None) -> List[str]:
    messages = _load_overlay("skins").get("skins", {})
    normalized_skin = str(skin_name or "").strip().lower()
    exact_spinner = (messages.get(normalized_skin, {}) if isinstance(messages.get(normalized_skin), dict) else {}).get("spinner", {})
    default_spinner = (messages.get("default", {}) if isinstance(messages.get("default"), dict) else {}).get("spinner", {})
    template = _lookup_localized_list(exact_spinner, key) or _lookup_localized_list(default_spinner, key)
    if template:
        return template
    return list(default or [])


def localize_skin_branding(skin_name: str, branding: Dict[str, str]) -> Dict[str, str]:
    localized = dict(branding)
    for key, value in branding.items():
        localized[key] = get_skin_branding_text(skin_name, key, value)
    return localized


def localize_skin_spinner(skin_name: str, spinner: Dict[str, Any]) -> Dict[str, Any]:
    localized = dict(spinner)
    localized["thinking_verbs"] = get_skin_spinner_text(
        skin_name,
        "thinking_verbs",
        [str(item).strip() for item in spinner.get("thinking_verbs", []) if str(item).strip()],
    )
    return localized


def get_tip_corpus(defaults: List[str]) -> List[str]:
    data = _load_overlay("tips")

    localized = data.get("tips", [])
    if isinstance(localized, list):
        cleaned = [str(item).strip() for item in localized if str(item).strip()]
        if cleaned:
            return cleaned

    translations = data.get("translations", {})
    if isinstance(translations, dict):
        mapped = [_lookup_localized(translations, item) or item for item in defaults]
        cleaned = [str(item).strip() for item in mapped if str(item).strip()]
        if cleaned:
            return cleaned

    return defaults


def clear_localization_caches() -> None:
    _LOCALIZATION_CACHE.clear()

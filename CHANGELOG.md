# Changelog

## 0.3.0

- Upgrade the versioned Chinese package from official Hermes `31e72764` to `a828daa7`.
- Carry the minimal terminal and Telegram overlay forward to the new official baseline.
- Add localization coverage for newly introduced `/agents`, `/copy`, and `/steer` fixed replies and command descriptions.
- Replace several release-hardcoded tests with `latest_release` driven checks.
- Make `scripts/apply_release.py` invalidate stale `.update_check` caches so a fresh upgrade does not falsely report old "commits behind" counts.

## 0.2.0

- Replace the old unattended overlay system with versioned release assets.
- Add `releases/31e72764/` as the first minimal Hermes Chinese package.
- Add `scripts/apply_release.py` and `scripts/verify_release.py`.
- Limit scope to terminal and Telegram fixed UI text only.
- Stop handling Web UI.

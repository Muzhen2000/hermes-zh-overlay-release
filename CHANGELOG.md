# Changelog

## 0.5.2

- Publish `releases/fc8e4ebf-gateway1/` as the current latest release.
- Finish the remaining terminal gateway fixed-copy coverage for setup banners, service-status prompts, process/service mismatch warnings, and Telegram platform metadata.
- Add the missing banner toolset aliases for Discord, Feishu Docs, and Feishu Drive.
- Refresh the local localization-audit helper maps so `auth.py`, `debug.py`, and `main.py` are tracked under their current `_ui` entrypoints instead of stale helper names.

## 0.5.1

- Publish `releases/fc8e4ebf-feishu2/` as the current latest release.
- Fix the Feishu reaction regression by keeping provider protocol tokens (`Typing` / `CrossMark`) out of localization data.
- Add the remaining Feishu fixed-copy coverage for gateway platform setup metadata and QR onboarding prompts.
- Tighten the release policy so API enums, callback tokens, and other protocol identifiers are never treated as localizable UI text.

## 0.5.0

- Publish `releases/fc8e4ebf-feishu1/` as the current latest release.
- Expand the declared overlay scope from terminal + Telegram to terminal + Telegram + Feishu fixed UI text.
- Add Feishu / Lark setup-copy localization, approval-card labels, resolved-card text, fallback labels, summary prefixes, and reaction badges.
- Extend release verification and localization-audit tooling so Feishu UI hooks are tracked under the same release contract as terminal and Telegram.

## 0.4.0

- Upgrade the versioned Chinese package from official Hermes `6af04474` to `fc8e4ebf`.
- Publish `releases/fc8e4ebf-kimi1/` as the current latest release.
- Carry the minimal terminal and Telegram overlay forward to the new official baseline.
- Keep the declared small compatibility patches, including the Kimi `thinking` bridge and display-layer fixes.
- Refresh README and install docs so the public repo entry points match the current release.

## 0.3.1

- Publish `releases/6af04474-kimi1/` as a versioned follow-up to `6af04474`.
- Add the declared Moonshot/Kimi `thinking` compatibility patch and matching regression test to the overlay release.

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

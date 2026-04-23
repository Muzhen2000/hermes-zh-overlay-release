# Changelog

## 0.8.2

- Publish `releases/88b6eb9/` as the current latest release.
- Upgrade the versioned Chinese package from official Hermes `7f1c1aa4` to `88b6eb9a`.
- Keep the declared overlay scope at terminal + Telegram fixed visible text only.
- Reconfirm that the intervening upstream commits stay outside the 21 overlay-managed source files, so the release patch remains byte-identical while the official baseline advances.

## 0.8.1

- Publish `releases/7f1c1aa/` as the current latest release.
- Upgrade the versioned Chinese package from official Hermes `bf039a92` to `7f1c1aa4`.
- Keep the declared overlay scope at terminal + Telegram fixed visible text only.
- Re-export the release patch from the fresh `7f1c1aa4` official baseline after confirming the intervening upstream commits did not touch the overlay-managed source surface.

## 0.8.0

- Publish `releases/bf039a9/` as the current latest release.
- Upgrade the versioned Chinese package from official Hermes `eda5ae5a` to `bf039a92`.
- Keep the declared overlay scope at terminal + Telegram fixed visible text only.
- Regenerate the release from a fresh `bf039a92` official baseline instead of carrying forward any older localized worktree.

## 0.7.0

- Publish `releases/eda5ae5a/` as the current latest release.
- Upgrade the versioned Chinese package from official Hermes `ce98e1ef` to `eda5ae5a`.
- Shrink the declared overlay scope back to terminal + Telegram fixed visible text only.
- Rebuild the latest release from a clean `eda5ae5a` official baseline instead of carrying forward the older wider-scope release surface.
- Carry the existing terminal + Telegram overlay forward and add the newly required latest-upstream terminal copy coverage for gateway service status, hook-block feedback, debug log snapshot labels, and WeCom setup metadata shown in the terminal.

## 0.6.1

- Publish `releases/ce98e1ef-gateway2/` as the current latest release.
- Remove the private Moonshot/Kimi `thinking` compatibility patch and return Kimi routing to the official `ce98e1ef` source behavior.
- Keep the same legacy wider fixed-text overlay surface while regenerating the patch from the official baseline instead of carrying forward obsolete Kimi runtime drift.

## 0.6.0

- Upgrade the versioned Chinese package from official Hermes `fc8e4ebf` to `ce98e1ef`.
- Publish `releases/ce98e1ef-gateway1/` as the previous release on this baseline.
- Rebase the existing legacy wider minimal overlay onto the latest official baseline through a clean official checkout, instead of stacking new patch-on-patch drift.
- Carry forward the declared display-only compatibility hooks, including CJK spinner row handling, display-only skill preview summarization, and the Kimi `thinking` bridge.
- Add the newly required gateway usage localization keys and adapt numbered clarify-panel “Other” rows to the latest upstream terminal layout.

## 0.5.4

- Publish `releases/fc8e4ebf-gateway2/` as the current latest release.
- Roll back the experimental skill slash-command description localization and the related skill-specific release gate, restoring the `gateway1` behavior on top of the same official `fc8e4ebf` baseline.
- Keep `scripts/apply_release.py` from pruning `~/.hermes/localization/reports/`, so localization audit baselines survive real release applies.
- Add regression coverage proving release verification does not depend on the current machine's installed skill set.

## 0.5.3

- Publish `releases/fc8e4ebf-skilldesc1/` as the current latest release.
- Route dynamic skill slash-command descriptions through `skills.zh-CN.yaml` when a localized entry exists, so terminal help, completion annotations, and gateway skill menus stop mixing Chinese and English.
- Add a regression test for localized skill command descriptions.

## 0.5.2

- Publish `releases/fc8e4ebf-gateway1/` as the current latest release.
- Finish the remaining terminal gateway fixed-copy coverage for setup banners, service-status prompts, process/service mismatch warnings, and Telegram platform metadata.
- Add the missing banner toolset aliases for Discord plus the extra docs/drive services that were still present in the legacy wider scope.
- Refresh the local localization-audit helper maps so `auth.py`, `debug.py`, and `main.py` are tracked under their current `_ui` entrypoints instead of stale helper names.

## 0.5.1

- Publish the second legacy wider-scope follow-up release on `fc8e4ebf`.
- Fix the legacy wider-scope reaction regression by keeping provider protocol tokens (`Typing` / `CrossMark`) out of localization data.
- Add the remaining legacy wider-scope fixed-copy coverage for gateway platform setup metadata and QR onboarding prompts.
- Tighten the release policy so API enums, callback tokens, and other protocol identifiers are never treated as localizable UI text.

## 0.5.0

- Publish the first legacy wider-scope follow-up release on `fc8e4ebf`.
- Expand the then-declared overlay scope from terminal + Telegram to a temporary wider fixed-UI surface.
- Add that temporary wider-scope setup copy, approval-card labels, resolved-card text, fallback labels, summary prefixes, and reaction badges.
- Extend release verification and localization-audit tooling so the temporary wider-scope UI hooks are tracked under the same release contract as terminal and Telegram.

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

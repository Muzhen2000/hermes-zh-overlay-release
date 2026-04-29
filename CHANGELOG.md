# Changelog

## 1.1.1
- Complete command localization coverage for the current 58-command registry: add `busy`, `curator`, `footer`, `indicator`, and `redraw`; remove obsolete `btw` and `provider` entries.

- Prune the previous `e5647d78-terminal-discord1` release directory so the public repo again exposes only the current verified release.
- Update the pinned install command in `docs/install.md` to `58a6171b-terminal-discord1`.
- Clarify historical audit docs so old release IDs are audit-time baselines, not current entry points.
- Separate non-disruptive verification commands from optional gateway restart checks in the Discord proxy audit.

## 1.1.0

- Publish `releases/58a6171b-terminal-discord1/` as the current latest release.
- Bind the package to official Hermes `58a6171bfb0ba2ca10b1b08854511736cd77a623`.
- Re-export the terminal/Discord Chinese display patch from a clean official baseline after upstream changed CLI and gateway files.
- Preserve the declared Discord proxy target-host exception and keep it limited to existing `NO_PROXY` handling.
- Drop stale private `/btw` overlay bodies during conflict resolution and keep the newer upstream command/session behavior.

## 1.0.1

- Re-export `releases/e5647d78-terminal-discord1/patches/hermes-zh.patch` from the same official Hermes baseline after adding one declared Discord gateway stability exception.
- Add Discord target hosts to existing Hermes proxy resolution call sites so profile-scoped `NO_PROXY` can bypass a broken macOS system proxy for permanent Discord gateways.
- Keep the exception narrow: no message routing, command dispatch, session state, auth semantics, model prompts, or Discord protocol identifiers are changed.
- Document the no-source alternatives that were audited and rejected: relying only on `.env` `NO_PROXY`, macOS proxy bypass domains, empty `DISCORD_PROXY`, or a permanently healthy local proxy.
- Update README, AGENTS, manifest metadata, and maintenance skill guidance so future agents treat the proxy patch as a declared removable exception, not hidden runtime drift.

## 1.0.0

- Publish `releases/e5647d78-terminal-discord1/` as the current latest release.
- Bind the package to official Hermes `e5647d7863d306c8f479e1da011ebe4a4848d56d`.
- Keep the declared scope at terminal + Discord fixed visible text only; Telegram and Feishu platform runtime patches are out of scope.
- Restore full terminal fixed-copy coverage: startup, command help, command replies, state/rollback/snapshot/model/reasoning/update/gateway messages, loading states, status bar, and all bundled skin text.
- Add Discord fixed-copy coverage for slash command descriptions, argument descriptions, command replies, approval/update cards, model picker labels, thread messages, and dynamic commands generated from `hermes_cli.commands`.
- Keep source changes limited to display-layer hooks and CJK terminal display adaptation; no model-facing prompts, command values, custom IDs, provider protocol fields, or runtime routing are localized.
- Prune historical release directories from the repository so future agents use only the current verified release as the baseline.
- Add the 2026-04-25 audit report and refresh README, install docs, AGENTS, and guardrail skill guidance.

## 0.9.0

- Publish `releases/023b1bff-discord1/` as the current latest release.
- Upgrade the versioned Chinese package from official Hermes `6fdbf2f2` to `023b1bff`.
- Change the active declared scope from terminal + Telegram to terminal + Discord.
- Restore Hermes to official source-only mode for this release: `manifest.patch` is empty and `allowed_source_files` is `[]`.
- Teach `scripts/apply_release.py` and `scripts/verify_release.py` to handle no-patch releases, so official Hermes source can stay at zero diff.

## 0.8.5

- Publish `releases/6fdbf2f2/` as the current latest release.
- Upgrade the versioned Chinese package from official Hermes `91d6ea07` to `6fdbf2f2`.
- Re-export the release from a fresh `6fdbf2f2` official baseline after absorbing upstream gateway CLI changes.
- Add visible progress output to `scripts/apply_release.py` so the two-line install flow no longer appears idle during network and git operations.

## 0.8.4

- Publish `releases/91d6ea07/` as the current latest release.
- Upgrade the versioned Chinese package from official Hermes `627abbb1` to `91d6ea07`.
- Keep the declared overlay scope at terminal + Telegram fixed visible text only.
- Pure-forward the release after confirming the intervening upstream commits only touched dev-tooling files outside the 21 overlay-managed paths, leaving the release patch byte-identical.

## 0.8.3

- Publish `releases/627abbb1/` as the current latest release.
- Upgrade the versioned Chinese package from official Hermes `88b6eb9a` to `627abbb1`.
- Keep the declared overlay scope at terminal + Telegram fixed visible text only.
- Re-export the release from a fresh `627abbb1` official baseline after absorbing upstream changes in `gateway/run.py` and the prompt-builder test suite.

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

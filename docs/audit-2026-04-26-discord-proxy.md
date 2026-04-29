# 2026-04-26 Discord Proxy Stability Audit

## Scope

Baseline:

- Official Hermes commit: `e5647d7863d306c8f479e1da011ebe4a4848d56d`
- Active release: `e5647d78-terminal-discord1`
- Managed surface: terminal + Discord fixed visible text, plus the single runtime exception declared below

This audit covers only the extra Discord gateway proxy change added after the 2026-04-25 localization audit.

## Symptom

Default and named Hermes profiles were running under launchd, but Discord messages were not reliably delivered. Logs showed Discord requests going through macOS system proxy ports such as `127.0.0.1:7890` or `127.0.0.1:7897`; direct Discord API connectivity worked.

The user requirement is stronger than a one-time manual recovery:

- default Hermes gateway must be permanently running
- each named profile gateway must be permanently running
- each profile owns one Discord channel
- a broken local proxy must not silently make a profile stop replying

## Root Cause

Hermes already has proxy bypass logic in `gateway/platforms/base.py`:

- `resolve_proxy_url(..., target_hosts=...)`
- `should_bypass_proxy(target_hosts)`
- `NO_PROXY` / `no_proxy` matching

However, the Discord adapter called `resolve_proxy_url(platform_env_var="DISCORD_PROXY")` without `target_hosts`. In that shape, `should_bypass_proxy()` returns false because it has no host to compare against `NO_PROXY`.

Result: profile-scoped `NO_PROXY=discord.com,.discord.com,discord.gg,.discord.gg` was present but inert for Discord.

## No-Source Alternatives Audited

1. Profile `.env` only:
   `NO_PROXY=discord.com,.discord.com,discord.gg,.discord.gg`
   Rejected as sufficient by itself because the Discord call sites did not pass target hosts into the existing bypass logic.

2. macOS proxy bypass domains:
   Not sufficient for Hermes because `_detect_macos_system_proxy()` only reads enabled proxy host/port from `scutil --proxy` and does not apply macOS `ExceptionsList` itself.

3. Empty `DISCORD_PROXY`:
   Not sufficient because empty values are ignored, then Hermes falls through to generic proxy env vars and macOS system proxy detection.

4. Force a working local proxy:
   Operationally possible, but it makes Hermes gateway reliability depend on an unrelated GUI proxy process. That does not satisfy permanent gateway operation.

5. Disable macOS system proxy globally:
   Possible but too broad. It changes the whole computer's network behavior to fix one Discord gateway path.

Conclusion: current Hermes has no clean profile-level configuration knob for "Discord direct, bypass detected macOS proxy" unless the Discord adapter supplies target hosts to the already-existing `NO_PROXY` logic.

## Source Change

File:

- `gateway/platforms/discord.py`

Patch shape:

- Add `_DISCORD_PROXY_TARGET_HOSTS = ("discord.com", "discord.gg", "gateway.discord.gg")`.
- Pass `target_hosts=_DISCORD_PROXY_TARGET_HOSTS` to all Discord `resolve_proxy_url()` call sites.

Locations:

- Discord bot/client connection
- outbound image download
- outbound animation download
- Discord REST command fetch helper

## Boundary Review

This patch touches runtime code, so it is not a localization change. It is allowed only as a declared runtime stability exception.

It does not change:

- Discord message routing
- channel allowlist semantics
- thread/no-thread behavior
- command names
- command choices
- custom IDs
- auth checks
- session state
- model request payloads
- model-facing prompts
- generated user-facing LLM content

It only makes existing `NO_PROXY` configuration effective for Discord.

## Removal Condition

Remove this exception when upstream Hermes does either of these:

- passes Discord target hosts into `resolve_proxy_url()`, or
- provides an official per-platform direct/no-proxy configuration option.

Until then, this patch should stay in the overlay release because it protects the user's permanent Discord multi-instance topology from local proxy outages.

## Verification

Expected checks:

```bash
python3 ~/.hermes/hermes-zh-overlay-release/scripts/verify_release.py --source-dir ~/.hermes/hermes-agent
git -C ~/.hermes/hermes-agent diff --check
launchctl kickstart -k gui/$(id -u)/ai.hermes.gateway
launchctl kickstart -k gui/$(id -u)/ai.hermes.gateway-contemplation
```

Expected gateway evidence:

- `gateway_state.json` reports Discord `connected`.
- Logs show `Connected as ...` after restart.
- New restart logs do not show `Using proxy for Discord` when profile `NO_PROXY` matches Discord hosts.


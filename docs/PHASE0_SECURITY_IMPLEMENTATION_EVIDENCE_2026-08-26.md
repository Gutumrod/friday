# Friday Phase 0 — Security & Machine-Specific Config Cleanup Evidence

Date: 2026-08-26
Repo: `Gutumrod/friday`
Branch: `master`
Status: **IMPLEMENTED — LIVE WINDOWS/TV REGRESSION PENDING**

## Scope Completed

1. Removed the paired LG webOS client key from current source.
2. Removed current LG TV IP/MAC/broadcast values from source defaults.
3. Removed the workstation-specific Google Cloud credentials path default.
4. Added environment-based runtime configuration for:
   - `GOOGLE_CLOUD_CREDS_PATH`
   - `FRIDAY_DEVICE_INDEX`
   - `FRIDAY_CAMERA_INDEX`
   - `FRIDAY_TV_IP`
   - `FRIDAY_TV_MAC`
   - `FRIDAY_TV_CLIENT_KEY`
   - `FRIDAY_TV_BROADCAST_IP`
   - `FRIDAY_TV_CONNECT_TIMEOUT`
   - `FRIDAY_TV_BOOT_WAIT`
5. Added safe value-free configuration diagnostics.
6. Added fail-closed runtime guards for all five LG TV side-effect tools when TV config is missing/invalid.
7. Added a guarded ASGI entrypoint for the Friday API and changed `run_friday_api.bat` to use it.
8. Updated the voice launcher to apply the same runtime guards before starting the voice loop.
9. Updated `.env.example` with placeholders only; `.env` remains ignored by git.
10. Added `src/test_phase0_security.py`, a stdlib-only Phase 0 regression script.

## Security Finding Resolved In Current Source

The public repository previously contained a paired LG webOS client key directly in `src/friday/config.py`.

Current source now reads it only from `FRIDAY_TV_CLIENT_KEY` in process environment / `.env`.

Important: removing a secret from the current tree does **not** remove it from public Git history. Treat the old paired key as exposed. Re-pair/rotate the TV key before restoring TV control locally. Do not reuse the historical key.

## Runtime Safety Behavior

Supported launch paths now fail closed for TV control when configuration is missing or invalid:

- Voice: `src/friday_walkie_talkie.py` -> `apply_runtime_security(core)` -> `core.main()`
- API: `run_friday_api.bat` -> `friday.api_launcher:app` -> `apply_runtime_security(core)` -> `friday.api:app`

When TV config is invalid, these tool executors are replaced with a non-side-effect unavailable response:

- `tv_power`
- `tv_volume`
- `tv_launch_app`
- `tv_play_video`
- `tv_remote_button`

The Confirm Gate remains in place. No side-effect tool is ungated by this phase.

## Safe Diagnostics

Configuration diagnostics expose variable names only. They do not echo:

- paired client key
- credential contents
- token values

Invalid numeric config raises a clear variable-name-only error.

## Test Coverage Added

`python src/test_phase0_security.py`

Checks:

1. TV client key has no quoted source default.
2. Google Cloud credentials path is machine-local.
3. `.env` remains ignored and `.env.example` contains placeholder-only TV key configuration.
4. diagnostics never echo a secret marker.
5. missing TV config disables all five TV side-effect executors.
6. Confirm Gate executors also fail closed.
7. valid TV config leaves original TV tools untouched.

An isolated syntax/guard-logic check was completed successfully while preparing this change.

## Commits

- `4c8d909` — move Friday device secrets/config to env
- `186474f` — add machine-local config placeholders
- `1e2f917` — add fail-closed runtime integration guards
- `fe875a7` — guard Friday voice runtime config
- `f3c8214` — add guarded Friday API entrypoint
- `eab0df2` — launch Friday API through runtime guards
- `7f66634` — add Phase 0 security regression checks

## Live Verification Still Required

Both registered development devices were offline during implementation, so the following must be rerun on the Windows Friday machine before Gate 0 can be marked PASS:

1. Pull latest `master`.
2. Create/update local `.env` from `.env.example` without committing it.
3. Re-pair LG webOS TV and put the newly issued client key in `FRIDAY_TV_CLIENT_KEY`.
4. Put current TV IP/MAC/broadcast values in `.env`.
5. Run:
   - `python src/test_phase0_security.py`
   - `python src/test_tools.py`
6. Start Friday through `run_friday.bat` and verify startup warnings contain no secret values.
7. Live TV regression:
   - power on
   - power off
   - volume up/down/mute
   - launch YouTube
   - remote button
8. Start API through `run_friday_api.bat` and verify `/api/status`, `/api/tools`, and gated TV flow still work.

## Gate Verdict

**Code-side remediation: COMPLETE**

**Gate 0: PENDING LIVE REGRESSION**

Do not start Phase 1 STT provider implementation until the live Windows/security/TV regression above passes and the owner approves moving on.

## Live Verification Update — 2026-08-28

Windows target machine is online and the pending Hermes redaction defect was retested.

Results:
- `python -m py_compile src/friday/hermes_client.py src/friday/core.py` — PASS
- `python src/test_phase0_security.py` — **5/5 PASS**
- `python src/test_tools.py hermes_shadow` — Hermes URL/Bearer redaction now PASS
- full self-check completed **79/80 PASS**
- only remaining full-suite failure is the pre-existing JaiTTS/Hugging Face runtime 401; it is not a Phase 0 security regression

The validated redaction fix now bounds URL-token matching at URL/text delimiters and removes the complete Bearer credential rather than leaving the original token after a marker.

Gate 0 remains **PENDING** until the historical LG paired key is rotated/re-paired and the final live TV/API regression is completed with the replacement key.

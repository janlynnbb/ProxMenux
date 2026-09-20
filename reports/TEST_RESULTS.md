# zh-CN localization validation results

Baseline: official `MacRimi/ProxMenux` Stable `v1.2.6`, commit `5b41cbfbe8bddcb7e2f1a597812765255fdba448` (tag verified 2026-09-20). The current official default branch was also inspected at `33c8ff5e7ef81cab4d923107ac7c63a04bf3d837`; it has no newer Stable tag.

| Check | Result | Notes |
| --- | --- | --- |
| JSON/key/placeholder audit | PASS | Monitor: 4,126 source keys and 4,126 zh-CN keys. CLI/TUI: 5,350 source keys and 114 curated zh-CN keys; the remaining 5,236 CLI/TUI strings intentionally use the built-in English fallback. No extra keys, unexpected blank values or placeholder mismatches. |
| Shell syntax | PASS | `bash -n install_proxmenux.sh install_proxmenux_beta.sh scripts/menus/config_menu.sh` |
| Patch whitespace | PASS | `git diff --check` |
| Monitor production build | PASS | `npm ci --legacy-peer-deps && npm run build` in `AppImage/`; Next.js compiled, generated static pages and exported successfully. |
| Static output content | PASS | The generated Next.js chunk contains `Proxmox 系统仪表板` and `正在加载`. |
| Direct full TypeScript check | BLOCKED (upstream) | `npx tsc --noEmit` reports pre-existing v1.2.6 errors across SWR generic types, missing icon modules and Monitor component models. Next.js's own project build skips type validation and still passes. No error references the zh-CN language registration or message catalog. |
| Live PVE/Monitor service | Not run | This isolated environment intentionally has no Proxmox VE host, PVE APIs, systemd service installation or hardware passthrough access. |

## What was not changed

- No user PVE, virtual machine, LXC, storage, network or external system was contacted or modified.
- English message keys remain the source of truth.
- Existing non-English catalogs were not rewritten.
- Hard-coded shell strings were not mass-refactored; their review list is in `zh-CN-uncovered-hardcoded-strings.md`.
- The CLI/TUI catalog is intentionally partial in this revision. Missing keys are visible in `zh-CN-validation.json` and safely fall back to English; no Spanish values are retained in `lang/zh-CN.json`.

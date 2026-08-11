# Platform Routing (shared)

Canonical platform detection and validation routing for Proofpunk skills.
Consolidated from `functional-validation`, `e2e-validate`,
`ios-validation-runner`, and `validate-phase`.

**Preflight first:** before routing to any validation path below, run the
environment/toolchain pass in `preflight-checks.md` — a missing simulator
runtime, an absent `node_modules`, or a wrong JDK turns every downstream
verdict into an environment failure, not a product verdict.

## Detection

| Indicator | Platform | Validation path |
|-----------|----------|-----------------|
| `.xcodeproj`, `Package.swift`, SwiftUI, `simctl` | iOS/macOS | Simulator automation + screenshot evidence |
| `package.json` with next/react/vite, HTML/CSS, Playwright | Web | Browser automation + screenshots + API checks |
| `pubspec.yaml`, Flutter | Flutter | `flutter run` + device screenshots |
| React Native, Expo | Cross-platform mobile | BOTH iOS and Web checklists apply |
| `Dockerfile`, `docker-compose.yml`, OpenAPI spec, `/health` route | API / backend | `curl -i` against live endpoints |
| CLI entry point, `argparse`/`commander`/Click | CLI | Run the real binary, capture stdout/stderr/exit code |
| Mixed web + API + mobile | Full-stack | Validate each surface AND the integrations between them |
| None of the above | Generic | Identify the real user interface (command, page, endpoint) and exercise it |

## Runtime Startup

| Platform | Start | Health check |
|----------|-------|--------------|
| Next.js / web dev server | `pnpm dev` / `npm run dev` in background | wait for `Ready in` / poll the URL |
| iOS | `xcrun simctl boot <UDID>`, build, install | app launches without crash |
| API | `npm start` / `python app.py` in background | `curl -sf http://localhost:$PORT/health` |
| CLI | none — runs synchronously | `--help` or `--version` exits 0 |
| Flutter | `flutter run -d <device>` | first frame rendered |

If the target fails to start: BLOCK. Report the startup error. Do not proceed
and do not simulate the run.

## Evidence Capture per Platform

| Platform | Execute | Capture |
|----------|---------|---------|
| Web | Playwright / browser DevTools: navigate, click, fill | screenshot per state, console log, network responses |
| iOS | `xcrun simctl` + `idb`: launch, tap, type, deep-link | sequential screenshots, `log stream` output, video |
| API | `curl -i` (headers + body) | full response files |
| CLI | `command >stdout.txt 2>stderr.txt; echo $?` | stdout, stderr, exit code |

## iOS-Specific Traps (from ios-validation-runner)

- Boot the simulator FIRST — screenshots during boot are black.
- Override the status bar (`simctl status_bar ... override --time "9:41"`)
  BEFORE screenshots for reproducible captures.
- Stop video with `kill -SIGINT` then `wait` — `kill -9` produces a corrupt
  MOV with no container footer.
- `log stream` needs `--info --debug` or Info/Debug messages are silently
  dropped; run `log show --last 120s` afterwards as belt-and-suspenders.
- Deep-link UUIDs must be lowercase; app must be foregrounded.
- Allow >= 3s settle time after launch and after navigation actions.
- Check `~/Library/Logs/DiagnosticReports/*.ips` for crash reports.

## Web-Specific Traps

- Clear build caches before the final pass (see evidence-contract).
- Capture empty / loading / populated / error states, not only happy path.
- Capture light AND dark mode; mobile AND desktop viewports.
- A `200` from a cached service worker is not evidence of a healthy backend.

## Full-Stack Rule

Validating each surface separately is necessary but not sufficient: exercise
at least one journey that crosses every boundary (UI -> API -> DB -> UI).

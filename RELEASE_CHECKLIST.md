# CleanVedio Release Checklist

Use this checklist before sharing a release with friends.

## 1) Build and Bundle

- Run `.\build_windows.ps1 -Clean` successfully.
- Verify artifact exists: `dist\CleanVedio.exe`.
- Run portable build:
  - Full: `.\make_portable_bundle.ps1 -BundleMode full`
  - or Lean: `.\make_portable_bundle.ps1 -BundleMode lean -EmRoot "..."`
- Confirm `portable\CleanVedioPortable\Run_CleanVedio.bat` exists.
- Confirm `PORTABLE_README.txt` shows runtime checks as `True` for chosen mode.

## 2) First-Run Experience

- Launch `Run_CleanVedio.bat`.
- Browser opens automatically (or manual `http://127.0.0.1:8787` works).
- Home page renders with no raw/debug errors.
- Process form uses friendly labels and no blocking JS alerts.

## 3) Core Processing

- Local file job completes successfully.
- YouTube job completes successfully.
- Progress panel updates stage, elapsed, and completion actions.
- "Open Output Folder" button works after completion.
- Processed video appears in `/final`.

## 4) Gallery Usability

- `Processed Videos` page lists expected videos.
- Thumbnail click starts playback.
- Download button saves file correctly.
- Delete flow requires confirmation and removes card on success.

## 5) Runtime Safety

- App binds to localhost by default.
- If `8787` is busy, app chooses a nearby available port.
- Logs and jobs are created under `%LOCALAPPDATA%\CleanVedio` (or configured `CLEANVEDIO_DATA_DIR`).

## 6) Diagnostics and Support

- `GET /health` returns valid status payload.
- `GET /diagnostics` returns counts and latest failures.
- `.\tail.ps1` reads logs.
- `.\export_support_bundle.ps1` generates a zip bundle.

## 7) Restart / Recovery

- `.\server.bat stop` cleanly stops the app.
- `.\server.bat start` starts it again.
- Failed jobs can be retried from the UI.

## 8) Final Packaging

- Zip entire `portable\CleanVedioPortable` folder.
- Include simple sharing note:
  - "Unzip and run `Run_CleanVedio.bat`."
  - "If browser does not open, go to `http://127.0.0.1:8787`."

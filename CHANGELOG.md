# Dead Air Remover — Changelog

## v1.4.5 (2026-07-13) — Theme + Polish
🧪 **Dark/Light Theme Toggle**
- 🌙/☀️ button in top nav
- `:root[data-theme="light"]` overrides CSS variables
- Auto-persist in localStorage (`dar_theme_v1`)
- 0.25s transition, color-scheme adapts scrollbar/inputs

## v1.4.4 (2026-07-13) — Performance
⚡ **Parallel audio decode** in `applyToAll`
- Audio files decode via `Promise.all` (no shared resources)
- Video files still sequential (need own video element)
- New `test_perf.py` for benchmarks

## v1.4.3 (2026-07-13) — Video Multi-File
🎬 **Video files in Export All**
- Exports audio-only WAV with `_audio` suffix
- Toast hints ffmpeg mux command for full video
- v1.4.3.1 hotfix: extra `}` in exportAll

## v1.4.2 (2026-07-13) — Progress
⏱️ **Progress bar in Apply to All**
- Reuses `setExporting()` pattern
- "Decoding N/M…" → "Analyzing N/M · filename"
- 10ms yield to UI per file

## v1.4.1 (2026-07-13) — Project Save
💾 **Project preset (vs Settings preset)**
- Save settings + file list as a named project
- 📁 icon prefix in dropdown
- Re-use for batch jobs (re-upload + apply)

## v1.4.0 (2026-07-13) — Drag-Drop
🔀 **Drag-drop files onto Tab Bar**
- Orange dashed border + glow on dragover
- Document-level preventDefault (no browser navigation)
- Tab bar accepts multiple files

## v1.3.3 (2026-07-13) — Tab Badges
📊 **Segment count badges on tabs**
- Green = decoded, Orange pulse = pending, Red = error

## v1.3.2 (2026-07-13) — Reset Badge
🔢 **File count badge on reset button**
- Animated scale-in orange badge
- Tooltip: "Replace all files · N file(s)"

## v1.3.1 (2026-07-13) — Close Confirm
🗑️ **Confirm before closing file**
- `confirm()` dialog with TH/EN messages
- Warning if file has `processedBuffer`

## v1.3 (2026-07-13) — Multi-File
- File tabs (queue-based state.files[])
- Apply to All (decode pending → analyze all)
- Export All (batch download with 80ms delay)
- Switch tab saves state first

## v1.1 (2026-07-12) — 10 Features
1. Drag-drop upload
2. Visual silence marker (green/red waveform)
3. Click-to-toggle segments
4. A/B auto-switch (5s interval)
5. 3 presets (Podcast/Video/Interview)
6. Adaptive threshold (noise floor calc)
7. Save custom preset
8. Real-time preview
9. Stats panel (time saved, segments)
10. 3-language UI (TH/EN/??)

## v1.0 (2026-07-12) — MVP
- Audio decode (Web Audio API)
- Threshold + min-silence + padding
- Export WAV (16-bit PCM)
- Single-file UI

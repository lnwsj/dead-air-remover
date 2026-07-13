#!/usr/bin/env python3
"""v1.4.4 perf test: 10 audio files decoded in parallel + applyToAll"""
import asyncio, sys, os, time
from playwright.async_api import async_playwright

URL = "http://localhost:8771/index.html"
TEST_DIR = "/tmp/dar-perf"
N = 10

async def main():
    os.makedirs(TEST_DIR, exist_ok=True)
    # Generate 10 small WAV files
    import struct, math
    for i in range(N):
        path = f"{TEST_DIR}/perf_{i}.wav"
        sr, dur = 22050, 4
        data = []
        for j in range(sr * dur):
            t = j / sr
            # 0.5s silence + 0.5s speech + 0.5s silence pattern
            phase = int(t * 2) % 2
            val = 0.85 * math.sin(2*math.pi*440*t) if phase == 1 else 0
            data.append(int(val * 32767))
        with open(path, 'wb') as f:
            n = len(data)
            f.write(b'RIFF')
            f.write(struct.pack('<I', 36 + n*2))
            f.write(b'WAVE')
            f.write(b'fmt ')
            f.write(struct.pack('<I', 16))
            f.write(struct.pack('<H', 1))
            f.write(struct.pack('<H', 1))
            f.write(struct.pack('<I', sr))
            f.write(struct.pack('<I', sr*2))
            f.write(struct.pack('<H', 2))
            f.write(struct.pack('<H', 16))
            f.write(b'data')
            f.write(struct.pack('<I', n*2))
            for v in data:
                f.write(struct.pack('<h', v))
    files = [f"{TEST_DIR}/perf_{i}.wav" for i in range(N)]
    print(f"✓ Generated {N} test files ({os.path.getsize(files[0])} bytes each)")

    errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            executable_path="/root/.cache/ms-playwright/chromium-1223/chrome-linux/chrome",
            args=["--no-sandbox", "--disable-gpu", "--use-gl=swiftshader"]
        )
        ctx = await browser.new_context(viewport={"width": 1440, "height": 1100}, accept_downloads=True)
        page = await ctx.new_page()
        page.on("pageerror", lambda e: errors.append(f"PAGE: {e}"))
        page.on("console", lambda m: errors.append(f"CONSOLE.{m.type}: {m.text}") if m.type == "error" else None)
        await page.goto(URL, wait_until="networkidle")
        await page.wait_for_timeout(1500)

        # Upload 10 files
        await page.set_input_files('#fileInput', files)
        # Wait for all to decode (status decoded)
        print(f"⏳ Waiting for all {N} files to decode...")
        t0 = time.time()
        all_decoded = False
        for attempt in range(60):  # 30s max
            decoded = await page.evaluate("state.files.filter(f => f.status === 'decoded').length")
            if decoded >= N:
                all_decoded = True
                break
            await page.wait_for_timeout(500)
        dt = (time.time() - t0) * 1000
        if not all_decoded:
            print(f"✗ Timeout: only {decoded}/{N} decoded after 30s")
            await browser.close()
            return False
        print(f"✓ All {N} files decoded in {dt:.0f}ms (avg {dt/N:.0f}ms/file)")

        # Test applyToAll performance
        t0 = time.time()
        await page.click('#applyToAllBtn')
        # Wait for all to have processedBuffer
        for attempt in range(60):
            processed = await page.evaluate("state.files.filter(f => f.processedBuffer).length")
            if processed >= N:
                break
            await page.wait_for_timeout(500)
        dt = (time.time() - t0) * 1000
        print(f"✓ Apply to All done in {dt:.0f}ms (avg {dt/N:.0f}ms/file)")

        # Verify each file has segments
        segments_per_file = await page.evaluate("state.files.map(f => f.segments.length)")
        print(f"✓ Segments per file: {segments_per_file}")
        total_segs = sum(segments_per_file)
        if total_segs == 0:
            print(f"✗ No segments detected!")
            await browser.close()
            return False

        # Test exportAll (downloads only, fast)
        downloads = []
        page.on("download", lambda d: downloads.append(d.suggested_filename))
        t0 = time.time()
        await page.click('#exportBtn')
        await page.wait_for_timeout(200)
        await page.click('#exportAll')
        await page.wait_for_timeout(N * 200 + 1000)
        dt = (time.time() - t0) * 1000
        print(f"✓ Export All done in {dt:.0f}ms · downloads: {len(downloads)}")

        await browser.close()
    print(f"\n--- Errors: {len(errors)} ---")
    for e in errors[:5]:
        print(f"  {e}")
    return len(errors) == 0

if __name__ == "__main__":
    ok = asyncio.run(main())
    sys.exit(0 if ok else 1)

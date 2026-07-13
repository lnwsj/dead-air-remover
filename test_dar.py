import asyncio
from playwright.async_api import async_playwright

CHROME = "/root/.cache/ms-playwright/chromium-1223/chrome-linux/chrome"
URL = "http://127.0.0.1:8765/"

async def main():
    errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=CHROME,
            headless=True,
            args=["--no-sandbox","--disable-gpu","--use-gl=swiftshader","--enable-webgl","--autoplay-policy=no-user-gesture-required"]
        )
        ctx = await browser.new_context(viewport={"width":1400,"height":900})
        page = await ctx.new_page()
        page.on("console", lambda msg: errors.append(f"[{msg.type}] {msg.text}") if msg.type in ("error","warning") else None)
        page.on("pageerror", lambda e: errors.append(f"[PAGEERROR] {e}"))
        await page.goto(URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(2500)

        editor_visible = await page.is_visible("#editor.show")
        print(f"Editor visible: {editor_visible}")
        await page.screenshot(path="/workspace/dar-1-initial.png", full_page=True)

        orig_dur = await page.text_content("#statOrig")
        new_dur = await page.text_content("#statNew")
        saved = await page.text_content("#statSaved")
        segs = await page.text_content("#segCount")
        print(f"Original: {orig_dur}  New: {new_dur}  Saved: {saved}  Segments: {segs}")

        keep_count = await page.eval_on_selector_all(".seg-item .tag.k", "els => els.length")
        cut_count = await page.eval_on_selector_all(".seg-item .tag.s", "els => els.length")
        print(f"Keep tags: {keep_count}  Cut tags: {cut_count}")

        await page.click("#procPlay")
        await page.wait_for_timeout(500)
        proc_playing = await page.text_content("#procPlay")
        print(f"Proc play btn text: {proc_playing}")
        await page.click("#procPlay")
        await page.wait_for_timeout(200)

        await page.eval_on_selector("#threshold", "el => { el.value = -30; el.dispatchEvent(new Event('input')); }")
        await page.wait_for_timeout(300)
        thr_val = await page.text_content("#thresholdVal")
        new_dur2 = await page.text_content("#statNew")
        print(f"After thr=-30: {thr_val}, new={new_dur2}")
        await page.screenshot(path="/workspace/dar-2-thr-30.png", full_page=True)

        try:
            async with page.expect_download(timeout=3000) as dl_info:
                await page.click("#exportBtn")
            dl = await dl_info.value
            await dl.save_as("/workspace/dar-export.wav")
            sz = __import__("os").path.getsize("/workspace/dar-export.wav")
            print(f"Exported WAV: {sz} bytes")
        except Exception as e:
            print(f"Export failed: {e}")

        await page.click("[data-lang=en]")
        await page.wait_for_timeout(200)
        h1 = await page.text_content("h1")
        print(f"EN h1 first 60 chars: {h1[:60]}")
        await page.screenshot(path="/workspace/dar-3-en.png", full_page=True)

        await page.click("#resetBtn")
        await page.wait_for_timeout(300)
        drop_visible = await page.is_visible("#drop")
        print(f"After reset, drop visible: {drop_visible}")

        await page.click("[data-lang=th]")
        await page.wait_for_timeout(200)

        print(f"\n=== JS errors/warnings: {len(errors)} ===")
        for e in errors[:20]: print("  ", e)

        await browser.close()

asyncio.run(main())

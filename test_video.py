"""Test Dead Air Remover with VIDEO file (new feature)."""
import asyncio
import os
from playwright.async_api import async_playwright

CHROME = "/root/.cache/ms-playwright/chromium-1223/chrome-linux/chrome"
URL = "http://127.0.0.1:8765/"
TEST_VIDEO = "/tmp/dar-test.mp4"

async def main():
    errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=CHROME, headless=True,
            args=["--no-sandbox","--disable-gpu","--use-gl=swiftshader","--enable-webgl","--autoplay-policy=no-user-gesture-required"]
        )
        ctx = await browser.new_context(viewport={"width":1400,"height":900})
        page = await ctx.new_page()
        page.on("console", lambda m: errors.append(f"[{m.type}] {m.text}") if m.type in ("error",) else None)
        page.on("pageerror", lambda e: errors.append(f"[PAGEERROR] {e}"))
        await page.goto(URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(2500)

        # Check editor showed (with demo audio)
        editor_visible = await page.is_visible("#editor.show")
        print(f"Editor visible (demo): {editor_visible}")

        # Check video stage hidden initially (demo is audio)
        video_visible = await page.is_visible("#videoStage")
        print(f"Video stage (audio demo): {video_visible}")

        # Check export button text
        export_text = await page.text_content("#exportBtn")
        print(f"Export btn text (audio): {export_text}")

        # Reset and upload a video file
        await page.click("#resetBtn")
        await page.wait_for_timeout(300)

        # Set file on file input
        await page.set_input_files("#fileInput", TEST_VIDEO)
        # Wait for processing (up to 30s for video)
        await page.wait_for_function(
            "document.getElementById('editor').classList.contains('show')",
            timeout=45000
        )
        await page.wait_for_timeout(2000)

        # Check video stage is visible
        video_visible = await page.is_visible("#videoStage")
        print(f"Video stage (after upload): {video_visible}")

        # Check export button text
        export_text = await page.text_content("#exportBtn")
        print(f"Export btn text (video): {export_text}")

        # Check video element has src
        video_src = await page.evaluate("document.getElementById('origVideo').src")
        print(f"Video src starts with: {video_src[:50]}")

        # Check file info shows video dimensions
        file_info = await page.text_content("#fileInfo")
        print(f"File info: {file_info}")

        # Check video stat
        video_stat = await page.text_content("#videoStat")
        print(f"Video stat: {video_stat}")

        # Check segments detected
        segs = await page.text_content("#segCount")
        print(f"Segments detected: {segs}")

        # Check stats
        saved = await page.text_content("#statSaved")
        print(f"Saved: {saved}")

        # Screenshot
        await page.screenshot(path="/workspace/dar-video-1-loaded.png", full_page=True)

        # Test play with cuts button
        await page.click("#videoPlayCuts")
        await page.wait_for_timeout(500)
        cuts_text = await page.text_content("#videoPlayCuts")
        print(f"Cuts play btn (running): {cuts_text}")
        # Stop
        await page.click("#videoPlayCuts")
        await page.wait_for_timeout(300)
        cuts_text2 = await page.text_content("#videoPlayCuts")
        print(f"Cuts play btn (stopped): {cuts_text2}")

        # Try export (just trigger, don't wait for download)
        # The download will be WebM
        try:
            async with page.expect_download(timeout=60000) as dl_info:
                await page.click("#exportBtn")
            dl = await dl_info.value
            await dl.save_as("/workspace/dar-export-video.webm")
            sz = os.path.getsize("/workspace/dar-export-video.webm")
            print(f"Exported WebM: {sz} bytes")
        except Exception as e:
            print(f"Export error (may be expected in headless): {e}")

        await page.screenshot(path="/workspace/dar-video-2-after-export.png", full_page=True)

        # Switch to EN
        await page.click("[data-lang=en]")
        await page.wait_for_timeout(300)
        export_text_en = await page.text_content("#exportBtn")
        print(f"Export btn text (EN, video): {export_text_en}")

        # Switch back to TH
        await page.click("[data-lang=th]")
        await page.wait_for_timeout(300)

        print(f"\n=== JS errors: {len(errors)} ===")
        for e in errors[:10]: print("  ", e)

        await browser.close()

asyncio.run(main())

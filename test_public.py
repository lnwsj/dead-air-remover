import asyncio
from playwright.async_api import async_playwright

CHROME = "/root/.cache/ms-playwright/chromium-1223/chrome-linux/chrome"
URL = "https://b2cpmxhjm4t2.space.minimax.io"

async def main():
    errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=CHROME, headless=True,
            args=["--no-sandbox","--disable-gpu","--use-gl=swiftshader","--autoplay-policy=no-user-gesture-required"]
        )
        ctx = await browser.new_context(viewport={"width":1400,"height":900})
        page = await ctx.new_page()
        page.on("console", lambda m: errors.append(f"[{m.type}] {m.text}") if m.type in ("error","warning") else None)
        page.on("pageerror", lambda e: errors.append(f"[PAGEERROR] {e}"))
        await page.goto(URL, wait_until="networkidle")
        await page.wait_for_timeout(3000)

        editor = await page.is_visible("#editor.show")
        segs = await page.text_content("#segCount")
        new_dur = await page.text_content("#statNew")
        saved = await page.text_content("#statSaved")
        print(f"Public URL: {URL}")
        print(f"Editor: {editor}, Segs: {segs}, New: {new_dur}, Saved: {saved}")

        await page.screenshot(path="/workspace/dar-public-1.png", full_page=True)
        print(f"JS errors: {len(errors)}")
        for e in errors[:10]: print("  ", e)
        await browser.close()

asyncio.run(main())

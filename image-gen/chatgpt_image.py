#!/usr/bin/env python3
"""ChatGPT image generator via Playwright (runs on Linux, headful inside Xvfb).

Usage:
    chatgpt_image.py login
    chatgpt_image.py logout
    chatgpt_image.py list <prompts.md>
    chatgpt_image.py generate <prompts.md> [--output-dir <path>] [--only <stem>] [--timeout <sec>]

Session is persisted at ~/.cache/chatgpt-image-profile.
Login exposes the browser via x11vnc on :5900 — the user tunnels & connects.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

try:
    from playwright.async_api import async_playwright, TimeoutError as PwTimeout
    _HAS_PLAYWRIGHT = True
except ImportError:
    _HAS_PLAYWRIGHT = False

def _require_playwright() -> None:
    if not _HAS_PLAYWRIGHT:
        print("Playwright not installed. Run: bash ~/.claude/skills/dami-marp/image-gen/run.sh setup", file=sys.stderr)
        sys.exit(1)

PROFILE = Path.home() / ".cache" / "chatgpt-image-profile"
CHATGPT_URL = "https://chatgpt.com/"
XVFB_DISPLAY = ":99"
VNC_PORT = 5900


# ──────────────────────────────── prompt parsing ────────────────────────────────

def parse_prompts(md_path: Path) -> list[dict]:
    """Extract image entries from a markdown file.

    Recognized block shape:

        ### `filename.png` — optional caption

        - **Prompt**:

        ```
        multi-line prompt
        ```
    """
    text = md_path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"###\s+`([^`]+\.png)`(?:\s*[—-]\s*([^\n]+))?.*?"
        r"\*\*Prompt\*\*\s*:\s*\n*```[^\n]*\n(.*?)\n```",
        re.DOTALL,
    )
    entries: list[dict] = []
    for m in pattern.finditer(text):
        entries.append({
            "filename": m.group(1).strip(),
            "caption": (m.group(2) or "").strip(),
            "prompt": m.group(3).strip(),
        })
    return entries


# ──────────────────────────────── xvfb + vnc helpers ────────────────────────────

class Xvfb:
    """Context manager: start Xvfb on DISPLAY, kill on exit."""

    def __init__(self, display: str = XVFB_DISPLAY, geometry: str = "1600x1000x24"):
        self.display = display
        self.geometry = geometry
        self.proc: subprocess.Popen | None = None

    def __enter__(self):
        # Kill stale Xvfb on the same display
        subprocess.run(["pkill", "-f", f"Xvfb {self.display}"], check=False)
        time.sleep(0.3)
        self.proc = subprocess.Popen(
            ["Xvfb", self.display, "-screen", "0", self.geometry, "-nolisten", "tcp"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        # Wait for display ready
        for _ in range(50):
            if Path(f"/tmp/.X{self.display[1:]}-lock").exists():
                break
            time.sleep(0.1)
        os.environ["DISPLAY"] = self.display
        return self

    def __exit__(self, *exc):
        if self.proc:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.proc.kill()


def start_x11vnc(display: str = XVFB_DISPLAY, port: int = VNC_PORT) -> subprocess.Popen:
    """Start x11vnc exposing the given display on localhost:port."""
    return subprocess.Popen(
        [
            "x11vnc", "-display", display, "-rfbport", str(port),
            "-localhost",          # only allow local connections → SSH tunnel required
            "-nopw",               # no password (safe because localhost-only)
            "-forever", "-shared", "-quiet",
        ],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


# ──────────────────────────────── commands ──────────────────────────────────────

async def cmd_login(display: str | None = None) -> int:
    """Launch a Chromium window for interactive login.

    If --display is given (e.g. :22), reuse that existing X server (e.g. Chrome
    Remote Desktop session). Otherwise start a fresh Xvfb + x11vnc on :99.
    """
    PROFILE.mkdir(parents=True, exist_ok=True)

    async def _run_browser() -> None:
        async with async_playwright() as p:
            ctx = await p.chromium.launch_persistent_context(
                str(PROFILE),
                headless=False,
                args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
                viewport={"width": 1440, "height": 900},
            )
            page = ctx.pages[0] if ctx.pages else await ctx.new_page()
            await page.goto(CHATGPT_URL, wait_until="domcontentloaded")
            loop = asyncio.get_event_loop()
            stop = loop.create_future()

            def handler(signum, frame):
                if not stop.done():
                    loop.call_soon_threadsafe(stop.set_result, None)
            signal.signal(signal.SIGINT, handler)
            signal.signal(signal.SIGTERM, handler)
            await stop
            print("\n→ Saving session...")
            await ctx.close()

    if display:
        os.environ["DISPLAY"] = display
        print("")
        print(f"🔐  Browser launched on existing display {display}.")
        print(f"    Use the Chromium window in that session (e.g. Chrome Remote Desktop).")
        print(f"    When done logging in, return here and press Ctrl-C.")
        print("")
        await _run_browser()
        print(f"✅ Login session saved to {PROFILE}")
        return 0

    with Xvfb():
        vnc = start_x11vnc()
        try:
            print("")
            print("🔐  Browser launched on remote Xvfb + exposed via x11vnc on localhost:5900.")
            print("")
            print("   On your LOCAL machine (not this SSH session):")
            print("     1) Open a new terminal and run:")
            print("          ssh -L 5900:localhost:5900 <REMOTE> -N")
            print("     2) Open a VNC viewer (TigerVNC, RealVNC, macOS Screen Sharing)")
            print("        and connect to:   localhost:5900")
            print("     3) Log in to ChatGPT in the browser.")
            print("     4) When done, return here and press Ctrl-C.")
            print("")
            print(f"   (Tip: if you're using Chrome Remote Desktop, rerun with:")
            print(f"        ... chatgpt_image.py login --display :22 )")
            print("")
            await _run_browser()
            print(f"✅ Login session saved to {PROFILE}")
            return 0
        finally:
            vnc.terminate()


def cmd_logout() -> int:
    if PROFILE.exists():
        shutil.rmtree(PROFILE)
        print(f"✅ Removed {PROFILE}")
    else:
        print(f"(already empty) {PROFILE}")
    return 0


def cmd_list(md_path: Path) -> int:
    entries = parse_prompts(md_path)
    if not entries:
        print("No entries parsed.", file=sys.stderr)
        return 1
    for e in entries:
        print(f"{e['filename']:30s}  {e['caption']}")
    print(f"\n총 {len(entries)}개")
    return 0


# ──────────────────────────────── generation ────────────────────────────────────

async def wait_for_image(page, timeout_s: int) -> str | None:
    """Wait for a generated image to appear in the conversation. Return src URL or None."""
    # ChatGPT serves generated images from files.oaiusercontent.com or similar.
    # Be permissive: look in the last assistant turn for an <img> with a remote src.
    selectors = [
        'main img[src*="oaiusercontent"]',
        'main img[src*="oaistatic"]',
        'main img[alt*="Generated"]',
        'main img[alt*="생성"]',
    ]
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        for sel in selectors:
            loc = page.locator(sel).last
            try:
                if await loc.count() > 0 and await loc.is_visible():
                    src = await loc.get_attribute("src")
                    if src and src.startswith("http"):
                        # Give it a moment to finish loading (the initial preview may be low-res)
                        await asyncio.sleep(3)
                        src = await loc.get_attribute("src")
                        return src
            except Exception:
                pass
        await asyncio.sleep(1.5)
    return None


async def _ensure_logged_in(page) -> bool:
    """If logged out, click '로그인' → 'Google 계정으로 계속하기' → wait for redirect.
    Relies on the persistent profile already having a Google session."""
    # Logged-out detection: 로그인 button visible OR on auth.openai.com
    is_logged_out = False
    if "auth.openai.com" in page.url:
        is_logged_out = True
    else:
        for label in ("로그인", "Log in", "Sign in"):
            try:
                btn = page.get_by_role("button", name=label, exact=True).first
                if await btn.count() > 0 and await btn.is_visible():
                    is_logged_out = True
                    break
            except Exception:
                pass
    if not is_logged_out:
        return True

    print(f"  ⤷ logged out, attempting auto-login (URL: {page.url})", flush=True)

    # Step 1: click 로그인 if on chatgpt.com
    if "chatgpt.com" in page.url:
        for label in ("로그인", "Log in", "Sign in"):
            try:
                btn = page.get_by_role("button", name=label, exact=True).first
                if await btn.count() > 0:
                    await btn.click(timeout=3000)
                    print(f"  ⤷ clicked '{label}'", flush=True)
                    await page.wait_for_load_state("domcontentloaded", timeout=10000)
                    await asyncio.sleep(3)
                    break
            except Exception:
                continue

    # Step 2: click "Google" button (works on chatgpt.com modal or auth.openai.com)
    # Button may be <button>, <a>, or <div role="button"> depending on which page we're on.
    google_clicked = False
    for sel in (
        "button:has-text('Google 계정으로 계속하기')",
        "a:has-text('Google 계정으로 계속하기')",
        "[role='button']:has-text('Google 계정으로 계속하기')",
        "button:has-text('Continue with Google')",
        "a:has-text('Continue with Google')",
        "[role='button']:has-text('Continue with Google')",
        "button:has-text('Google')",
        "a:has-text('Google')",
    ):
        try:
            gbtn = page.locator(sel).first
            if await gbtn.count() > 0 and await gbtn.is_visible():
                await gbtn.click(timeout=5000)
                google_clicked = True
                print(f"  ⤷ clicked Google button via {sel}", flush=True)
                break
        except Exception as e:
            print(f"  ⤷ {sel} failed: {e}", flush=True)
            continue

    if not google_clicked:
        print("  ⚠️  no Google button found", flush=True)
        return False

    # Step 3: wait up to 45s for redirect back to chatgpt.com (Google session may take a moment)
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        if "chatgpt.com" in page.url and await page.locator("div[contenteditable='true']#prompt-textarea").count() > 0:
            print("  ⤷ auto-login succeeded", flush=True)
            return True
        await asyncio.sleep(1)
    print(f"  ⚠️  auto-login timed out at URL: {page.url}", flush=True)
    return False


async def generate_one(ctx, prompt: str, output_path: Path, timeout_s: int) -> bool:
    page = await ctx.new_page()
    try:
        await page.goto(CHATGPT_URL, wait_until="domcontentloaded")
        await asyncio.sleep(2)
        # Close any welcome modal / announcement
        for label in ["Stay logged out", "Not now", "Dismiss", "Got it"]:
            try:
                btn = page.get_by_role("button", name=label)
                if await btn.count() > 0:
                    await btn.first.click(timeout=2000)
            except Exception:
                pass

        # Auto-login if session expired (uses Google session in the persistent profile)
        await _ensure_logged_in(page)

        # Dismiss "Stay logged out" / no-auth modal that intercepts pointer events
        try:
            await page.evaluate("""() => {
                const ids = ['#modal-no-auth-login', '[data-testid=\"modal-no-auth-login\"]'];
                for (const sel of ids) document.querySelectorAll(sel).forEach(el => el.remove());
            }""")
        except Exception:
            pass

        # Find the prompt textarea (ProseMirror or textarea)
        textbox = page.locator("div[contenteditable='true']#prompt-textarea").first
        if await textbox.count() == 0:
            textbox = page.get_by_role("textbox").first
        await textbox.wait_for(state="visible", timeout=20_000)
        await textbox.click()
        # Include explicit image-generation instruction so GPT uses image tool
        full_prompt = f"Please generate an image with the following description. Respond with ONLY the generated image, no commentary.\n\n{prompt}"
        await textbox.fill(full_prompt)
        await page.keyboard.press("Enter")

        src = await wait_for_image(page, timeout_s)
        if not src:
            dbg = output_path.with_suffix(".fail.png")
            try: await page.screenshot(path=str(dbg), full_page=False)
            except Exception: pass
            print(f"  ❌ {output_path.name}: timed out after {timeout_s}s (screenshot: {dbg})")
            print(f"     URL: {page.url}")
            return False

        # Download via request context (reuses browser cookies/session)
        resp = await ctx.request.get(src)
        if resp.status != 200:
            print(f"  ❌ {output_path.name}: download HTTP {resp.status}")
            return False
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(await resp.body())
        print(f"  ✅ {output_path.name}  ({len(await resp.body())//1024} KB)")
        return True
    except PwTimeout as e:
        print(f"  ❌ {output_path.name}: {e}")
        return False
    except Exception as e:
        print(f"  ❌ {output_path.name}: {type(e).__name__}: {e}")
        return False
    finally:
        await page.close()


async def cmd_generate(md_path: Path, output_dir: Path, only: list[str] | None, timeout_s: int) -> int:
    entries = parse_prompts(md_path)
    if only:
        wanted = set()
        for tok in only:
            for x in tok.split(","):
                x = x.strip()
                if x:
                    wanted.add(x)
        def matches(e):
            fn = e["filename"]
            return fn in wanted or Path(fn).stem in wanted
        entries = [e for e in entries if matches(e)]
        if not entries:
            print(f"No entries matched {only}", file=sys.stderr)
            return 1

    if not PROFILE.exists() or not any(PROFILE.iterdir()):
        print("❌ No saved session. Run login first:", file=sys.stderr)
        print("     bash ~/.claude/skills/dami-marp/image-gen/run.sh login", file=sys.stderr)
        return 2

    print(f"📝 {len(entries)} image(s) to generate")
    print(f"📂 Output: {output_dir}")
    print(f"⏱️  Timeout per image: {timeout_s}s\n")

    with Xvfb():
        async with async_playwright() as p:
            ctx = await p.chromium.launch_persistent_context(
                str(PROFILE),
                headless=False,
                args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
                viewport={"width": 1440, "height": 900},
            )
            ok = 0
            skipped = 0
            failed = 0
            try:
                for i, e in enumerate(entries, 1):
                    out = output_dir / e["filename"]
                    print(f"[{i}/{len(entries)}] {e['filename']}  —  {e['caption']}")
                    if out.exists():
                        print(f"  ⏭️  already exists, skipping")
                        skipped += 1
                        continue
                    if await generate_one(ctx, e["prompt"], out, timeout_s):
                        ok += 1
                    else:
                        failed += 1
            finally:
                await ctx.close()

    print(f"\n완료: ✅ {ok}  ⏭️ {skipped}  ❌ {failed}")
    return 0 if failed == 0 else 1


# ──────────────────────────────── cli ───────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="ChatGPT image generation via Playwright")
    sub = parser.add_subparsers(dest="cmd", required=True)

    login_p = sub.add_parser("login")
    login_p.add_argument("--display", default=None,
                         help="Reuse an existing X display (e.g. :22 for Chrome Remote Desktop). "
                              "If omitted, starts a fresh Xvfb+x11vnc on :99.")
    sub.add_parser("logout")

    lst = sub.add_parser("list")
    lst.add_argument("prompts")

    gen = sub.add_parser("generate")
    gen.add_argument("prompts")
    gen.add_argument("--output-dir", default=None,
                     help="Output directory. Default: <prompts.md dir>/images/")
    gen.add_argument("--only", action="append", default=None,
                     help="Generate only matching filename(s). Stem or full name. Comma-separated or repeat.")
    gen.add_argument("--timeout", type=int, default=180, help="Per-image timeout (sec)")

    args = parser.parse_args()

    if args.cmd == "login":
        _require_playwright()
        return asyncio.run(cmd_login(display=args.display))
    if args.cmd == "logout":
        return cmd_logout()
    if args.cmd == "list":
        return cmd_list(Path(args.prompts).expanduser())
    if args.cmd == "generate":
        _require_playwright()
        md = Path(args.prompts).expanduser()
        if not md.exists():
            print(f"❌ prompts file not found: {md}", file=sys.stderr)
            return 1
        out = Path(args.output_dir).expanduser() if args.output_dir else md.parent / "images"
        return asyncio.run(cmd_generate(md, out, args.only, args.timeout))

    return 2


if __name__ == "__main__":
    sys.exit(main())

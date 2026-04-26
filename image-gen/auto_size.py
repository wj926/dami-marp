"""Auto-fit slide image widths via iterative render-measure-adjust loop.

Algorithm:
    1. Build PDF (via dami-marp build.py).
    2. For each `![w:NNN](...)` image in the MD, locate its slide by scanning
       slide separators (`---` at column 0).
    3. Render that slide page from the PDF, find non-white content bbox.
    4. Compute fill_ratio = content_bottom / slide_content_area.
    5. If fill_ratio outside [target_lo, target_hi] → resize and rebuild.
    6. Iterate up to N attempts per image.

Usage:
    python auto_size.py <slides.md> [--lo 0.85] [--hi 0.96] [--max-iter 8]
                                    [--only filename1.png,filename2.png]

Requires: PyMuPDF (`pip install pymupdf`), Pillow, numpy.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import fitz
import numpy as np


SLIDE_SEPARATOR = re.compile(r"^---\s*$", re.MULTILINE)
IMAGE_PATTERN = re.compile(r"!\[w:(\d+)\]\(([^)]+)\)")

MIN_W, MAX_W = 200, 1200


def backup_md_once(md: Path) -> Path | None:
    """Backup the markdown file to <project>/.history/ once per run.

    Returns the backup path, or None if backup already exists for this run.
    The "once per run" guard avoids spamming .history/ on every iteration.
    """
    history_dir = md.parent / ".history"
    history_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = history_dir / f"{md.stem}_{timestamp}{md.suffix}"
    if backup_path.exists():
        return None
    shutil.copy2(md, backup_path)
    return backup_path


def find_build_script() -> Path:
    """Locate dami-marp build.py — first try sibling skill dir, then PATH."""
    candidates = [
        Path(__file__).resolve().parent.parent / "bin" / "build.py",
        Path.home() / ".claude" / "skills" / "dami-marp" / "bin" / "build.py",
    ]
    for c in candidates:
        if c.exists():
            return c
    sys.exit(f"ERROR: dami-marp build.py not found. Looked in: {candidates}")


def build(md: Path, build_script: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(build_script), str(md)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        sys.exit(f"[build] failed:\n{result.stderr}")


def discover_targets(md_text: str) -> list[tuple[int, str, int]]:
    """Find all `![w:N](path)` images and return (slide_idx, image_path, width).

    Slide index is 0-based. The first slide is everything before the first
    `---` separator (after the frontmatter). Frontmatter is the first
    `---...---` block at the top of the file.
    """
    # Strip frontmatter
    body_start = 0
    if md_text.startswith("---"):
        # find closing fence
        m = re.search(r"^---\s*$", md_text[3:], re.MULTILINE)
        if m:
            body_start = 3 + m.end()
    body = md_text[body_start:]

    # Find slide boundaries (positions of `---` at line start)
    boundaries = [m.start() for m in SLIDE_SEPARATOR.finditer(body)]
    boundaries = [0] + boundaries + [len(body)]

    targets: list[tuple[int, str, int]] = []
    for img in IMAGE_PATTERN.finditer(body):
        pos = img.start()
        # which slide bucket does pos fall into?
        slide_idx = 0
        for i in range(len(boundaries) - 1):
            if boundaries[i] <= pos < boundaries[i + 1]:
                slide_idx = i
                break
        width = int(img.group(1))
        path = img.group(2)
        targets.append((slide_idx, path, width))
    return targets


def get_width(md_text: str, image_path: str) -> int:
    m = re.search(rf"!\[w:(\d+)\]\({re.escape(image_path)}\)", md_text)
    return int(m.group(1)) if m else -1


def set_width(md: Path, image_path: str, new_w: int) -> None:
    text = md.read_text(encoding="utf-8")
    new_text = re.sub(
        rf"!\[w:\d+\]\({re.escape(image_path)}\)",
        f"![w:{new_w}]({image_path})",
        text,
    )
    md.write_text(new_text, encoding="utf-8")


def render_slide(pdf: Path, slide_idx: int) -> np.ndarray:
    doc = fitz.open(pdf)
    pix = doc[slide_idx].get_pixmap(dpi=100)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    doc.close()
    return img


def check_fit(slide_img: np.ndarray) -> tuple[float, bool]:
    """Returns (fill_ratio, overflows).

    fill_ratio = bottom_of_content / content_area_height (0~1+).
    overflows  = content reaches the very bottom of the content area.
    """
    h, w = slide_img.shape[:2]
    gray = slide_img[:, :, :3].mean(axis=2)
    non_white = gray < 250
    footer_start = int(h * 0.92)  # exclude footer
    rows_with_content = np.where(non_white[:footer_start, :].any(axis=1))[0]
    if len(rows_with_content) == 0:
        return 0.0, False
    bottom = rows_with_content[-1]
    ratio = bottom / footer_start
    overflows = ratio >= 0.99
    return ratio, overflows


def adjust(
    md: Path,
    pdf: Path,
    build_script: Path,
    image_path: str,
    slide_idx: int,
    target_lo: float,
    target_hi: float,
    max_iter: int,
) -> None:
    cur_w = get_width(md.read_text(encoding="utf-8"), image_path)
    if cur_w < 0:
        print(f"  [WARN] width tag not found for {image_path}, skipping")
        return
    print(f"  current width: {cur_w}px")
    for attempt in range(max_iter):
        build(md, build_script)
        img = render_slide(pdf, slide_idx)
        ratio, overflow = check_fit(img)
        print(f"    attempt {attempt+1}: w={cur_w}  fill_ratio={ratio:.2f}  overflow={overflow}")
        if overflow or ratio > target_hi:
            new_w = int(cur_w * 0.85)
        elif ratio < target_lo:
            new_w = int(cur_w * 1.15)
        else:
            print(f"    [OK] fit at w={cur_w} (ratio={ratio:.2f})")
            return
        new_w = max(MIN_W, min(MAX_W, new_w))
        if new_w == cur_w:
            print(f"    [OK] converged at w={cur_w}")
            return
        set_width(md, image_path, new_w)
        cur_w = new_w
    print(f"    [WARN] max iterations reached, last w={cur_w}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Auto-fit Marp slide image widths")
    parser.add_argument("md", type=Path, help="Marp slide markdown file")
    parser.add_argument("--lo", type=float, default=0.85, help="target fill_ratio lower bound (default 0.85)")
    parser.add_argument("--hi", type=float, default=0.96, help="target fill_ratio upper bound (default 0.96)")
    parser.add_argument("--max-iter", type=int, default=8, help="max iterations per image (default 8)")
    parser.add_argument(
        "--only",
        type=str,
        default="",
        help="comma-separated image filenames to adjust (default: all `![w:N](...)` images)",
    )
    args = parser.parse_args()

    md: Path = args.md.resolve()
    if not md.exists():
        sys.exit(f"ERROR: file not found: {md}")
    pdf = md.with_suffix(".pdf")
    build_script = find_build_script()

    text = md.read_text(encoding="utf-8")
    targets = discover_targets(text)
    if not targets:
        sys.exit("ERROR: no `![w:N](...)` images found in slides.")

    if args.only:
        wanted = {s.strip() for s in args.only.split(",") if s.strip()}
        targets = [t for t in targets if Path(t[1]).name in wanted or t[1] in wanted]
        if not targets:
            sys.exit(f"ERROR: --only filter matched 0 images (wanted: {wanted})")

    print(f"Discovered {len(targets)} image target(s):")
    for slide_idx, path, w in targets:
        print(f"  slide {slide_idx+1}: {path} (w={w})")
    print()

    # Backup markdown once before any modification (rollback safety)
    backup = backup_md_once(md)
    if backup:
        print(f"[backup] {md.name} → {backup.relative_to(md.parent)}")
    print()

    for slide_idx, image_path, _w in targets:
        print(f"[slide {slide_idx+1}] {image_path}")
        adjust(md, pdf, build_script, image_path, slide_idx, args.lo, args.hi, args.max_iter)

    print("\nFinal build:")
    build(md, build_script)
    print(f"  → {pdf}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Marp 슬라이드 빌드 프리프로세서.

사용법:
    python3 build.py <slides.md> [--pdf|--pptx|--html]

동작:
    1. 슬라이드 파일과 같은 폴더에서 `refs.toml`을 찾는다.
    2. 슬라이드 본문의 `{{cite:key}}` 를 `refs.toml`의 항목으로 치환한다.
    3. 치환된 내용을 `<파일명>.built.md` 로 저장하고 marp 로 빌드한다.
    4. 빌드 후 `<파일명>.built.md` 는 삭제한다.

인용 형식 (통일):
    저자. "제목." *저널/학회명*, 권(호), 쪽, 연도.
    예: Rao, R. V., et al. "Teaching-learning-based optimization." *Computer-Aided Design*, 43(3), 303-315, 2011.
"""
from __future__ import annotations

import argparse
import base64
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path


CITE_PATTERN = re.compile(r"\{\{cite:([a-zA-Z0-9_\-]+)\}\}")

# ```mermaid\n...\n```  (fence may have optional annotation like `{width: 80%}`)
MERMAID_PATTERN = re.compile(
    r"^```mermaid\s*(\{[^}]*\})?\s*\n(.*?)\n```",
    re.MULTILINE | re.DOTALL,
)


def format_citation(ref: dict) -> str:
    """refs.toml 항목을 통일된 인용 문자열로 변환."""
    if "raw" in ref:
        return ref["raw"]

    authors = ref.get("authors", "Unknown").rstrip()
    title = ref.get("title", "Untitled").rstrip(".")
    venue = ref.get("venue", "")
    year = ref.get("year", "n.d.")

    authors_with_dot = authors if authors.endswith(".") else authors + "."
    parts: list[str] = [f'{authors_with_dot} "{title}."']

    venue_segment_tokens: list[str] = []
    if venue:
        venue_segment_tokens.append(f"*{venue}*")
    if "volume" in ref and "issue" in ref:
        venue_segment_tokens.append(f'{ref["volume"]}({ref["issue"]})')
    elif "volume" in ref:
        venue_segment_tokens.append(str(ref["volume"]))
    if "pages" in ref:
        venue_segment_tokens.append(str(ref["pages"]))
    venue_segment_tokens.append(str(year))
    parts.append(", ".join(venue_segment_tokens) + ".")

    return " ".join(parts)


def load_refs(refs_path: Path) -> dict[str, dict]:
    if not refs_path.exists():
        return {}
    with refs_path.open("rb") as f:
        return tomllib.load(f)


def substitute_placeholders(content: str, refs: dict[str, dict]) -> tuple[str, list[str]]:
    missing: list[str] = []

    def replace(match: re.Match) -> str:
        key = match.group(1)
        if key not in refs:
            missing.append(key)
            return f"[MISSING CITATION: {key}]"
        return format_citation(refs[key])

    return CITE_PATTERN.sub(replace, content), missing


def find_mmdc() -> str | None:
    """mermaid-cli 바이너리 경로를 찾는다. 없으면 None."""
    mmdc = shutil.which("mmdc")
    if mmdc:
        return mmdc
    nvm_dir = Path.home() / ".nvm" / "versions" / "node"
    if nvm_dir.exists():
        for node_dir in sorted(nvm_dir.iterdir(), reverse=True):
            candidate = node_dir / "bin" / "mmdc"
            if candidate.exists():
                return str(candidate)
    return None


def render_mermaid(code: str, mmdc: str, config_path: Path) -> str:
    """mermaid 블록 하나를 SVG 문자열로 변환."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mmd_file = Path(tmpdir) / "diagram.mmd"
        svg_file = Path(tmpdir) / "diagram.svg"
        mmd_file.write_text(code, encoding="utf-8")

        result = subprocess.run(
            [
                mmdc,
                "-i", str(mmd_file),
                "-o", str(svg_file),
                "--configFile", str(config_path),
                "--quiet",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0 or not svg_file.exists():
            raise RuntimeError(
                f"mermaid 렌더 실패:\n--- code ---\n{code}\n"
                f"--- stderr ---\n{result.stderr}"
            )
        return svg_file.read_text(encoding="utf-8")


def svg_to_data_uri(svg: str) -> str:
    """SVG 문자열을 base64 data URI 로 변환 (markdown/HTML 에 안전하게 임베드).

    root <svg> 에 `overflow="visible"` 를 주입해 Chromium 이 <img> 로
    렌더할 때 text bbox 우측 sub-pixel clipping 을 방지한다.
    """
    svg = re.sub(r"<svg\b", '<svg overflow="visible"', svg, count=1)
    b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"


def substitute_mermaid_blocks(content: str, source_path: Path) -> str:
    """```mermaid ... ``` 블록을 inline SVG 로 교체."""
    blocks = list(MERMAID_PATTERN.finditer(content))
    if not blocks:
        return content

    mmdc = find_mmdc()
    if not mmdc:
        sys.exit(
            "ERROR: `mmdc` (mermaid-cli) 를 찾을 수 없습니다. "
            "설치: `npm i -g @mermaid-js/mermaid-cli`"
        )

    config_path = Path(__file__).resolve().parent.parent / "themes" / "mermaid-config.json"
    if not config_path.exists():
        sys.exit(f"ERROR: mermaid config 파일이 없습니다: {config_path}")

    print(f"[build] mermaid 블록 {len(blocks)}개 렌더 중...")

    def replace(match: re.Match) -> str:
        annotation = match.group(1) or ""
        code = match.group(2)
        # annotation 에서 width 추출 (예: {width: 80%})
        width_match = re.search(r"width\s*:\s*([^,}]+)", annotation)
        width_style = f"max-width: {width_match.group(1).strip()};" if width_match else ""

        try:
            svg = render_mermaid(code, mmdc, config_path)
        except RuntimeError as e:
            line = content[: match.start()].count("\n") + 1
            sys.exit(f"[build] {source_path}:{line} {e}")

        data_uri = svg_to_data_uri(svg)
        return f'<div class="mermaid-embed" style="{width_style}"><img src="{data_uri}" alt="mermaid diagram" /></div>'

    return MERMAID_PATTERN.sub(replace, content)


def find_marp() -> str:
    marp_bin = shutil.which("marp")
    if marp_bin:
        return marp_bin

    nvm_dir = Path.home() / ".nvm" / "versions" / "node"
    if nvm_dir.exists():
        for node_dir in sorted(nvm_dir.iterdir(), reverse=True):
            candidate = node_dir / "bin" / "marp"
            if candidate.exists():
                return str(candidate)

    sys.exit(
        "ERROR: `marp` 를 찾을 수 없습니다. 새 터미널을 열거나 "
        "`source ~/.nvm/nvm.sh && nvm use --lts` 후 다시 시도하세요."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Marp build with citation preprocessing")
    parser.add_argument("slides", type=Path, help="슬라이드 마크다운 파일 경로")
    parser.add_argument(
        "--format",
        choices=["pdf", "pptx", "html"],
        default="pdf",
        help="출력 형식 (기본: pdf)",
    )
    parser.add_argument(
        "--keep-built",
        action="store_true",
        help="전처리 결과 .built.md 파일을 지우지 않음 (디버깅용)",
    )
    args = parser.parse_args()

    slides_path: Path = args.slides.resolve()
    if not slides_path.exists():
        sys.exit(f"ERROR: 파일이 없습니다: {slides_path}")

    refs_path = slides_path.parent / "refs.toml"
    refs = load_refs(refs_path)
    print(f"[build] refs.toml: {refs_path} ({len(refs)}개 항목)")

    content = slides_path.read_text(encoding="utf-8")
    new_content, missing = substitute_placeholders(content, refs)

    if missing:
        print(f"[build] ⚠️  누락된 인용 키: {sorted(set(missing))}")

    new_content = substitute_mermaid_blocks(new_content, slides_path)

    built_path = slides_path.with_name(f"{slides_path.stem}.built.md")
    built_path.write_text(new_content, encoding="utf-8")

    marp = find_marp()
    output_path = slides_path.with_suffix(f".{args.format}")
    flag = f"--{args.format}"

    theme_path = Path(__file__).resolve().parent.parent / "themes" / "dami-lab.css"
    if not theme_path.exists():
        sys.exit(f"ERROR: theme 파일이 없습니다: {theme_path}")

    cmd = [
        marp,
        str(built_path),
        flag,
        "--theme-set", str(theme_path),
        "--allow-local-files",
        "-o", str(output_path),
    ]
    print(f"[build] 실행: {' '.join(cmd)}")
    result = subprocess.run(cmd)

    if not args.keep_built:
        built_path.unlink()

    if result.returncode != 0:
        sys.exit(result.returncode)

    print(f"[build] ✅ 완료: {output_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Generate PDF reports from Markdown (config in config/report.yaml).

- Converts Mermaid blocks to PNG via Mermaid CLI (mmdc): saves each block as
  .mmd, runs mmdc -i diagram.mmd -o diagram.png -b transparent, and inserts
  the PNG into the Markdown. Output is deterministic and CI-friendly.
- Creates one folder per report under output_dir (e.g. docs/pdf/0001-report-models/)
  containing the PDF plus diagram PNGs (and .mmd sources).
- Applies CSS for margins and typography (report-pdf.css).

Usage (from project root):
  python scripts/docs/generate-report-pdf.py

Requirements:
  - Node.js and Mermaid CLI: npm install -g @mermaid-js/mermaid-cli  (mmdc -v)
  - Pandoc, wkhtmltopdf (or pdflatex).
  - PyYAML (pip install pyyaml).
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML not found. Install with: pip install pyyaml")
    sys.exit(1)

# Optional explicit path to Mermaid CLI on Windows (npm global).
def _mmdc_win_path() -> Path | None:
    apd = os.environ.get("APPDATA")
    if not apd:
        return None
    return Path(apd, "npm", "mmdc.cmd")


def get_mmdc_path() -> Path | str:
    """Return mmdc executable: explicit Windows path if present, else 'mmdc' from PATH."""
    if sys.platform == "win32":
        win_path = _mmdc_win_path()
        if win_path and win_path.is_file():
            return win_path
    return "mmdc"


def find_repo_root() -> Path:
    """Repository root (directory containing config/ and docs/)."""
    script_dir = Path(__file__).resolve().parent
    root = script_dir.parent.parent
    if not (root / "config").is_dir():
        root = Path.cwd()
    return root


def load_report_config(root: Path) -> dict:
    """Load config/report.yaml and return the 'report' section."""
    config_path = root / "config" / "report.yaml"
    if not config_path.exists():
        print(f"Error: Config not found: {config_path}")
        sys.exit(1)
    with open(config_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not data or "report" not in data:
        print("Error: config/report.yaml must contain key 'report'.")
        sys.exit(1)
    return data["report"]


def ensure_pandoc() -> bool:
    """Check for Pandoc on PATH; on Windows optionally try winget install."""
    if shutil.which("pandoc"):
        return True
    print("Pandoc not found on PATH.")
    if sys.platform == "win32":
        print("Attempting install via winget: winget install pandoc")
        try:
            subprocess.run(
                [
                    "winget", "install", "pandoc",
                    "--accept-package-agreements", "--accept-source-agreements",
                ],
                check=False,
                capture_output=True,
                timeout=120,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            print(f"Could not run winget: {e}")
        if shutil.which("pandoc"):
            print("Pandoc installed. Run the script again (you may need to reopen the terminal).")
            return True
    print("Install Pandoc manually: https://pandoc.org/installing.html")
    return False


def ensure_mmdc() -> bool:
    """Check that Mermaid CLI (mmdc) is available."""
    path = get_mmdc_path()
    if path == "mmdc":
        if shutil.which("mmdc"):
            return True
    else:
        if Path(path).is_file():
            return True
    print("Mermaid CLI (mmdc) not found.")
    if sys.platform == "win32":
        win_path = _mmdc_win_path()
        if win_path:
            print(f"  Expected at: {win_path}")
    print("Install with: npm install -g @mermaid-js/mermaid-cli")
    return False


def ensure_pdf_engine() -> bool:
    """Ensure a PDF engine (wkhtmltopdf or pdflatex) is available; on Windows optionally try winget."""
    if shutil.which("wkhtmltopdf"):
        return True
    if shutil.which("pdflatex"):
        return True
    print("No PDF engine found (wkhtmltopdf or pdflatex).")
    if sys.platform == "win32":
        print("Attempting install via winget: winget install wkhtmltopdf.wkhtmltox")
        try:
            subprocess.run(
                [
                    "winget", "install", "wkhtmltopdf.wkhtmltox",
                    "--accept-package-agreements", "--accept-source-agreements",
                ],
                check=False,
                capture_output=True,
                timeout=180,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            print(f"Could not run winget: {e}")
        if shutil.which("wkhtmltopdf"):
            print("wkhtmltopdf installed. Run the script again (you may need to reopen the terminal).")
            return True
    print("Install a PDF engine: winget install wkhtmltopdf.wkhtmltox  or MiKTeX/TeX Live for pdflatex.")
    return False


def collect_md_files(root: Path, input_path: str) -> list[Path]:
    """Return list of .md files from input_path (file or directory)."""
    p = root / input_path.replace("/", os.sep)
    if not p.exists():
        print(f"Error: Input path not found: {p}")
        sys.exit(1)
    if p.is_file():
        return [p] if p.suffix.lower() == ".md" else []
    return sorted(p.glob("**/*.md"))


def mermaid_blocks_to_local_images(md_content: str, images_dir: Path, mmdc_cmd) -> str:
    """
    Replace ```mermaid ... ``` blocks with local PNG images.
    Saves each block as diagram_N.mmd and generates diagram_N.png with mmdc -b transparent.
    """
    mmdc_list = [str(mmdc_cmd)] if isinstance(mmdc_cmd, Path) else [mmdc_cmd]
    pattern = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
    images_dir.mkdir(parents=True, exist_ok=True)
    seen = 0

    def replace_block(match: re.Match) -> str:
        nonlocal seen
        seen += 1
        idx = seen
        code = match.group(1).strip()
        filename_mmd = f"diagram_{idx}.mmd"
        filename_png = f"diagram_{idx}.png"
        filepath_mmd = images_dir / filename_mmd
        filepath_png = images_dir / filename_png
        try:
            filepath_mmd.write_text(code, encoding="utf-8")
            result = subprocess.run(
                mmdc_list + ["-i", str(filepath_mmd), "-o", str(filepath_png), "-b", "transparent"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(images_dir),
            )
            if result.returncode != 0:
                raise RuntimeError(result.stderr or result.stdout or f"exit code {result.returncode}")
        except FileNotFoundError:
            print("  Warning: mmdc not found. Install: npm install -g @mermaid-js/mermaid-cli")
            return "\n\n*[Diagram not available — install Mermaid CLI.]*\n\n"
        except subprocess.TimeoutExpired:
            print(f"  Warning: timeout generating diagram {idx}.")
            return "\n\n*[Diagram not available — timeout.]*\n\n"
        except Exception as e:
            print(f"  Warning: could not generate diagram {idx}: {e}")
            return "\n\n*[Diagram not available.]*\n\n"
        abs_path = filepath_png.resolve().as_posix()
        file_url = "file:///" + abs_path.replace("\\", "/")
        return f"\n\n![Diagram {idx}]({file_url})\n\n"

    return pattern.sub(replace_block, md_content)


def main() -> None:
    root = find_repo_root()
    os.chdir(root)

    config = load_report_config(root)
    input_path = config.get("input_path", "docs")
    output_dir = config.get("output_dir", "docs/pdf")
    output_dir_path = root / output_dir.replace("/", os.sep)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    md_files = collect_md_files(root, input_path)
    if not md_files:
        print("No .md files found.")
        sys.exit(0)

    if not ensure_pandoc():
        sys.exit(1)
    if not ensure_pdf_engine():
        sys.exit(1)
    if not ensure_mmdc():
        sys.exit(1)

    mmdc_cmd = get_mmdc_path()
    script_dir = Path(__file__).resolve().parent
    css_path = script_dir / "report-pdf.css"
    if not css_path.exists():
        css_path = None

    for md_file in md_files:
        stem = md_file.stem
        report_folder = output_dir_path / stem
        output_pdf = report_folder / f"{stem}.pdf"

        if report_folder.exists():
            shutil.rmtree(report_folder)
        report_folder.mkdir(parents=True, exist_ok=True)

        md_content = md_file.read_text(encoding="utf-8")
        print(f"Generating diagrams in {report_folder}...")
        md_processed = mermaid_blocks_to_local_images(md_content, report_folder, mmdc_cmd)

        prepared_md = report_folder / "_prepared.md"
        prepared_md.write_text(md_processed, encoding="utf-8")

        cmd = [
            "pandoc",
            str(prepared_md),
            "-o", str(output_pdf),
            "--standalone",
        ]
        if css_path:
            cmd.extend(["--css", str(css_path)])
        if shutil.which("wkhtmltopdf"):
            cmd.extend([
                "--pdf-engine=wkhtmltopdf",
                "--pdf-engine-opt=--enable-local-file-access",
                "--pdf-engine-opt=--quiet",
            ])
        elif shutil.which("pdflatex"):
            pass
        else:
            print("Error: wkhtmltopdf or pdflatex should be on PATH after ensure_pdf_engine().")
            sys.exit(1)

        print(f"Generating PDF: {md_file.name} -> {output_pdf}")
        result = subprocess.run(cmd, cwd=root)
        if result.returncode != 0:
            print("Pandoc failed. Try: winget install wkhtmltopdf.wkhtmltox")
            sys.exit(1)
        prepared_md.unlink(missing_ok=True)
        print(f"OK: {output_pdf}")

    print("Done.")


if __name__ == "__main__":
    main()

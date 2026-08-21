#!/usr/bin/env python3
"""Use an already-installed BaoCut CLI as an optional local ASR adapter.

This helper never installs BaoCut, downloads model weights, or changes app
settings. It returns ``unavailable`` when no existing CLI can be found.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from json import JSONDecoder
from pathlib import Path

DEFAULT_CANDIDATES = (
    "/Applications/BaoCut.app/Contents/MacOS/baocut-cli",
)


def find_cli() -> str | None:
    on_path = shutil.which("baocut")
    if on_path:
        return on_path
    for candidate in DEFAULT_CANDIDATES:
        path = Path(candidate)
        if path.is_file() and path.stat().st_mode & 0o111:
            return str(path)
    return None


def last_json(text: str) -> dict:
    decoder = JSONDecoder()
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            value, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and "status" in value:
            return value
    raise RuntimeError("BaoCut did not return a parseable JSON result")


def run_command(cli: str, args: list[str], timeout: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [cli, "--json", *args],
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("media", type=Path, help="Local audio/video file")
    parser.add_argument("--output", required=True, type=Path, help="Markdown transcript output")
    parser.add_argument("--source-lang", default="zh", help="Source language passed to BaoCut")
    parser.add_argument("--keep-project", action="store_true", help="Keep the temporary BaoCut project")
    parser.add_argument("--timeout", type=int, default=1800, help="Per-command timeout in seconds")
    args = parser.parse_args()

    cli = find_cli()
    if not cli:
        print(json.dumps({"status": "unavailable", "reason": "no existing BaoCut CLI found"}, ensure_ascii=False))
        return 2
    if not args.media.is_file():
        print(json.dumps({"status": "error", "reason": f"media file not found: {args.media}"}, ensure_ascii=False))
        return 2

    project_id: str | None = None
    try:
        result = run_command(
            cli,
            ["transcribe", str(args.media), "--source-lang", args.source_lang, "--no-speakers"],
            args.timeout,
        )
        payload = last_json(result.stdout)
        if result.returncode != 0 or payload.get("status") != "ok":
            raise RuntimeError(payload.get("error") or result.stderr.strip() or "BaoCut transcription failed")
        project_id = str(payload["projectId"])

        args.output.parent.mkdir(parents=True, exist_ok=True)
        export = run_command(
            cli,
            ["export", project_id, "--markdown", "--no-timestamps", "--no-speakers", "--output", str(args.output)],
            args.timeout,
        )
        if export.returncode != 0 or not args.output.is_file() or args.output.stat().st_size == 0:
            raise RuntimeError(export.stderr.strip() or export.stdout.strip() or "BaoCut transcript export failed")

        print(json.dumps({
            "status": "ok",
            "provider": "existing_baocut_installation",
            "project_id": project_id,
            "output": str(args.output),
            "media_retention": "caller_managed",
        }, ensure_ascii=False))
        return 0
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"status": "error", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    finally:
        if project_id and not args.keep_project:
            try:
                run_command(cli, ["project", "delete", project_id, "--yes"], args.timeout)
            except (OSError, subprocess.TimeoutExpired):
                pass


if __name__ == "__main__":
    raise SystemExit(main())

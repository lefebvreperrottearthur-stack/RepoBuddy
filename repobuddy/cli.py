"""Command line interface for RepoBuddy."""
import argparse
import json
from pathlib import Path
from .checks import analyze, as_markdown


def main(argv=None):
    parser = argparse.ArgumentParser(prog="repobuddy", description="Audit repository health (offline; no API token required).")
    parser.add_argument("path", nargs="?", default=".", help="Local repository path (default: current directory)")
    parser.add_argument("--format", choices=["text", "json", "markdown"], default="text", help="Output format")
    parser.add_argument("--output", metavar="FILE", help="Write output to a file")
    parser.add_argument("--fail-under", type=int, choices=range(101), metavar="0..100", help="Exit code 1 if score is below threshold")
    args = parser.parse_args(argv)
    try:
        result = analyze(Path(args.path))
    except ValueError as exc:
        parser.error(str(exc))
    if args.format == "json":
        output = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    elif args.format == "markdown":
        output = as_markdown(result)
    else:
        lines = [f"RepoBuddy | {result['score']}/100 | {result['passed']}/{result['total']} passed", "=" * 56]
        for item in result["findings"]:
            symbol = {"pass": "OK", "fail": "FIX", "warning": "WARN"}[item["status"]]
            lines.append(f"[{symbol}] {item['message']}")
            if item["status"] != "pass":
                lines.append(f"       -> {item['suggestion']}")
        lines.append("\nNote: " + result["note"])
        output = "\n".join(lines) + "\n"
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(output, end="")
    return int(args.fail_under is not None and result["score"] < args.fail_under)


if __name__ == "__main__":
    raise SystemExit(main())

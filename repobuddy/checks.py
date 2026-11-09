"""Deterministic, dependency-free checks for common repository practices."""
from dataclasses import asdict, dataclass
from pathlib import Path
import re

IGNORED = {".git", ".venv", "venv", "node_modules", "dist", "build", "__pycache__", ".tox", ".next"}
SECRET_NAMES = {".env", ".env.local", ".env.production", "id_rsa", "id_ed25519", "credentials.json", "service-account.json"}


@dataclass(frozen=True)
class Finding:
    id: str
    status: str
    message: str
    suggestion: str
    weight: int = 10

    def to_dict(self):
        return asdict(self)


def _exists(root: Path, *names: str) -> bool:
    return any((root / name).is_file() for name in names)


def _read(root: Path, name: str) -> str:
    try:
        return (root / name).read_text(encoding="utf-8", errors="replace")[:100_000]
    except OSError:
        return ""


def _walk_files(root: Path):
    """Limit scanning: never descend into symlinked directories or common build folders."""
    import os
    count = 0
    for base, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in IGNORED and not (Path(base) / d).is_symlink())
        for name in sorted(files):
            path = Path(base) / name
            if path.is_symlink():
                continue
            yield path
            count += 1
            if count >= 5000:
                return


def analyze(root: Path) -> dict:
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")
    findings = []

    def check(id, ok, message, suggestion, weight=10, warn=False):
        findings.append(Finding(id, "pass" if ok else ("warning" if warn else "fail"), message, suggestion, weight))

    readme = next((p for p in [root / "README.md", root / "README.rst", root / "README.txt"] if p.is_file()), None)
    check("readme", readme is not None, "README exists", "Add README.md explaining what the project does and how to run it.", 15)
    if readme:
        text = _read(root, readme.name)
        check("readme_usage", bool(re.search(r"(?im)^#{1,4}\s*(usage|installation|getting started|quickstart|utilisation|installation|démarrage)\b", text)), "README has an installation or usage section", "Add an Installation or Usage heading to the README.", 10)
    else:
        check("readme_usage", False, "README has an installation or usage section", "Document installation and usage.", 10)
    check("license", _exists(root, "LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"), "License exists", "Add an OSI-approved LICENSE (for example MIT).", 15)
    check("gitignore", _exists(root, ".gitignore"), ".gitignore exists", "Add .gitignore to exclude local and generated files.", 10)
    check("contributing", _exists(root, "CONTRIBUTING.md", ".github/CONTRIBUTING.md"), "Contribution guide exists", "Add CONTRIBUTING.md explaining how to contribute.", 10)
    check("code_of_conduct", _exists(root, "CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md"), "Code of conduct exists", "Add CODE_OF_CONDUCT.md to set community expectations.", 5)
    check("security", _exists(root, "SECURITY.md", ".github/SECURITY.md"), "Security policy exists", "Add SECURITY.md with a private vulnerability reporting process.", 5)
    check("ci", (root / ".github/workflows").is_dir() and any((root / ".github/workflows").glob("*.yml")) or ((root / ".github/workflows").is_dir() and any((root / ".github/workflows").glob("*.yaml"))), "GitHub Actions workflow exists", "Add a GitHub Actions workflow to run tests automatically.", 15)
    check("tests", any((root / name).is_dir() for name in ["tests", "test", "__tests__"]), "Tests directory exists", "Add automated tests in a tests/ directory.", 10)

    exposed = []
    for f in _walk_files(root):
        rel = f.relative_to(root)
        if f.name in SECRET_NAMES or (f.name.startswith(".env.") and f.name != ".env.example"):
            exposed.append(str(rel))
    check("sensitive_files", not exposed, "No common secret-file names found", "Review and remove possible credentials from the repository; rotate any exposed keys. Found: " + ", ".join(exposed[:5]), 10, warn=True)
    total = sum(f.weight for f in findings)
    achieved = sum(f.weight for f in findings if f.status == "pass")
    return {"tool": "RepoBuddy", "version": "0.1.0", "path": str(root), "score": round(100 * achieved / total), "passed": sum(f.status == "pass" for f in findings), "total": len(findings), "findings": [f.to_dict() for f in findings], "note": "Heuristic checks only; a passing result is not a security audit."}


def as_markdown(result: dict) -> str:
    lines = ["# RepoBuddy report", "", f"**Score:** {result['score']}/100 ({result['passed']}/{result['total']} checks passed)", "", "| Status | Check | Recommendation |", "| --- | --- | --- |"]
    for f in result["findings"]:
        clean = lambda s: str(s).replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {f['status'].upper()} | {clean(f['message'])} | {clean('—' if f['status'] == 'pass' else f['suggestion'])} |")
    lines += ["", f"> {result['note']}"]
    return "\n".join(lines) + "\n"

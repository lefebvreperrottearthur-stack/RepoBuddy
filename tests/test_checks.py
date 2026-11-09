import json
from pathlib import Path
from repobuddy.checks import analyze, as_markdown
from repobuddy.cli import main


def test_empty_repo_has_actionable_failures(tmp_path):
    r = analyze(tmp_path)
    assert r["score"] < 50
    assert any(x["id"] == "readme" and x["status"] == "fail" for x in r["findings"])
    assert len(r["findings"]) == 10


def test_good_repo_scores_full_marks(tmp_path):
    for name in ["README.md", "LICENSE", ".gitignore", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "SECURITY.md"]:
        (tmp_path / name).write_text("# Usage\nInstall and run", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / ".github/workflows").mkdir(parents=True)
    (tmp_path / ".github/workflows/test.yml").write_text("name: test", encoding="utf-8")
    r = analyze(tmp_path)
    assert r["score"] == 100
    assert "| PASS |" in as_markdown(r)


def test_sensitive_file_warning(tmp_path):
    (tmp_path / ".env").write_text("TOKEN=fake", encoding="utf-8")
    r = analyze(tmp_path)
    assert next(x for x in r["findings"] if x["id"] == "sensitive_files")["status"] == "warning"


def test_cli_json_and_threshold(tmp_path, capsys):
    code = main([str(tmp_path), "--format", "json", "--fail-under", "80"])
    data = json.loads(capsys.readouterr().out)
    assert code == 1
    assert data["tool"] == "RepoBuddy"


def test_cli_markdown_to_file(tmp_path):
    report = tmp_path / "report.md"
    assert main([str(tmp_path), "--format", "markdown", "--output", str(report)]) == 0
    assert "# RepoBuddy report" in report.read_text(encoding="utf-8")

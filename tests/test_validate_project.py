import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_project.py"


def valid_episode(number: int) -> str:
    body = "末世画面持续推进，人物行动改变局势。" * 32
    return (
        f"# 第{number:02d}集 测试集\n\n"
        "## 正文\n\n"
        "※场景：避难所·夜\n\n"
        "△主角关门，把最后一箱物资推进空间。\n\n"
        f"{body}\n\n"
        "【卡黑】"
    )


def write_state(root: Path, episodes: list[int]) -> None:
    values = ", ".join(str(item) for item in episodes)
    (root / "project.yaml").write_text(
        "version: 1\n"
        f"completed_episodes: [{values}]\n",
        encoding="utf-8",
    )


class ValidateProjectTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "chapters").mkdir()
        (self.root / "drafts").mkdir()
        write_state(self.root, [])

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root), *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def write_episode(self, number: int, content: Optional[str] = None, source: str = "chapters") -> None:
        (self.root / source / f"Episode-{number:02d}.md").write_text(
            content if content is not None else valid_episode(number),
            encoding="utf-8",
        )

    def test_empty_template_passes(self) -> None:
        result = self.run_cli()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("PASS", result.stdout)

    def test_valid_episode_range_passes(self) -> None:
        self.write_episode(1, source="drafts")
        self.write_episode(2, source="drafts")
        result = self.run_cli("--source", "drafts", "--episodes", "1-2")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_missing_episode_fails(self) -> None:
        self.write_episode(1, source="drafts")
        result = self.run_cli("--source", "drafts", "--episodes", "1-2")
        self.assertEqual(1, result.returncode)
        self.assertIn("MISSING_EPISODE", result.stdout)

    def test_illegal_filename_fails(self) -> None:
        (self.root / "drafts" / "Episode-1.md").write_text(valid_episode(1), encoding="utf-8")
        result = self.run_cli("--source", "drafts")
        self.assertEqual(1, result.returncode)
        self.assertIn("INVALID_FILENAME", result.stdout)

    def test_missing_scene_marker_fails(self) -> None:
        self.write_episode(1, valid_episode(1).replace("※", ""), source="drafts")
        result = self.run_cli("--source", "drafts", "--episodes", "1-1")
        self.assertEqual(1, result.returncode)
        self.assertIn("MISSING_SCENE_MARKER", result.stdout)

    def test_missing_action_marker_fails(self) -> None:
        self.write_episode(1, valid_episode(1).replace("△", ""), source="drafts")
        result = self.run_cli("--source", "drafts", "--episodes", "1-1")
        self.assertEqual(1, result.returncode)
        self.assertIn("MISSING_ACTION_MARKER", result.stdout)

    def test_missing_cliffhanger_fails(self) -> None:
        self.write_episode(1, valid_episode(1).replace("【卡黑】", ""), source="drafts")
        result = self.run_cli("--source", "drafts", "--episodes", "1-1")
        self.assertEqual(1, result.returncode)
        self.assertIn("MISSING_CLIFFHANGER", result.stdout)

    def test_short_episode_fails(self) -> None:
        self.write_episode(1, "# 第01集 测试\n\n## 正文\n※场景\n△动作\n很短。\n【卡黑】", source="drafts")
        result = self.run_cli("--source", "drafts", "--episodes", "1-1")
        self.assertEqual(1, result.returncode)
        self.assertIn("WORD_COUNT", result.stdout)

    def test_missing_required_heading_fails(self) -> None:
        self.write_episode(1, valid_episode(1).replace("## 正文", "正文"), source="drafts")
        result = self.run_cli("--source", "drafts", "--episodes", "1-1")
        self.assertEqual(1, result.returncode)
        self.assertIn("MISSING_HEADING", result.stdout)

    def test_chapters_state_mismatch_fails(self) -> None:
        self.write_episode(1)
        result = self.run_cli()
        self.assertEqual(1, result.returncode)
        self.assertIn("STATE_MISMATCH", result.stdout)

    def test_invalid_episode_range_returns_usage_error(self) -> None:
        result = self.run_cli("--episodes", "5-1")
        self.assertEqual(2, result.returncode)
        self.assertIn("集数范围", result.stderr)

    def test_missing_source_directory_returns_usage_error(self) -> None:
        (self.root / "drafts").rmdir()
        result = self.run_cli("--source", "drafts")
        self.assertEqual(2, result.returncode)
        self.assertIn("目录不存在", result.stderr)


if __name__ == "__main__":
    unittest.main()

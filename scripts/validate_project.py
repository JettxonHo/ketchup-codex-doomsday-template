#!/usr/bin/env python3
"""末世重生漫剧项目的确定性校验器。"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Tuple


EPISODE_FILE = re.compile(r"^Episode-(\d{2})\.md$")
TITLE_PATTERN = re.compile(r"^#\s+第\d{2}集\s+.+", re.MULTILINE)
BODY_HEADING_PATTERN = re.compile(r"^##\s+正文\s*$", re.MULTILINE)
COMPLETED_PATTERN = re.compile(r"^completed_episodes:\s*\[(.*?)\]\s*$", re.MULTILINE)
MIN_LENGTH = 500
MAX_LENGTH = 800


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    path: str
    message: str

    def render(self) -> str:
        location = f" [{self.path}]" if self.path else ""
        return f"- {self.code}{location}: {self.message}"


def parse_episode_range(value: str) -> Tuple[int, int]:
    try:
        start_text, end_text = value.split("-", 1)
        start, end = int(start_text), int(end_text)
    except (ValueError, TypeError):
        raise argparse.ArgumentTypeError("集数范围格式必须为 N1-N2")
    if start < 1 or end > 60 or start > end:
        raise argparse.ArgumentTypeError("集数范围必须在 1-60 且起始集不大于结束集")
    return start, end


def visible_character_count(content: str) -> int:
    without_markdown = re.sub(r"^[#>*_`~-]+", "", content, flags=re.MULTILINE)
    return len(re.sub(r"\s+", "", without_markdown))


def read_completed_episodes(state_path: Path) -> Tuple[Optional[List[int]], Optional[ValidationIssue]]:
    if not state_path.is_file():
        return None, ValidationIssue("STATE_FILE", str(state_path), "缺少 project.yaml")
    try:
        content = state_path.read_text(encoding="utf-8")
    except OSError as error:
        return None, ValidationIssue("STATE_FILE", str(state_path), f"无法读取：{error}")
    match = COMPLETED_PATTERN.search(content)
    if not match:
        return None, ValidationIssue("STATE_FORMAT", str(state_path), "缺少 completed_episodes 整数数组")
    raw = match.group(1).strip()
    if not raw:
        return [], None
    values = [part.strip() for part in raw.split(",")]
    if any(not value.isdigit() for value in values):
        return None, ValidationIssue("STATE_FORMAT", str(state_path), "completed_episodes 只能包含整数")
    episodes = [int(value) for value in values]
    if len(set(episodes)) != len(episodes) or any(value < 1 or value > 60 for value in episodes):
        return None, ValidationIssue("STATE_FORMAT", str(state_path), "completed_episodes 必须是 1-60 内不重复的集数")
    return sorted(episodes), None


def validate_episode(path: Path) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        return [ValidationIssue("READ_ERROR", str(path), f"无法读取 UTF-8 文件：{error}")]
    if not TITLE_PATTERN.search(content):
        issues.append(ValidationIssue("MISSING_HEADING", str(path), "缺少“# 第NN集 标题”"))
    if not BODY_HEADING_PATTERN.search(content):
        issues.append(ValidationIssue("MISSING_HEADING", str(path), "缺少“## 正文”标题"))
    length = visible_character_count(content)
    if length < MIN_LENGTH or length > MAX_LENGTH:
        issues.append(ValidationIssue("WORD_COUNT", str(path), f"正文可见字符数为 {length}，要求 {MIN_LENGTH}-{MAX_LENGTH}"))
    if "※" not in content:
        issues.append(ValidationIssue("MISSING_SCENE_MARKER", str(path), "缺少场景标记 ※"))
    if "△" not in content:
        issues.append(ValidationIssue("MISSING_ACTION_MARKER", str(path), "缺少动作标记 △"))
    if "【卡黑】" not in content:
        issues.append(ValidationIssue("MISSING_CLIFFHANGER", str(path), "缺少结尾标记【卡黑】"))
    return issues


def discover_episodes(source_dir: Path) -> Tuple[dict, List[ValidationIssue]]:
    episodes = {}
    issues: List[ValidationIssue] = []
    for path in sorted(source_dir.iterdir()):
        if path.name == ".gitkeep" or not path.is_file():
            continue
        match = EPISODE_FILE.fullmatch(path.name)
        if not match:
            issues.append(ValidationIssue("INVALID_FILENAME", str(path), "文件名必须为 Episode-NN.md"))
            continue
        number = int(match.group(1))
        if number < 1 or number > 60:
            issues.append(ValidationIssue("INVALID_FILENAME", str(path), "集数必须在 01-60"))
            continue
        if number in episodes:
            issues.append(ValidationIssue("DUPLICATE_EPISODE", str(path), f"第 {number:02d} 集重复"))
            continue
        episodes[number] = path
    return episodes, issues


def validate_project(
    root: Path,
    source: str = "chapters",
    episode_range: Optional[Tuple[int, int]] = None,
) -> List[ValidationIssue]:
    source_dir = root / source
    if not source_dir.is_dir():
        raise FileNotFoundError(f"目录不存在：{source_dir}")
    episodes, issues = discover_episodes(source_dir)
    if episode_range is not None:
        expected = set(range(episode_range[0], episode_range[1] + 1))
        for number in sorted(expected - set(episodes)):
            issues.append(ValidationIssue("MISSING_EPISODE", str(source_dir), f"缺少 Episode-{number:02d}.md"))
        selected = sorted(expected & set(episodes))
    else:
        selected = sorted(episodes)
    for number in selected:
        issues.extend(validate_episode(episodes[number]))
    if source == "chapters":
        completed, state_issue = read_completed_episodes(root / "project.yaml")
        if state_issue:
            issues.append(state_issue)
        elif completed != sorted(episodes):
            issues.append(
                ValidationIssue(
                    "STATE_MISMATCH",
                    str(root / "project.yaml"),
                    f"状态记录 {completed} 与 chapters 文件 {sorted(episodes)} 不一致",
                )
            )
    return issues


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="校验末世重生漫剧项目文件")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="项目根目录")
    parser.add_argument("--source", choices=("drafts", "chapters"), default="chapters", help="正文来源目录")
    parser.add_argument("--episodes", type=parse_episode_range, help="集数范围，例如 1-5")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        issues = validate_project(args.root.resolve(), args.source, args.episodes)
    except (FileNotFoundError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    if issues:
        print(f"FAIL：发现 {len(issues)} 个问题")
        for issue in issues:
            print(issue.render())
        return 1
    print("PASS：确定性校验通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())

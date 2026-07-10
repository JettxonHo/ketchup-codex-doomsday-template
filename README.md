# KETC11UP：Codex 末世重生漫剧工作流模板

一套面向 60 集末世重生漫剧的 Codex 项目模板。它把专业创作、项目状态、格式检查和剧情一致性检查组合成可重复执行的工作流。

> 这里的 `/character`、`/catalog`、`/write` 等是本项目在 `AGENTS.md` 中约定的对话指令，不是 Codex 内置命令。

## 它能做什么

- 按“大纲 → 人物 → 目录 → 正文 → 全剧检查”推进项目；
- 调用 `doomsday-skill` 执行专业创作；
- 调用 `doomsday-aligner` 检查剧情和设定一致性；
- 使用 Python 脚本检查文件名、集数、字数及必要标记；
- 正文先进入 `drafts/`，双重检查通过后才发布到 `chapters/`；
- 提供可双击打开的 `新人操作手册.html`。

## 使用 GitHub 模板

仓库启用 Template Repository 后：

1. 点击 GitHub 页面右上方 **Use this template**；
2. 选择 **Create a new repository**；
3. 填写你的项目名称并创建仓库；
4. 将新仓库克隆到电脑；
5. 使用 Codex 打开新项目目录。

如果使用本地压缩包，直接解压并用 Codex 打开目录即可。

## 五分钟快速开始

### 1. 确认项目资源

项目根目录应包含：

```text
AGENTS.md
project.yaml
doomsday-skill/SKILL.md
doomsday-aligner/SKILL.md
scripts/validate_project.py
```

### 2. 打开新人手册

双击 `新人操作手册.html`。它不联网，可以生成启动提示词、复制指令并记录培训进度。

### 3. 在 Codex 中启动项目

告诉 Codex 以下三项：

- 核心创意；
- 金手指类型；
- 题材议题或故事调性。

示例：

```text
核心创意：女主前世被亲属赶出安全屋，在极寒中冻死，重生到末日前三个月。
金手指：玉镯空间，可储物且时间静止。
题材议题：囤货复仇，重点表现前世今生反差和物资碾压。
请按项目工作流创作完整故事大纲。
```

### 4. 按顺序执行

```text
/character
/catalog
/write 1
```

之后依次使用 `/write 2` 至 `/write 12`。不要跳过前置阶段。

### 5. 查看状态或检查

```text
/status
/check
```

也可以直接运行确定性校验：

```bash
python3 scripts/validate_project.py
```

## 十二个正文批次

| 批次指令 | 集数 | 所属幕 |
|---|---:|---|
| `/write 1` | 01—05 | 第一幕 |
| `/write 2` | 06—10 | 第一幕 |
| `/write 3` | 11—15 | 第一幕 |
| `/write 4` | 16—20 | 第一幕 |
| `/write 5` | 21—25 | 第二幕 |
| `/write 6` | 26—30 | 第二幕 |
| `/write 7` | 31—35 | 第二幕 |
| `/write 8` | 36—40 | 第二幕 |
| `/write 9` | 41—45 | 第二幕 |
| `/write 10` | 46—50 | 第三幕 |
| `/write 11` | 51—55 | 第三幕 |
| `/write 12` | 56—60 | 第三幕 |

## 质量门禁

```text
生成五集草稿
  → scripts/validate_project.py 检查硬规则
  → doomsday-aligner 检查剧情一致性
  → FAIL：返修并复查，最多三轮
  → PASS：发布到 chapters/ 并更新 project.yaml
```

正式正文已存在时，工作流默认停止，不会静默覆盖。

## 校验器用法

```bash
# 检查所有正式正文与 project.yaml 是否一致
python3 scripts/validate_project.py

# 检查第 1—5 集草稿
python3 scripts/validate_project.py --source drafts --episodes 1-5

# 检查全部正式正文
python3 scripts/validate_project.py --source chapters --episodes 1-60
```

退出码：`0` 表示通过，`1` 表示内容或状态问题，`2` 表示参数或运行环境问题。

## 项目目录

```text
drafts/       未通过双重检查的草稿
reviews/      Aligner 检查报告
chapters/     已通过双重检查的正式正文
scripts/      确定性校验工具
tests/        校验器测试
```

`outline.md`、`character.md` 和 `chapter_index.md` 会在对应阶段完成时创建，模板不会预建空文件。

## 运行测试

无需安装依赖：

```bash
python3 -m unittest discover -s tests -v
```

## 发布成 GitHub 模板

本项目整理完成后可推送到 GitHub，然后在仓库 **Settings** 中启用 **Template repository**。发布前需要确认：

- 仓库名称；
- 公开或私有；
- 是否采用开源许可证；
- 仓库中不包含创作成品、密钥、邮箱或本地绝对路径。

## 参与改进

请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。程序问题使用 Bug 表单，流程建议使用 Workflow Feedback 表单。


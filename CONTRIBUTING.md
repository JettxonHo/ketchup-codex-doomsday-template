# 贡献指南

感谢改进 FEICAI 工作流。提交修改前，请先判断变更属于哪个边界。

## 文件职责

- `AGENTS.md`：项目阶段、指令路由、文件读写和质量门禁；
- `doomsday-skill/`：创作方法论、写作风格、模板和示例；
- `doomsday-aligner/`：一致性检查规则；
- `scripts/validate_project.py`：可确定判断的格式与状态规则；
- `新人操作手册.html`：培训内容与浏览器交互；
- `project.yaml`：新项目初始状态。

语义判断不要塞进 Python 校验器；可以通过明确规则判断的内容不要只依赖模型审查。

## 修改原则

1. 保持 60 集、三幕和十二批次契约一致；
2. `/write` 参数统一称为“批次编号”；
3. 不修改无关方法论或示例；
4. 不引入第三方 Python、CSS 或 JavaScript 依赖；
5. HTML 必须断网可用；
6. 不提交实际剧本、账号、令牌、邮箱、`.env` 或本地绝对路径；
7. 新增确定性规则时必须同步添加单元测试；
8. 修改指令或批次时必须同步更新 `AGENTS.md`、`README.md` 和 `新人操作手册.html`。

## 本地检查

运行单元测试：

```bash
python3 -m unittest discover -s tests -v
```

检查空模板状态：

```bash
python3 scripts/validate_project.py
```

检查 Markdown 和 HTML 中是否误写本地绝对路径或常见密钥：

```bash
rg -n '/Users/|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|ghp_|github_pat_|sk-' .
```

检查 Git 空白错误：

```bash
git diff --check
```

## 修改 Skill

修改 `SKILL.md` 时：

- 保持触发条件清楚；
- 明确每个阶段必须读取的资源；
- 模板与示例只作为资源，不在入口文件重复全文；
- 变更创作硬规则时同步检查 Aligner 是否仍一致；
- 在 Issue 或提交说明中写清影响的大纲、人物、目录或正文阶段。

## 修改培训手册

- 使用语义化 HTML；
- 交互按钮必须可用键盘访问；
- 操作结果要有文字反馈，不能只使用颜色；
- 本地存储只使用本项目自己的键；
- 重置进度前必须二次确认；
- 禁用 JavaScript 后仍应能阅读完整教程。

## 提交建议

一个提交只解决一个逻辑问题。推荐格式：

```text
feat: 添加新的确定性检查
fix: 修正第十批集数映射
docs: 完善新人故障排查
```

提交 Issue 时不要粘贴包含隐私、商业剧本全文或访问令牌的日志。


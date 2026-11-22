---
name: blog-write-migrate-from-confluence
description: "Migrate one Confluence page (exported or pasted as Markdown) into this repository's knowledge base as a complete article rather than an AI-style summary or runbook: keep the original verbatim in resources/, interview the author for the missing background (project, reasons, alternatives, real pitfalls, what is still true), record it in plan.md, propose an outline mapped to the original, verify outdated facts, then rewrite README.md in the author's voice and run the checks. Use when the author pastes or points to a Confluence page and says 迁移, 迁过来, 从 Confluence 搬过来, migrate this page, 把这篇 Confluence 改成博文, usually with a target path under docs/source."
argument-hint: "<目标路径 docs/source/<分类>/<文档>/> <Confluence 页面 .md 内容或文件路径>"
---

# blog-write-migrate-from-confluence

把一篇 Confluence 页面迁进知识库, 改写成一篇有头有尾的文章. 原稿往往是作者当年用 AI 直接写的: 步骤齐全, 但没有背景, 没有判断, 读起来像摘要或 runbook. 这个 skill 的价值不在搬运, 在于**把原稿缺的东西从作者那里问出来**, 再按知识库的规范重写.

先读 [../blog-base/SKILL.md](../blog-base/SKILL.md), 再读:

- [../blog-base/ref/03-workflow/01-lifecycle.md](../blog-base/ref/03-workflow/01-lifecycle.md)
- [../blog-base/ref/03-workflow/02-writing-process.md](../blog-base/ref/03-workflow/02-writing-process.md)
- [../blog-base/ref/01-strategy/01-positioning.md](../blog-base/ref/01-strategy/01-positioning.md)
- [../blog-base/ref/02-spec/01-repository-layout.md](../blog-base/ref/02-spec/01-repository-layout.md)
- [../blog-base/ref/02-spec/02-metadata.md](../blog-base/ref/02-spec/02-metadata.md)
- [../blog-base/ref/02-spec/03-language-punctuation.md](../blog-base/ref/02-spec/03-language-punctuation.md)
- [../blog-base/ref/02-spec/04-tone.md](../blog-base/ref/02-spec/04-tone.md)
- [../blog-base/ref/02-spec/05-resources.md](../blog-base/ref/02-spec/05-resources.md)
- [../blog-base/ref/02-spec/06-plan.md](../blog-base/ref/02-spec/06-plan.md)
- [../blog-base/ref/02-spec/07-readme-body.md](../blog-base/ref/02-spec/07-readme-body.md)
- [../blog-base/ref/02-spec/09-checklist.md](../blog-base/ref/02-spec/09-checklist.md)

要用 MyST 指令时, 看 `sphinx-myst-kb-site` skill 的 `examples/docs-source/01-feature-demo/`.

按这些文档做. 下面只记迁移特有的做法.

## 0. 拿齐输入

输入: `$ARGUMENTS` 和作者在对话里贴的内容. 需要两样:

1. **原稿.** 作者贴进来的 Markdown, 或者一个 `.md` 文件路径. 作者只给了 Confluence 链接: 请作者导出或复制成 Markdown 贴过来, 不要自己去登录 Confluence 抓.
2. **放在哪.** 作者通常会给 `docs/source/<分类>/<文档>/README.md` 这样的路径. 没给就用 `list-categories` 列出现有分类问作者. 路径里的分类不存在: 告诉作者, 确认分类名和两句话描述后用 `new-category` 建.

顺手问一句 (可以不答): Confluence 页面的链接, 最后修改日期. 用来填原稿的 `source_url` 和 `published_at`.

## 1. 读原稿, 给作者一个诊断

通读原稿, 用五六行告诉作者你看到了什么, 不要复述内容:

- 这是什么类型 (见第 4 步的表): 操作和实施记录, 原理讲解, 选型对比, 排错记录, 速查清单, 还是几样混在一起.
- 可以直接用的: 哪些事实, 步骤, 代码, 判断是实打实的.
- 缺的: 背景 (为什么写, 在什么场景下), 判断 (为什么这么选), 真实的经历和坑, 结尾.
- 可疑的: 看起来是 AI 补全的部分 (编出来的数字, 泛泛的 "下一步", 把所有可能的选项都列一遍), 可能过时的事实, 编不过的代码.
- 体量: 原稿多长, 是不是一篇装了好几件事, 值不值得拆成几篇 (拆不拆由作者定).

## 2. 建目录, 存原稿

1. 用作者给的路径跑 `new-post`. slug 取路径最后一段, 标题先用原稿的 H1, `description` 先写一个临时的两句话.
2. 把原稿**一字不改**写进 `resources/confluence-<slug>.md`, 按 `05-resources.md` 补 front matter: `source_type: "confluence"`, `author` 填作者本人的名字 (`pyproject.toml` 的 `authors`; 作者说不是自己写的再改), `title` 是原稿 H1, `intake_at` 是今天, `note: "从 Confluence 迁移的原稿"`. 原稿里的格式问题也原样留着.
3. 在 `plan.md` 里记: `种子` 写 "从 Confluence 迁移: <原稿标题>", `素材怎么用` 加一行, 用法是 "改写", 用在 "全篇".

```bash
python3 .claude/skills/blog-base/scripts/blog_utils.py new-post --parent <分类路径> --slug <slug> --title "<原稿 H1>" --description "<临时的两句话>"
python3 .claude/skills/blog-base/scripts/blog_utils.py check --path <文档目录>
```

## 3. 采访作者, 补背景

这是本 skill 最重要的一步. 按 `02-writing-process.md` 第 1 节的规则 (一次三到五个问题, 答了马上记进 `plan.md`, 不编). 迁移时优先问这几个, 按原稿内容改写得具体一点:

1. 这篇当时是在什么场景下写的 (哪个项目, 哪个问题, 学什么东西)? 那件事后来怎么样了?
2. 原稿里哪些是你真的做过, 验证过, 想清楚的; 哪些是当时 AI 顺手补全的?
3. 原稿里的关键选择 (方案, 工具, 做法), 当时为什么这么选, 比较过别的吗?
4. 实际做的时候, 或者理解这件事的时候, 哪里最难, 踩了什么坑?
5. 现在回头看, 结论还成立吗? 什么情况下不适用?
6. 这篇以后主要给谁看: 自己查, 给 agent 读, 还是要发给别人?

不是每题都适用: 原理讲解类的原稿没有 "做的时候", 速查清单类的原稿可能只需要第 1, 2, 6 题. 挑适用的问, 并按原稿内容问得具体: 点名原稿里的具体选择和步骤, 而不是照搬上面的措辞.

一般问两轮就够. 作者说 "就这些" 或 "跳过", 就带着已有的信息往下走; 背景缺的部分在正文里诚实地少写, 不要编一个. 第 2 题的答案决定原稿哪些内容能当成作者的经验写, 哪些只能当成一般做法写, 甚至删掉.

## 4. 提纲: 对着原稿逐节交代

按 `02-writing-process.md` 第 2 节给提纲, 另外附一张对照表, 让作者一眼看清原稿去哪了:

| 原稿的节 | 去向 | 说明 |
| :--- | :--- | :--- |
| <原稿的节> | 保留, 改名为 "## <新标题>" | <为什么> |
| <原稿的节> | 合并进 "## <新标题>" | <为什么> |
| <原稿的节> | 压缩成一两句 | <比如: 官方文档查得到, 给链接> |
| <原稿的节> | 删 | <比如: 泛泛的清单, 作者没做过> |

原稿的每一节都要在表里出现, 不能悄悄丢.

结构从内容里长出来, 不要套模板. 下面是几类常见原稿的参考骨架, 只在拿不准时参考, 混合型的原稿按主要用途选或者组合:

| 原稿类型 | 参考骨架 |
| :--- | :--- |
| 操作和实施记录 | 开头 (问题, 背景, 结论) → 整体思路和关键机制 → 实施步骤 → 坑和排查 → 结尾 (适用边界) |
| 原理讲解 | 开头 (为什么要搞懂它) → 核心概念 → 机制一步步拆开 → 常见误解 → 结尾 (怎么用这个理解做判断) |
| 选型对比 | 开头 (要解决什么, 约束是什么) → 候选和评判标准 → 逐项对比 → 最后的选择和理由 → 结尾 (什么情况下会选别的) |
| 排错记录 | 开头 (现象和影响) → 排查过程 → 根因 → 修复 → 结尾 (怎么防止再发生) |
| 速查清单 | 开头 (什么时候查这篇) → 按场景分组的条目 → 结尾 (容易用错的地方). 清单本身可以保留列表或表格形式, 但开头和结尾不能省 |

原稿是一篇装了几件事的, 在这里提出拆成几篇, 作者决定.

作者点头才写.

## 5. 核实可能过时的事实

原稿里的版本号, API 和命令参数, 界面菜单名, 价格和限额, 都可能过时. 正文要用到的, 查官方文档核实 (WebSearch / WebFetch); 核实到变化的, 按现在的写, 并在 `plan.md` 的 `随手记` 记一句改了什么. 核实不了的, 在正文里写明 "以 YYYY-MM 时为准". 不需要的细节直接不写, 也就不用核实.

## 6. 写

按 `02-writing-process.md` 第 3, 4 节和 `07-readme-body.md` 写进 `README.md`. 迁移时再注意这些 Confluence 导出的毛病, 一律在新正文里改掉 (原稿那份不动):

| Confluence 导出的样子 | 新正文 |
| :--- | :--- |
| ``` `` code `` ``` 两层反引号加空格 | `` `code` `` |
| 整段, 整节, 标题都包在 `**...**` 里 | 去掉加粗 |
| 嵌套列表被拍平, 编号列表从 1 重新开始 | 按意思重排, 能写成段落的写成段落 |
| 代码块没有语言标记 | 标上对应的语言, 不知道就用 `text` |
| 节与节之间的 `---` | 删掉, H2 就是分隔 |
| 信息面板, 警告面板 (常导出成 ⚠️ 加粗段落) | ```` ```{note} ```` / ```` ```{warning} ```` |
| 残留的 `<https://...>`, `\_` 之类的转义 | 修好 |

原稿有代码或命令时: 留下这篇真正要讲的, 修掉跑不通的地方 (缺依赖, 用了没定义的名字, 废弃的 API), 修不了就说明是片段. 同一件事给了好几种写法时, 保留作者实际用的那种 (问过第 2 题就知道), 其他一句话带过或用 `tab-set`.

## 7. 收尾

按 `02-writing-process.md` 第 5 节: 文风自检, 改准 `description` 和 `tags`, `updated_at` 改成今天, 中文文档跑 `c2ep`, 过 `09-checklist.md`. 迁移的文档通常会用到新的 MyST 写法, 所以除了 `check` 和 `lint-doc`, 也跑一次 `build-doc`:

```bash
uvx --from "chinese_to_english_punctuation>=0.1.3" c2ep file --skip_code --path <文档目录>/README.md --dry_run
uvx --from "chinese_to_english_punctuation>=0.1.3" c2ep file --skip_code --path <文档目录>/README.md
python3 .claude/skills/blog-base/scripts/blog_utils.py check --path <文档目录>
mise run lint-doc
mise run build-doc
```

## 8. 告诉作者

- 文档路径和 `doc_id`.
- 新文章的 H1 和 H2.
- 原稿删了什么, 为什么 (对照第 4 步的表).
- 从采访里补进了什么.
- 核实后改了哪些过时的事实, 哪些没核实到.
- `plan.md` 的 `没想清楚的` 里还剩什么等作者补.

提醒作者: push 到 main 就会上线; Confluence 上的原页面要不要删或者加一个指向 kb 的链接, 由作者自己处理.

## 边界

- `resources/confluence-*.md` 写进去之后不再改.
- 不替作者编经历, 不把 "AI 当年补全的" 内容写成作者的经验.
- 一次只迁一篇. 作者给了好几篇, 一篇一篇来, 每篇都走完采访.
- 不碰 Confluence 本身. 不 commit, 不 push, 除非作者要求.

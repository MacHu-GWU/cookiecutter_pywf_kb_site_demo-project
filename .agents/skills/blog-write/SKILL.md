---
name: blog-write
description: "Main writer for this repository's knowledge base: write the body of a document (docs/source/.../README.md, MyST Markdown) in the author's own voice from its plan.md and resources/, as a complete article with background, judgement and an ending rather than a summary or runbook; or turn an existing rough body into a finished one; then fix description, tags and updated_at and run the checks. Use when the author says 写正文, 写这篇, 起草, draft, 开始写, 按我的风格改一下, 打磨, 帮我改这篇, for a knowledge base document. For a Confluence page use blog-write-migrate-from-confluence instead."
---

> Usage: `/blog-write <doc_id 或文档目录>`

# blog-write

知识库的主力写作 skill: 按 `plan.md` 和 `resources/` 写出一篇符合知识库规范, 用作者自己文风, 有头有尾的正文 (`README.md`). 正文已经有了 (作者自己写的粗稿, 或者以前随手写的), 就把它改成规范稿.

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

要用 MyST 指令 (tab-set, mermaid, literalinclude 等) 时, 再看 `sphinx-myst-kb-site` skill 的 `examples/docs-source/01-feature-demo/` 里对应的演示文档.

按这些文档写. 下面只记本 skill 自己的做法.

## 1. 找到这篇, 判断走哪种模式

输入: `$ARGUMENTS`. 用 `get` 找到它. 只给了一个新主题, 还没有目录, 就告诉作者先用 `blog-plan` (或者 `blog-intake`) 起个头; 作者坚持直接写, 就问清分类, 确认 slug, 标题和临时 `description` 后跑 `new-post`.

```bash
python3 .agents/skills/blog-base/scripts/blog_utils.py get --doc_id <doc_id>
```

作者给的是一份 Confluence 页面: 改用 `blog-write-migrate-from-confluence`.

看 `README.md` 的 H1 下面有没有正文:

- **没有正文: 走 A. 从 plan 写.**
- **有正文: 走 B. 改成规范稿.** 先问作者一句: 这份正文的观点和结构要保留, 还是可以重排. 作者没说就保留.

## A. 从 plan 写

1. **读 plan.** `背景` 或 `核心观点` 是空的, 先提醒作者跑 `blog-plan`. 作者坚持直接写, 就按 `02-writing-process.md` 第 1 节当场把背景问出来, 记进 `plan.md`.
2. **读素材.** `素材怎么用` 表里标了 "改写", "引用" 和 "提到" 的素材读全文. "背景" 的看需要读. 没进表的不用.
3. **给提纲, 作者点头再写.** 按 `02-writing-process.md` 第 2 节.
4. **写全文.** 按 `02-writing-process.md` 第 3 节和 `07-readme-body.md`, 写在 `README.md` 的 H1 下面.

## B. 改成规范稿

1. **读完现有正文, 再读 plan 和素材.** 正文里有, plan 里没有的观点, 记进 `plan.md` 的 `随手记`, 不要丢. 缺背景就按 `02-writing-process.md` 第 1 节问.
2. **给改稿提纲, 作者点头再改.** 标出哪几节是原有的, 哪几节合并, 拆开, 新加, 删掉.
3. **改全文.** 按 `02-writing-process.md` 第 3, 4 节. 作者的原话, 真实经历, 数字和判断尽量留着.

## 2. 收尾

按 `02-writing-process.md` 第 5 节: 文风自检, 改准 `description` 和 `tags`, `updated_at` 改成今天, 中文文档跑 `c2ep` 并检查误伤, 过 `09-checklist.md`, 再跑:

```bash
uvx --from "chinese_to_english_punctuation>=0.1.3" c2ep file --skip_code --path <文档目录>/README.md --dry_run
uvx --from "chinese_to_english_punctuation>=0.1.3" c2ep file --skip_code --path <文档目录>/README.md
python3 .agents/skills/blog-base/scripts/blog_utils.py check --path <文档目录>
mise run lint-doc
```

用了新的 MyST 写法, 新分类, 或者改动很大时, 再跑 `mise run build-doc` 确认没有 warning.

## 3. 告诉作者

文档路径, 写了哪几节, (改稿时) 删了什么, 还有哪些点等作者补. kb 默认不配图 (见 `08-images.md`), 不要问要不要配图; 只在最后提一句: 需要配图可以用 `blog-add-images`. 提醒作者: push 到 main 就会自动部署.

## 边界

- 只写 `README.md` 正文和 front matter 的 `description` / `tags` / `updated_at`, 以及 `plan.md`. 不改 `resources/`, 不改 `doc_id` 和 `created_at`.
- 不 commit, 不 push, 不跑 `deploy-doc`, 除非作者明确要求.

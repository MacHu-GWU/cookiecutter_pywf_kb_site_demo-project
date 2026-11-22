---
name: blog-plan
description: "Work out what a knowledge base document will say, with the author, and keep its plan.md up to date as ideas come up: seed, background (project, constraints, alternatives, pitfalls), reader, core point, points in order, how each resource is used. Use when the author says 计划, plan, 理一理思路, 我想写个什么, 聊聊这篇怎么写, or starts talking through an idea for a knowledge base document."
---

> Usage: `/blog-plan <doc_id 或文档目录 或想法>`

# blog-plan

陪作者理清一篇文档要说什么, 把背景问出来, 边聊边把想法写进 `plan.md`.

先读 [../blog-base/SKILL.md](../blog-base/SKILL.md), 再读:

- [../blog-base/ref/03-workflow/01-lifecycle.md](../blog-base/ref/03-workflow/01-lifecycle.md)
- [../blog-base/ref/03-workflow/02-writing-process.md](../blog-base/ref/03-workflow/02-writing-process.md) (第 1 节: 怎么问背景)
- [../blog-base/ref/01-strategy/01-positioning.md](../blog-base/ref/01-strategy/01-positioning.md)
- [../blog-base/ref/02-spec/01-repository-layout.md](../blog-base/ref/02-spec/01-repository-layout.md)
- [../blog-base/ref/02-spec/03-language-punctuation.md](../blog-base/ref/02-spec/03-language-punctuation.md)
- [../blog-base/ref/02-spec/05-resources.md](../blog-base/ref/02-spec/05-resources.md)
- [../blog-base/ref/02-spec/06-plan.md](../blog-base/ref/02-spec/06-plan.md)

按这些文档做. 下面只记本 skill 自己的做法.

## 1. 进场

输入: `$ARGUMENTS`.

- 是已有的文档: `get` 找到它, 读 `plan.md`, 再看 `resources/` 下每个文件的 frontmatter (`title`, `note`). 素材全文等聊到相关的点再读.
- 是一个想法, 还没有目录: 先听作者把想法说完. 问作者放在哪个分类下 (`list-categories`), 按 `01-repository-layout.md` 起英文 slug, 连同暂定标题和临时 `description` 给作者确认, 跑 `new-post`, 把作者的原话记进 `种子`.
- 跑一次 `search`, 看看知识库里有没有写过相关的, 有就告诉作者, 并问这篇要不要用 `{ref}` 链过去.

进场后用两三句话告诉作者 plan 现在的状态: 哪几节有内容, 哪几节是空的, 有几份素材还没决定怎么用.

```bash
python3 .agents/skills/blog-base/scripts/blog_utils.py get --doc_id <doc_id>
python3 .agents/skills/blog-base/scripts/blog_utils.py search --query "<关键词>" --k 20
python3 .agents/skills/blog-base/scripts/blog_utils.py new-post --parent <分类路径> --slug <english-slug> --title "<暂定标题>" --description "<临时的两句话>"
```

## 2. 边聊边落盘

这是本 skill 的核心. 作者说到哪, 想到哪, 一有成形的东西就写进 `plan.md`, 不要攒到最后:

- 能归到某一节的, 直接写进那一节.
- 归不了的, 先记进 `随手记`. 后面想清楚了再挪到对应的节, 并从 `随手记` 删掉.
- 写完用一行告诉作者改了哪一节, 不要把整份 plan 复述一遍.
- 记作者的意思, 尽量保留作者的原话, 不要改写成书面语.

你自己可以提建议: 观点哪里不清楚, 哪份素材能撑哪个点, 这篇和哪篇已有文档重叠. 但**建议要作者点头才写进去**, 没点头的放进 `没想清楚的`, 标明是你的建议.

## 3. 帮作者往前推

聊天停住的时候, 按这个顺序找下一个要问的问题:

1. `背景` 是空的或很薄: 按 `02-writing-process.md` 第 1 节的问题问, 一次三到五个.
2. `核心观点` 还说不成一句话: 帮作者收敛.
3. `读者` 是空的: 问这篇主要给谁看.
4. `要讲的点` 没排顺序, 或者某个点没有素材撑着: 指出来.
5. `resources/` 里有素材没进 `素材怎么用` 那张表: 读一下素材, 提议它是改写, 引用, 提到还是背景.

缺素材就建议作者去找, 找到了用 `blog-intake` 收进来.

## 4. 收尾

`背景`, `核心观点`, `要讲的点` 都有内容了, 就告诉作者可以用 `blog-write` 开始写正文了. 作者想继续聊就继续.

## 边界

- 只写 `plan.md`. 不写 `README.md` 正文 (新建时 `new-post` 生成的骨架除外), 不改 `resources/` 里的素材.
- `plan.md` 的标点也按 `03-language-punctuation.md`, 用英文半角.

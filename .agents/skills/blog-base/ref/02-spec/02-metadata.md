# Spec: 文档的 metadata

> 管辖范围: `README.md` 的 YAML front matter 有哪些字段, 每个写什么. 格式的硬规则 (哪些值必须加引号, 为什么) 由 `sphinx-myst-kb-site` skill 和它的 `lint_docs.py` 定义, 本文不重复, 只记本 family 的约定. `.rst` 和 `.ipynb` 的 metadata 放在各自格式的位置 (顶部 field list, notebook metadata), 字段相同.

---

## 1. 模板

模板在 `assets/readme-template.md`, `new-post` 自动填好:

```markdown
---
doc_id: aBcDeFgHiJkL
description: "<第一句: 讲了什么>. <第二句: 是什么样的文档>."
tags: [<tag>, <tag>]
created_at: "2026-11-06"
updated_at: "2026-11-06"
---

# 文档标题
```

字段只有这五个, 按这个顺序. 要加字段, 先改本文和模板.

---

## 2. 字段

| 字段 | 写什么 | 谁写 |
| :--- | :--- | :--- |
| `doc_id` | 12 位 `[A-Za-z]` 随机串, 一辈子不改, 不复用. 裸值, 不加引号 | `new-post` 生成 |
| `description` | 一行, 双引号, 至少两句话: 这篇讲什么, 这是一篇什么样的文档 | 建目录时写临时的, `blog-write` 写完正文改准 |
| `tags` | `[a, b]`, 小写英文单词, 可以是 `[]` | `blog-write` |
| `created_at` | 建目录那天, `"YYYY-MM-DD"`, 双引号. 之后不改 | `new-post` |
| `updated_at` | 最后一次改正文内容的日期, 双引号 | 每次改正文的 invoker |

### description

它给两个地方用: 站内搜索里只命中标题的结果下面那行说明 (`kb-titles.json`), 以及 `llms.txt` 里每篇文档后面的那句话. 最后一个最重要: agent 只读 `llms.txt` 就要能判断 "这篇和我手上的事有没有关系", 不用打开全文.

- 第一句: 讲了什么. 点名具体的技术, 场景和核心结论, 让人不打开全文也知道这篇能不能回答手上的问题. 不写 "本文介绍了..." 这种空话.
- 第二句: 是什么样的文档. 比如 "是一篇带完整代码的实战记录.", "是一篇选型判断.", "是一篇原理讲解.", "是一篇排错记录.", "是一个分类的目录页."
- 不能有双引号, 不能换行. 句子用英文半角 `.` 加空格结尾 (lint 按这个数句子).

### created_at / updated_at

本 family 用 `created_at` / `updated_at`, 和 `sphinx-myst-kb-site` 的示例一致.

只改错别字可以不动 `updated_at`. 只改 `plan.md` 或 `resources/` 不算改正文.

**迁移来的文档** (比如从 Confluence): `created_at` 是在 kb 里建目录那天, 不是原文的日期. 原文的日期记在 `resources/` 里那份原稿的 `published_at` 上.

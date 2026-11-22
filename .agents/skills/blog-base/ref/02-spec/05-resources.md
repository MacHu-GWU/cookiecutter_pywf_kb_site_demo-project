# Spec: resources/ 素材

> 管辖范围: 一篇文档的 `resources/` 目录里放什么, 每份素材长什么样. 它不进网站 (见 [01-repository-layout.md](01-repository-layout.md) 第 2 节).

---

## 1. 放什么

写这篇时收进来的**别人的东西, 以及作者以前写的旧稿**: 博文, 官方文档, 视频字幕, 论文, 社交媒体帖子, 从 Confluence 等地方迁过来的原稿. 作者这次的想法不放这里, 放 `plan.md`.

- 每份素材一个 `.md` 文件, 正文是原文转成的 Markdown.
- 原始文件 (PDF, 截图, 网页存档) 可以一起放, 和对应的 `.md` 同名: `<name>.pdf` 配 `<name>.md`.
- 单个文件超过约 10 MB 不放进来, 只留 `.md`, 用 `source_url` 指过去.

---

## 2. 文件名

`<作者或来源>-<内容概括>.md`, 英文小写加 `-`: 官方文档写成 `<产品>-docs-<主题>.md`, 某人的文章写成 `<作者>-<主题>.md`, 视频写成 `<频道>-<主题>.md`. 重名加 `-2`.

- **文件名里不放日期.** 日期都在 frontmatter 里.
- **永远不叫 `README.md`**, 否则会被当成一篇文档.
- 从 Confluence 迁过来的原稿统一以 `confluence-` 开头.

---

## 3. 模板

模板在 `assets/resource-template.md`:

```markdown
---
title: ""
source_url: ""
source_type: ""
author: ""
published_at: ""
intake_at: ""
note: ""
---

原文 ...
```

| 字段 | 写什么 |
| :--- | :--- |
| `title` | 原文标题, 保持原文语言 |
| `source_url` | 原文链接. 作者直接贴进来的文字或本地文件填 `""` |
| `source_type` | `article`, `video`, `podcast`, `paper`, `doc`, `social`, `confluence`, `other` 之一 |
| `author` | 原作者或机构. 作者自己的旧稿填作者本人的名字 (`pyproject.toml` 的 `authors`). 不知道就 `""` |
| `published_at` | 原文发表或最后修改的日期 `YYYY-MM-DD`, 查不到就 `""` |
| `intake_at` | 收进来的日期 `YYYY-MM-DD`, 必填 |
| `note` | 一句话: 为什么收它, 作者当时怎么说的 |

所有值都用双引号, 每个字段一行. 这个文件不进网站, 但 `blog_utils.py check` 会检查字段齐不齐.

---

## 4. 正文

- **原样保留.** 不翻译, 不改写, 不总结, 不跑 `c2ep`. 要总结要评论, 写到 `plan.md`. Confluence 原稿里的格式问题 (乱加粗, 坏掉的列表) 也原样留着, 那是改写时要处理的事.
- 只抓到一部分 (付费墙, 字幕缺失) 时, 在正文第一行写 `> 只抓到了 ...`.
- 网页导航, 广告, 评论区删掉.

正文里要用别人的原文时, 只引短句并注明出处. 怎么用每份素材, 在 `plan.md` 里定.

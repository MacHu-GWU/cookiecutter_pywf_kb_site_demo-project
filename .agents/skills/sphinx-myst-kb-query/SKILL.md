---
name: sphinx-myst-kb-query
description: "Answer questions from the knowledge base site https://kb-site-seed-demo.pages.dev: read its llms.txt index, fetch the plain text of the relevant documents, answer in the user's language and cite the pages. Use when the user asks what the knowledge base says about something, or says 查一下知识库, 知识库里怎么说, 我的 KB 里有没有, search the knowledge base."
---

> Usage: `/sphinx-myst-kb-query [question]`

# sphinx-myst-kb-query

只根据 https://kb-site-seed-demo.pages.dev 线上已发布的文档回答, 不用训练数据冒充. 只读, 不写文档.

问题: $ARGUMENTS (为空就用对话里的提问)

## 1. 读索引

```bash
curl -sS https://kb-site-seed-demo.pages.dev/llms.txt
```

用 `curl`, 不要用 WebFetch: WebFetch 会先让模型摘要, 可能丢行和链接. 文件只有几 KB, 每次整份读完, 不要凭记忆.

每行一篇文档, 缩进是目录层级 (上一级是分类页):

```text
- [标题](https://kb-site-seed-demo.pages.dev/p/<doc_id>.md): 两句话的 description
```

## 2. 挑文档

- 按标题和 description 挑 1 到 3 篇. 文档的语言可能和提问不同, 技术名词通常保留英文: 先把关键词翻成文档的语言, 英文名词原样也匹配一遍.
- `Feature Demo` 和 `Deep Nesting` 两个分类是网站本身的功能演示, 不是知识. 除非问的是这个知识库怎么搭的, 否则跳过.
- 定位不到具体文档, 就读最接近的分类页再往下找.

## 3. 读正文

```bash
curl -sS https://kb-site-seed-demo.pages.dev/p/<doc_id>.md
```

- 返回 200 的纯文本, 不是跳转: MyST Markdown, 少数是 reST, notebook 是构建时生成的 Markdown 副本 (长输出被截断, 图片不含).
- 正文里的 {ref}`<doc_id>` 是指向另一篇文档的链接, 用同样的地址读它.
- 没答完就换关键词或沿链接继续, 直到答完或确认知识库里没有.

## 4. 回答

- 用用户的语言回答. 每个要点后附来源的网页地址 `https://kb-site-seed-demo.pages.dev/p/<doc_id>` (去掉 `.md`, 浏览器会跳到真正的页面).
- 没找到就说 "知识库里没有找到", 列出查过的文档. 用自己的知识补充时, 标明哪部分不来自知识库.
- 在知识库自己的仓库里工作时, `docs/source/` 可能有还没发布的改动. 问的是线上知识库就以线上为准, 两边不一致时告诉用户.

## 和首页提示词保持一致

首页 AI Reader 的提示词 (`cookiecutter_pywf_kb_site_demo/ai_reader.py` 的 `build_ai_site_prompt`) 是这个 skill 的浓缩版, 给没有这个 skill 的聊天机器人用. 改了这里的流程, 同步改那里.

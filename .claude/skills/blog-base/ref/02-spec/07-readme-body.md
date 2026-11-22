# Spec: README.md 的正文

> 管辖范围: front matter 之后的部分: 标题, 开头, AI 伴读链接, 能用哪些 MyST 写法, 怎么链接别的文档, 什么不能放进正文. 语言和腔调见 [03-language-punctuation.md](03-language-punctuation.md) 和 [04-tone.md](04-tone.md). MyST 每个功能的具体语法和坑, 看 `sphinx-myst-kb-site` skill 的 `examples/docs-source/01-feature-demo/` 和 `references/gotchas.md`.

---

## 1. 格式

默认写 `README.md` (MyST Markdown). 只有作者要求, 或者正文的核心是一段要带着运行结果看的代码时, 才用 `README.ipynb`. 新文档不写 `.rst`.

---

## 2. H1 和开头

- 每篇只有一个 H1, 就是标题, 紧跟在 front matter 后面. lint 要求第一个标题就是 H1.
- H1 是直白的判断句或清楚的名词短语, 不用比喻. 知识库允许 "XX 怎么接到 YY" 这种查东西的人会搜的写法.
- **H1 下面紧接着就是开头段**: 一两段交代问题, 背景, 这篇的结论或读完能得到什么. 不放 "概述" 这种 H2.

---

## 3. AI 伴读链接: 构建时自动加, 不要手写

每个页面在 H1 正下方都有一行 AI 伴读链接 (`🌐 AI Reader`), 点开后可以在 Claude, ChatGPT, Gemini 等任意 AI 里把这篇翻成英文或者边读边问. 链接的编码和 `esc_mini_tools_chatbot_deeplink` 的 deep link 一样.

- **它由 Sphinx 扩展 `cookiecutter_pywf_kb_site_demo.sphinx_ext` 在构建时根据 `doc_id` 生成并插到 H1 下面**, 所有格式 (`.md`, `.rst`, `.ipynb`) 都有. 源文件里不写.
- 链接里的提示词只给 AI 一个地址: `https://cookiecutter-pywf-kb-site-demo.sanhe.me/p/<doc_id>.md` (这篇的纯文本, notebook 是它的 Markdown 副本; 不提 HTML 网页), 所以文件夹搬家也不失效.
- 首页 (`docs/source/README.md`) 例外: 没人会针对首页本身提问, 所以首页的链接是 "Ask AI about this whole knowledge base", 提示词让 AI 从 `https://cookiecutter-pywf-kb-site-demo.sanhe.me/llms.txt` 出发检索全站来回答问题.
- **不要在源文件里手写这一行.** `blog_utils.py check` 发现源文件里有 deep link 的 URL 会报 ERROR.

---

## 4. 链接别的文档: 只用 doc_id

- 整篇: `` {ref}`<doc_id>` ``, 链接文字自动取对方的标题. 自定义文字: `` {ref}`文字 <doc_id>` ``.
- 某一节: 在那个标题上一行写 `(<doc_id>-<英文 slug>)=`, 再 `` {ref}`<doc_id>-<slug>` ``. 中文标题必须这么做, `[文字](#标题)` 只对英文标题有效.
- 不要用相对路径链接别的文档. 路径会因为搬家断掉, doc_id 不会.
- 要找一篇文档的 doc_id: `blog_utils.py search --query <关键词>`.

---

## 5. 标题层级

- 大节用 H2, 小节用 H3. 右侧的 "On this page" 只显示 H2 和 H3.
- H4 可以用, 但它不进导航, 少用. 感觉需要 H5, 说明这一节太密了: 拆开, 或者单独写一篇再用 `{ref}` 链过去.
- H2 和 H3 写成直白的判断句或动作短语, 只读标题能串起全篇.

---

## 6. 能用的写法

知识库不像博客那样只能贴进博客平台, 下面这些都能用, 按需要选, 不要为了用而用:

| 需要 | 用 |
| :--- | :--- |
| 提醒, 警告, 补充说明 | ```` ```{note} ````, ```` ```{warning} ````, ```` ```{tip} ```` (代替满屏的加粗和 ⚠️) |
| 同一件事的几种写法 (不同操作系统, 语言, 工具) | sphinx-design 的 `tab-set` |
| 流程, 架构, 时序 | ```` ```mermaid ```` |
| 对比, 清单 | Markdown 表格 |
| 很长的代码 | 放成文档目录下的单独文件, 用 `literalinclude` 引一部分 |
| 公式 | `$...$`, `$$...$$` |

代码块:

- 每个代码块都标语言 (` ```python `, ` ```bash `, ` ```text `).
- 代码前面一句话说它干什么, 后面说要注意什么. 不要连着贴三段代码不说话.
- 不贴编不过的代码: 缺 import, 用了没定义的名字, 官方已经标为废弃的 API 要修掉或者明确标出来.

---

## 7. 正文里不放的东西

- 属性区 ("作者", "更新时间", "本文链接"): 都在 front matter 里, 页面顶部的 doc_id 栏也会显示.
- 写作计划, 素材笔记, 给 AI 的指令: 留在 `plan.md`.
- 结尾的 "祝你开发顺利", "如果有问题请查阅文档" 这种客套话.

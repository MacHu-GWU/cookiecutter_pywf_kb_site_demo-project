---
name: blog-add-images
description: "Add images to a knowledge base document, only when the author asks: design and generate a cover (cover.jpeg) and section images for key H2s (img/NN-section-<slug>.jpeg) in the editorial-ink-art style, embed them in README.md, and compress every image in place with imgsqueeze. Image generation only runs in the Antigravity IDE; in Claude Code it is skipped and only embedding and compression of images the author added are done. Use when the author says 配图, 加图片, 给这篇配图, 画个封面, 重画某一节的图, for a knowledge base document."
argument-hint: "<doc_id 或文档目录> [all | cover | section-XX...]"
---

# blog-add-images

给一篇写好的文档配图: 封面和核心 H2 的章节图, 嵌进 `README.md`, 再把所有图压缩一遍. kb 默认不配图, 只在作者要求时做.

先读 [../blog-base/SKILL.md](../blog-base/SKILL.md), 再读:

- [../blog-base/ref/02-spec/01-repository-layout.md](../blog-base/ref/02-spec/01-repository-layout.md)
- [../blog-base/ref/02-spec/07-readme-body.md](../blog-base/ref/02-spec/07-readme-body.md)
- [../blog-base/ref/02-spec/08-images.md](../blog-base/ref/02-spec/08-images.md)
- [../editorial-ink-art/SKILL.md](../editorial-ink-art/SKILL.md) 和 [references/style-spec.md](../editorial-ink-art/references/style-spec.md) (只在要生图时读)
- [../pypi-imgsqueeze/SKILL.md](../pypi-imgsqueeze/SKILL.md)

按这些文档做. 下面只记本 skill 自己的做法.

## 0. 先看你在哪里运行

**只有在 Antigravity IDE 里才生图.** 你是 Claude Code, 或者手上没有生图工具, 就跳过第 2, 3 步, 不要用别的办法画图, 也不要只写 prompt 交差. 先告诉作者一句 "Claude Code 里不生图, 要生图请到 Antigravity 里跑 `blog-add-images`", 然后:

- 作者已经自己把图放进目录了: 照常做第 4, 5 步 (嵌入, 压缩).
- 没有图: 到此结束.

## 1. 定范围

输入: `$ARGUMENTS`. 用 `get` 找到这篇. 没给文档, 就用对话里刚写完的那篇, 不确定就问.

```bash
python3 .claude/skills/blog-base/scripts/blog_utils.py get --doc_id <doc_id>
```

没说配哪些, 用选择题问作者:

1. 只要封面 (推荐, kb 文档大多够了)
2. 封面 + 有独立论点的 H2
3. 只重画某几张

正文还没有 H2 (还没写), 只能配封面, 告诉作者. 纯操作步骤的 H2, 参考清单, 附录不配章节图.

## 2. 列视觉方案表 (只在 Antigravity)

通读 `README.md`, 按 `style-spec.md` 给每个要出图的位置列一行, 给作者看, 作者点头再生成:

| 文件 | 对应 | 这张图要讲的矛盾 | Mode | 底色 | 具体画什么 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `cover.jpeg` | 全篇 | ... | B | ... | ... |
| `img/01-section-<slug>.jpeg` | 第一张正文图 | ... | A | ... | ... |

- 封面讲全篇的总矛盾, 默认 Mode B.
- 相邻的图底色不同, 每张图的器物和构图都不一样.

## 3. 生成和检查 (只在 Antigravity)

1. 用 `style-spec.md` 第 5 节的英文模板写 prompt, 调用 `image-generator` subagent 生成 16:9 的图, 多张就并行.
2. 逐张看结果, 对照 `style-spec.md` 第 6 节: 没有乱码文字 (章节图一个字母都不能有), 留白够, 是手绘墨线的质感. 不合格就改 prompt 重生.
3. 合格的图放进文档目录: 封面是根下的 `cover.jpeg`; `img/` 下的图按正文出现顺序编号 (见 `08-images.md` 第 2 节). 重画就直接覆盖, 同时删掉旧图的 `.json` sidecar.

## 4. 嵌入 README.md

按 `08-images.md` 第 2 节: 封面放在开头段之后, 第一个 H2 之前; 章节图放在对应 H2 正下方, 和标题, 首段之间各空一行. alt 用中文写这张图讲什么. 已经嵌过的不要重复嵌. 只加图片那一行, 不动正文其他内容, 也不改 `updated_at`. 插图后序号乱了, 按 `08-images.md` 重排文件名和引用.

## 5. 压缩和检查

```bash
uvx imgsqueeze optimize <文档目录的绝对路径> --preset aggressive --json
python3 .claude/skills/blog-base/scripts/blog_utils.py check --path <文档目录>
```

读 JSON 里的 `summary`, 告诉作者压了几张, 一共省了多少 (`bytes_saved`). 有 `error` 的结果原样报给作者. 退出码 3 说明缺 PNG 工具, 把 stderr 里的安装说明转给作者. `check` 报 "image not found" 或 "not referenced" 就修掉.

## 6. 告诉作者

列出这次新增或替换的图, 每张一句话说画的是什么. 想在本地看效果: `mise run build-doc` 再 `mise run view-doc`.

## 边界

- 只写图片文件, 它们的 `.json` sidecar, 以及 `README.md` 里的图片行. 不改正文文字, 不改 front matter.

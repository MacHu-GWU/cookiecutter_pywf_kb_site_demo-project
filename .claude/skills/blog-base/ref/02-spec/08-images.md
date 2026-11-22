# Spec: 配图与压缩

> 管辖范围: 知识库文档什么时候配图, 图怎么命名, 放哪, 怎么嵌进正文, 什么画风, 怎么压缩.

---

## 1. 默认不配图

**kb 的文档大部分不配图.** 只有作者主动说要配图 (或者明确说 "给这篇画个封面"), 才进 `blog-add-images`. `blog-write` 写完正文不主动问要不要配图, 只在最后提一句 "需要配图可以用 `blog-add-images`".

能用文字, 表格, mermaid 说清楚的结构, 优先用它们 (见 [07-readme-body.md](07-readme-body.md) 第 6 节), 不需要图.

---

## 2. 三种图

| 图 | 文件 | 嵌在哪 |
| :--- | :--- | :--- |
| 封面 | 文档目录根下的 `cover.jpeg` | H1 下面的开头段之后, 第一个 H2 之前 (kb 页面没有 feature image, 封面就是正文第一张图) |
| 章节配图 | `img/NN-section-<slug>.jpeg` | 对应 H2 的正下方 |
| 信息图, 截图 | `img/NN-<name>.svg` / `.png` | 对应段落的下面 |

- `img/` 下的文件按**在正文里出现的先后顺序**加两位序号 `01-`, `02-`, 包括它们的 `.json` sidecar. 中间插图或删图后, 顺手重排序号和正文里的引用.
- 用相对路径引用: `![一句话说这张图讲什么](./img/01-section-<slug>.jpeg)`. alt 用中文.
- Sphinx 会把引用到的图片复制进构建结果. 没被引用的图片不进网站, 但还在 git 里, 不要留.

---

## 3. 画风

AI 生成的封面和章节图统一用 [`editorial-ink-art`](../../../editorial-ink-art/SKILL.md): 2D 手绘黑墨线, 莫兰迪纯色底, 少数关键图加一个 3D 磨砂发光焦点. 封面讲全篇的总矛盾, 默认 `Mode B`; 章节图严格零文字, 大约 70% `Mode A`, 30% `Mode B`. 一篇里每张图的器物和构图都不重复, 底色轮换.

信息图 (带精确数字, 结构拆解) 不用 AI 画, 写成 `.svg` 或 mermaid.

---

## 4. 只有 Antigravity 能生图

生图要用 Antigravity IDE 里的生图工具 (`image-generator` subagent). **Claude Code 里没有生图工具, 跳过生图这一步**, 不要试着用别的办法画, 也不要只写 prompt 交差. 作者想要图, 就到 Antigravity 里跑 `blog-add-images`.

不生图的那部分 (嵌入, 压缩) 两边都能做: 作者自己把图放进目录后, Claude Code 里也可以嵌进正文并压缩.

---

## 5. 压缩

任何时候新增或替换了 `.jpeg` / `.jpg` / `.png` / `.webp`, 收工前都用 [`pypi-imgsqueeze`](../../../pypi-imgsqueeze/SKILL.md) 原地压一次, 参数用绝对路径:

```bash
uvx imgsqueeze optimize <文档目录的绝对路径> --preset aggressive --json
uvx imgsqueeze check <文档目录的绝对路径>
```

- 每张图旁边会多一个 `<图片>.json` sidecar, 记录压缩后的 sha256, 以后不会二次压缩. sidecar 和图片一起提交, 不要手改, 不要删. 重画的图要删掉旧 sidecar.
- 压坏了: `git checkout` 恢复原图, 改用 `--preset light`, 或 `imgsqueeze pin <图片>`.
- `.svg` 不压缩.
- Cloudflare Pages 免费版一次部署最多 20,000 个文件, 图片也算. 一篇文档里图片别太多.
